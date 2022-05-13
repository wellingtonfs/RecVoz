import pygame
import os, time
from src.micro import Microfone

class ScreenInit:
    def __init__(self, screen, dados):
        self.screen = screen

        with open(os.path.join(dados.pathRoot, "rec", "font.txt")) as f:
            nameFont = f.read().replace('\n', '')

        self.fonteMenor = pygame.font.SysFont(nameFont, 30)
        
        self.microOn = pygame.image.load(os.path.join(dados.pathRoot, "rec", "micro_on.png"))
        self.microOff = pygame.image.load(os.path.join(dados.pathRoot, "rec", "micro_off.png"))

        self.dados = dados
        self.options = []
        self.__novaEstruturaOpt()
        self.localPoint = 0

        self.microfone = Microfone()
        self.obterDados = False
        self.lock = 0

        self.x = lambda s : 640 - s // 2
        self.y = lambda i : 400 + i * 40

        self.backgroundcolor = 255, 255, 255
        self.tempo = time.time()

    def __novaEstruturaOpt(self):
        dados = self.dados.getModels()
    
        for i, name in enumerate(dados):
            for j, v in enumerate(dados[name]):
                self.options.append([name, v, i, j])

        pygame.display.set_caption(self.options[0][0])

    def __back(self):
        self.localPoint -= 1
        if self.localPoint < 0: self.localPoint = len(self.options) - 1
        pygame.display.set_caption(self.options[self.localPoint][0])

    def __next(self):
        self.localPoint = (self.localPoint + 1) % len(self.options)
        pygame.display.set_caption(self.options[self.localPoint][0])

    def plotTexts(self):
        for i, v in enumerate(self.options):
            cor = (128, 128, 128)

            if i == self.localPoint:
                cor = (250, 100, 100)

            text = '[%d] ' %i + v[0] + ': ' + str(v[1])

            size = self.fonteMenor.size(text)[0]

            self.screen.blit(
                self.fonteMenor.render(text, True, cor),
                (self.x(size), self.y(i))
            )

    def processarTexto(self):
        dados = self.microfone.getText()

        if not dados.ok:
            return False

        if dados.cmd and dados.cmd[0] == "ok":
            self.dados.posOptGeral = self.options[self.localPoint][2]
            self.dados.modeloAtual = self.options[self.localPoint][3]
            return True
        elif dados.number and 0 <= dados.getInt() < len(self.options):
            self.localPoint = dados.getInt()
            pygame.display.set_caption(self.options[self.localPoint][0])

    def __call__(self):
        self.screen.fill(self.backgroundcolor)

        #detecção do teclado
        key = pygame.key.get_pressed()

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

        if key[pygame.K_RETURN] or key[pygame.K_KP_ENTER]:
            self.obterDados = True
        else:
            self.obterDados = False

        if key[pygame.K_UP] and time.time() - self.tempo > 0.2:
            self.__back()
            self.tempo = time.time()
        elif key[pygame.K_DOWN] and time.time() - self.tempo > 0.2:
            self.__next()
            self.tempo = time.time()

        #desenhar elementos na tela
        self.plotTexts()

        self.screen.blit(self.microOn if self.obterDados else self.microOff, (515, 50))

        return 0