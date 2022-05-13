import pygame, os
from src.micro import Microfone
from src.componentes import TextFala

class ScreenConfig:
    def __init__(self, screen, dados):
        self.screen = screen

        with open(os.path.join(dados.pathRoot, "rec", "font.txt")) as f:
            nameFont = f.read().replace('\n', '')

        self.fonte = pygame.font.SysFont(nameFont, 35)
        self.fonteMenor = pygame.font.SysFont(nameFont, 20)

        self.microOn = pygame.image.load(os.path.join(dados.pathRoot, "rec", "micro_on.png"))
        self.microOff = pygame.image.load(os.path.join(dados.pathRoot, "rec", "micro_off.png"))

        self.textFala = TextFala(screen, self.fonteMenor)
        self.microfone = Microfone()
        self.dados = dados

        self.localPoint = 0
        self.options = []

        self.obterDados = False
        self.lock = 0

        self.x = 100
        self.startY = 75
        self.step = 50

    def updateOptions(self):
        if not self.options:
            self.options = self.dados.getStaticVars()
            fonteH = self.fonte.size("data")[1]

            self.startY = 360 - (self.step * len(self.options) - (self.step - fonteH)) // 2
        
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

    def __getCurrentOpt(self):
        return self.options[self.localPoint]

    def __back(self):
        self.localPoint -= 1
        if self.localPoint < 0: self.localPoint = len(self.options) - 1

    def __next(self):
        self.localPoint = (self.localPoint + 1) % len(self.options)

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
                self.__next()
            elif dados.cmd[0] == "change" and "modelo" in dados.cmd[1]:
                self.options = []
                self.localPoint = 0
                return -1
            elif dados.cmd[0] == "change":
                self.__go(dados.cmd[1])
            elif dados.cmd[0] == "ok":
                self.options = []
                self.localPoint = 0
                return 1
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

        self.screen.blit(self.microOn if self.obterDados else self.microOff, (820, 235))
        self.textFala.plot()
        self.plotOptions()

        return 0