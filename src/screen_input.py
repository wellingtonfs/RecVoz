import pygame, threading
from src.micro import Microfone
from src.componentes import TextFala, TextInferior, GetTextFromAudio
import src.lexico as lx
import os, copy

class Texts:
    def __init__(self, screen, fonte, cbEnd) -> None:
        self.data = None

        self.screen = screen
        self.fonte = fonte
        self.ponteiro = 0
        self.keys = []
        self.nT = False
        self.cbEnd = cbEnd

    def setData(self, data):
        self.data = data
        self.keys = list(map(lambda x: x[0], self.data.getVars()))
        self.nT = True if self.data.getVarType(self.keys[self.ponteiro]) != 'float' else False

    def needsText(self):
        return self.nT

    def plot(self):
        if self.data is None: return

        x = 100
        startY = 75
        step = 50

        for i, v in enumerate(self.data.getVars()):
            cor = (128, 128, 128)

            if i == self.ponteiro:
                cor = (200, 0, 0)

            self.screen.blit(
                self.fonte.render("%s: %s" %(v[0], v[1]['valor']), True, cor),
                (x, startY))

            startY += step

    def back(self):
        self.ponteiro -= 1

        if self.ponteiro < 0:
            self.ponteiro = len(self.keys) - 1

    def next(self):
        sizeKeys = len(self.keys)
        self.ponteiro = (self.ponteiro + 1) % sizeKeys

        if sizeKeys > 0 and self.ponteiro == 0:
            self.cbEnd()

    def updateNumber(self, number):
        self.data.updateVar(self.keys[self.ponteiro], number)
        self.next()
        self.nT = True if self.data.getVarType(self.keys[self.ponteiro]) != 'float' else False

class Molduras:
    def __init__(self, screen, fonte):
        self.screen = screen
        self.fonte = fonte
        self.buffer = []

        self.x, self.y = 5, 400
        self.marginTop = 30 #texto
        self.cor = (128, 128, 128)
        self.corDest = (200, 100, 100)

    def plot(self):
        y = self.y

        for data in self.buffer[-10:]:
            x = self.x

            texto = "|"
            for key, value in data:
                texto +=  " %s: " %key
                self.screen.blit(self.fonte.render(texto, True, self.cor), (x, y))
                x += self.fonte.size(texto)[0] + 5

                texto =  "%s" %value['valor']
                self.screen.blit(self.fonte.render(texto, True, self.corDest), (x, y))
                x += self.fonte.size(texto)[0] + 5

                texto =  " |"
                self.screen.blit(self.fonte.render(texto, True, self.cor), (x, y))
                x += self.fonte.size(texto)[0] + 5

                texto = ""

            y += self.marginTop

    def addData(self, data):
        self.buffer.append(copy.deepcopy(data.getVars()))

class ScreenInput:
    def __init__(self, screen, pathRoot):
        self.screen = screen
        self.fonte = pygame.font.Font(os.path.join(pathRoot, "rec", "Florida Project Phase One.ttf"), 35)
        self.fonteMenor = pygame.font.Font(os.path.join(pathRoot, "rec", "Florida Project Phase One.ttf"), 20)
        self.microOn = pygame.image.load(os.path.join(pathRoot, "rec", "micro_on.png"))
        self.microOff = pygame.image.load(os.path.join(pathRoot, "rec", "micro_off.png"))

        self.backgroundcolor = 255, 255, 255

        self.texts = Texts(screen, self.fonte, self.eventSave)
        self.textFala = TextFala(screen, self.fonteMenor)
        self.textInf = TextInferior(screen, self.fonteMenor)
        self.moldura = Molduras(screen, self.fonteMenor)
        self.microfone = Microfone()
        self.data = None

        self.tr = None
        self.buffer = []
        self.obterDados = False
        self.stop_thread = False
        self.textOriginal = ""
        self.lock = True

    def clear(self):
        self.buffer = []
        self.textOriginal = ""
        self.lock = True

    def eventSave(self):
        self.data.saveData()
        self.moldura.addData(self.data)

    def updateData(self, data):
        self.data = data
        self.texts.setData(data)
        self.textInf.setData(data)

    def __call__(self):
        #detecção de voz
        if self.obterDados and self.tr is None:
            self.tr = threading.Thread(target = GetTextFromAudio, args =(self.microfone, lambda : self.stop_thread, self.buffer, ))
            self.tr.daemon = True
            self.tr.start()
        elif not self.obterDados and self.tr is not None:
            self.stop_thread = True
            self.tr.join()
            self.stop_thread = False
            self.tr = None

        #comandos de voz
        while len(self.buffer) > 0:
            tn = lx.Analise(self.buffer[-1], getText=self.texts.needsText())
            self.textOriginal = "Não entendi" if tn.original is None else tn.original

            if tn.ok:
                if tn.isNumber:
                    self.texts.updateNumber(tn.value)
                elif tn.value == "back":
                    self.texts.back()
                elif tn.value == "config":
                    if self.tr is not None:
                        self.stop_thread = True
                        self.tr.join()
                        self.stop_thread = False
                        self.tr = None
                    return True
                else:
                    self.texts.updateNumber(tn.value)

            self.buffer.pop()

        #detecção do teclado
        key = pygame.key.get_pressed()

        if key[pygame.K_RETURN] or key[pygame.K_KP_ENTER]:
            self.obterDados = True if not self.lock else self.obterDados
        else:
            self.lock = False
            self.obterDados = False

        #desenhar elementos na tela
        self.screen.fill(self.backgroundcolor)
        self.texts.plot()
        self.textFala.plot(self.textOriginal)
        self.moldura.plot()
        self.textInf.plot()

        self.screen.blit(self.microOn if self.obterDados else self.microOff, (820, 50))
        return None