import pygame, os, time
from src.micro import Microfone
from src.componentes import TextFala
from playsound import playsound
from threading import Thread

def efeito(path):
    playsound(path)

class ScreenInput:
    def __init__(self, screen, dados):
        self.screen = screen

        with open(os.path.join(dados.pathRoot, "rec", "font.txt")) as f:
            nameFont = f.read().replace('\n', '')

        self.fonte = pygame.font.SysFont(nameFont, 35)
        self.fonteHist = pygame.font.SysFont(nameFont, 25)
        self.fonteMenor = pygame.font.SysFont(nameFont, 20)
        self.fonteH = self.fonte.size("data")[1]

        self.microOn = pygame.image.load(os.path.join(dados.pathRoot, "rec", "micro_on.png"))
        self.microOff = pygame.image.load(os.path.join(dados.pathRoot, "rec", "micro_off.png"))
        self.efeitoSonoro = os.path.join(dados.pathRoot, "rec", "efeito.mp3")

        self.textFala = TextFala(screen, self.fonteMenor, position=True)
        self.microfone = Microfone()
        self.dados = dados

        self.localPoint = 0
        self.options = []

        self.obterDados = False
        self.lock = 0
        self.salvando = None
        self.alterandoDados = False
        self.podeSalvar = True

        #infos superior
        self.y_micro = 235
        self.x = 100
        self.startY = 50
        self.step = 50

        #barras
        self.alturaBarra = 75
        self.qtdBarras = 5

        self.coresBarras = [(200, 200, 220), (235, 235, 255)]

    def plotTextSalvando(self):
        if self.salvando is None:
            return

        txt = "Alterando Dados..." if self.alterandoDados else "Dados Salvos"

        size = self.fonte.size(txt)[0]

        self.screen.blit(
            self.fonte.render(txt, True, (200, 0, 0)),
            (1260 - size, 20)
        )

        if time.time() - self.salvando > 2:
            self.salvando = None
            self.alterandoDados = False
        
    def plotOptions(self):
        y = self.startY
        for i, (name, value) in enumerate(self.options):
            cor = (128, 128, 128)

            if i == self.localPoint:
                cor = (200, 0, 0)

            self.screen.blit(
                self.fonte.render("%s: %s" %(name, value["valor"]), True, cor),
                (self.x, y)
            )

            y += self.step

    def plotBarras(self):
        ic = 1 if self.qtdBarras % 2 == 0 else 0

        y = 720 - self.alturaBarra

        listaDados = self.dados.getLastLines(self.qtdBarras)
        listaDados.reverse()

        for line in listaDados:
            pygame.draw.rect(
                self.screen, self.coresBarras[ic], pygame.Rect(0, y, 1280, self.alturaBarra)
            )

            line = line[:150] + '...' if len(line) > 150 else line

            st = self.fonteHist.size(line)
            xt = 640 - st[0] // 2
            yt = y + (self.alturaBarra // 2 - st[1] // 2)

            self.screen.blit(
                self.fonteHist.render(line, True, (128, 128, 128)),
                (xt, yt)
            )

            ic = (ic + 1) % 2
            y -= self.alturaBarra

    def updateOptions(self):
        if not self.options:
            self.options = self.dados.getDinamicVars()

            pygame.display.set_caption(
                ', '.join([ v[1]["valor"] for v in self.dados.getStaticVars() ])
            )

            htFont = (self.step * len(self.options) - (self.step - self.fonteH))
            tam_sup = max(htFont, 250) + 80

            self.qtdBarras = (720 - tam_sup) // self.alturaBarra
            hs_livre = (720 - (self.qtdBarras * self.alturaBarra)) // 2

            self.y_micro = hs_livre - 250 // 2
            self.startY = hs_livre - htFont // 2

    def __getCurrentOpt(self):
        return self.options[self.localPoint]

    #erro aconteceu e deve ser reparado (caso o voltar baixe de 0)
    def __back(self):
        self.localPoint -= 1

        if self.localPoint < 0:
            self.dados.dropLast()
            self.localPoint = len(self.options) - 1
            self.salvando = time.time()
            self.alterandoDados = True
            self.podeSalvar = True

    def __next(self):
        self.localPoint = (self.localPoint + 1) % len(self.options)

        if self.podeSalvar and self.localPoint == 0:
            self.salvando = time.time()
            self.alterandoDados = False

            tr = Thread(target=efeito, args=(self.efeitoSonoro, ))
            tr.daemon = True
            tr.start()

            self.dados.save()
        elif not self.podeSalvar:
            self.podeSalvar = True

    def __go(self, key):
        for i, v in enumerate(self.options):
            if key.lower() in v[0].lower():
                self.localPoint = i
                return

    def processarTexto(self):
        dados = self.microfone.getText()
        self.textFala.text = dados.text

        if not dados.ok:
            return 0

        if dados.cmd:
            if dados.cmd[0] == "back":
                self.__back()
            elif dados.cmd[0] == "next":
                self.podeSalvar = False
                self.__next()
            elif dados.cmd[0] == "ok":
                self.__next()
            elif dados.cmd[0] == "change":
                if "modelo" in dados.cmd[1]:
                    self.options = []
                    self.localPoint = 0
                    return -2
                elif any([v in dados.cmd[1] for v in dados.config]) or "dados" in dados.cmd[1]:
                    self.options = []
                    self.localPoint = 0
                    return -1
            #elif dados.cmd[0] == "change":
            #    self.__go(dados.cmd[-1])
            elif dados.cmd[0] == "config":
                self.options = []
                self.localPoint = 0
                return -1
        elif self.__getCurrentOpt()[1]["tipo"] == "date":
            dataForm = dados.convertDate(dados.text)

            if dataForm:
                self.dados.updateVar(self.__getCurrentOpt()[0], dataForm)
                self.__next()
        elif self.__getCurrentOpt()[1]["tipo"] == "float":
            if dados.number:
                self.dados.updateVar(self.__getCurrentOpt()[0], dados.number)
                self.__next()
        else:
            self.dados.updateVar(self.__getCurrentOpt()[0], dados.text)
            self.__next()

        return 0

    def __call__(self):
        self.screen.fill((255, 255, 255))

        self.updateOptions()

        #detecção de voz
        if self.obterDados:
            if self.lock == 1:
                self.microfone.start()
                self.lock = 2
        else:
            if self.lock == 2:
                self.microfone.stop()
                devoSair = self.processarTexto()

                if devoSair:
                    self.lock = 0
                    return devoSair

                self.lock = 1

            if self.lock == 0:
                self.lock = 1

        #detecção do teclado
        key = pygame.key.get_pressed()

        if key[pygame.K_RETURN] or key[pygame.K_KP_ENTER]:
            self.obterDados = True
        else:
            self.obterDados = False

        if key[pygame.K_SPACE]:
            return True

        #self.screen.blit(self.modelos, (140, 430))

        self.screen.blit(self.microOn if self.obterDados else self.microOff, (820, self.y_micro)) #y=235 para ficar no meio
        self.textFala.plot()
        self.plotOptions()
        self.plotTextSalvando()
        self.plotBarras()

        return 0