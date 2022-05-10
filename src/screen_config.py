import pygame, threading
from src.micro import Microfone
from src.componentes import TextFala, GetTextFromAudio
import src.lexico as lx
import os

class Texts:
    def __init__(self, screen, fonte):
        self.screen = screen
        self.fonte = fonte
        self.size = screen.get_size()
        self.ponteiro = 0
        self.dataObj = None
        self.data = None
        self.meses = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
            "outubro", "novembro", "dezembro"
        ]

    def plot(self):
        x = 100
        startY = 75
        step = 50

        for i, v in enumerate(self.data):
            cor = (128, 128, 128)

            if i == self.ponteiro:
                cor = (200, 0, 0)

            self.screen.blit(
                self.fonte.render("%s: %s" %(v[0], v[1]["valor"]), True, cor),
                (x, startY)
            )

            startY += step

    def setData(self, data):
        self.dataObj = data
        self.data = data.getInfo()

    def back(self):
        self.ponteiro -= 1
        if self.ponteiro < 0:
            self.ponteiro = len(self.data) - 1

    def next(self):
        self.ponteiro = (self.ponteiro + 1) % len(self.data)

    def go(self, key):
        for i, v in enumerate(self.data):
            if key.lower() in v[0].lower():
                self.ponteiro = i
                return

    def saveData(self, data, move=True):
        key = self.data[self.ponteiro][0]
        self.dataObj.updateVar(key, data)
        self.data = self.dataObj.getInfo()
        if move:
            self.ponteiro = (self.ponteiro + 1) % len(self.data)

    def update(self, txt):
        dados = self.data[self.ponteiro][1]

        if dados["tipo"] == "date":
            txt = txt.lower().split()
            txt = [
                self.meses.index(t) + 1 if t in self.meses else t for t in txt
            ]

            nums = []

            for t in txt:
                if lx.isNumber(t):
                    tn = str(int(t))
                    nums.append(tn if len(tn) > 1 else '0' + tn)

            if len(nums) == 3:
                self.saveData('/'.join(nums))
            else:
                self.saveData("erro: não entendi", move=False)

        elif dados["tipo"] == "mod":
            txt = txt.lower().split()[-1].strip()
            txt = txt if len(txt) == 1 else txt[0]

            if txt in self.dataObj.getModelKeys():
                self.saveData(txt, move=False)
                self.dataObj.setModel(txt)
        else:
            self.saveData(txt)

class TextsModels:
    def __init__(self, screen, fonte):
        self.screen = screen
        self.fonte = fonte
        self.data = None
        self.models = None
        self.cor = (128, 128, 128)
        self.corDest = (0, 0, 0)

    def setData(self, data):
        self.data = data
        models = self.data.getModels()
        self.models = [('[%s]'%k, ', '.join(models[k])) for k in models]

    def plot(self):
        if self.models is None: return

        size = self.fonte.size("Modelos")[0]
        self.screen.blit(self.fonte.render("Modelos", True, self.corDest), (640 - size // 2, 425))

        y = 480

        for linha in self.models:
            size = self.fonte.size(linha[0])[0]
            self.screen.blit(self.fonte.render(linha[0], True, self.corDest), (100, y))

            self.screen.blit(self.fonte.render(linha[1], True, self.cor),(100 + size + 15, y))

            y += 40

class ScreenConfig:
    def __init__(self, screen, pathRoot):
        self.screen = screen

        with open(os.path.join(pathRoot, "rec", "font.txt")) as f:
            nameFont = f.read().replace('\n', '')

        self.fonte = pygame.font.SysFont(nameFont, 35)
        self.fonteMenor = pygame.font.SysFont(nameFont, 20)

        #self.fonte = pygame.font.Font(os.path.join(pathRoot, "rec", "Florida Project Phase One.ttf"), 35)
        #self.fonteMenor = pygame.font.Font(os.path.join(pathRoot, "rec", "Florida Project Phase One.ttf"), 20)
        self.microOn = pygame.image.load(os.path.join(pathRoot, "rec", "micro_on.png"))
        self.microOff = pygame.image.load(os.path.join(pathRoot, "rec", "micro_off.png"))
        self.modelos = pygame.image.load(os.path.join(pathRoot, "rec", "modelos.png"))

        self.backgroundcolor = 255, 255, 255

        self.texts = Texts(screen, self.fonte)
        self.textFala = TextFala(screen, self.fonteMenor)
        self.textsModels = TextsModels(screen, self.fonte)
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

    def setData(self, data):
        self.texts.setData(data)
        self.textsModels.setData(data)
        self.data = data
    
    def getData(self):
        return self.data

    def getOut(self):
        if self.tr is not None:
            self.stop_thread = True
            self.tr.join()
            self.stop_thread = False
            self.tr = None
        return True

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
            tn = lx.Analise(self.buffer[-1], getText=True)

            self.textOriginal = "Não entendi" if tn.original is None else tn.original

            if tn.ok:
                if tn.isNumber:
                    pass
                elif tn.value == "back":
                    self.texts.back()
                elif tn.value == "next":
                    self.texts.next()
                elif tn.value == "ok":
                    return self.getOut()
                elif tn.value == "change":
                    self.texts.go(tn.args[0])
                elif tn.value is not None:
                    self.texts.update(tn.value)

            self.buffer.pop()

        #detecção do teclado
        key = pygame.key.get_pressed()

        if key[pygame.K_RETURN] or key[pygame.K_KP_ENTER]:
            self.obterDados = True if not self.lock else self.obterDados
        else:
            self.lock = False
            self.obterDados = False

        if key[pygame.K_SPACE]:
            return self.getOut()

        #desenhar elementos na tela
        self.screen.fill(self.backgroundcolor)
        self.texts.plot()
        self.textFala.plot(self.textOriginal)
        self.textsModels.plot()

        #self.screen.blit(self.modelos, (140, 430))

        self.screen.blit(self.microOn if self.obterDados else self.microOff, (820, 50))
        return None