import pygame
from src.data import GetDataFromTXT
import os, time

class TextOptions:
    def __init__(self, screen, fonte, data):
        self.screen = screen
        self.fonte = fonte
        self.x = lambda s : 640 - s // 2
        self.y = lambda i : 100 + i * 40
        self.data = data

    def plot(self):
        for i, v in enumerate(self.data.getOptions()):
            cor = (128, 128, 128)

            if i == self.data.ponteiro:
                cor = (250, 100, 100)

            size = self.fonte.size(v)[0]

            self.screen.blit(
                self.fonte.render(v, True, cor),
                (self.x(size), self.y(i))
            )

class ScreenInit:
    def __init__(self, screen, pathRoot):
        self.screen = screen
        self.fonteMenor = pygame.font.Font(os.path.join(pathRoot, "rec", "Florida Project Phase One.ttf"), 20)

        self.backgroundcolor = 255, 255, 255
        self.data = GetDataFromTXT(pathRoot, os.path.join(pathRoot, "config.txt"))
        self.texts = TextOptions(screen, self.fonteMenor, self.data)
        self.tempo = time.time()

    def getData(self):
        return self.data

    def __call__(self):
        #detecção do teclado
        key = pygame.key.get_pressed()

        if key[pygame.K_RETURN] or key[pygame.K_KP_ENTER]:
            return self.data
        elif key[pygame.K_UP] and time.time() - self.tempo > 0.2:
            self.data.back()
            self.tempo = time.time()
        elif key[pygame.K_DOWN] and time.time() - self.tempo > 0.2:
            self.data.next()
            self.tempo = time.time()

        #desenhar elementos na tela
        self.screen.fill(self.backgroundcolor)
        self.texts.plot()

        return None