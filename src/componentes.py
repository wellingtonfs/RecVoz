import time

def GetTextFromAudio(microfone, stop, buffer): 
    with microfone.source() as source:
        while not stop(): 
            microfone.gravar(source)

        t = time.time()
        while time.time() - t <= 1:
            microfone.gravar(source)

        buffer.append(microfone.getText(source))

class TextFala:
    def __init__(self, screen, fonte, position=False):
        self.screen = screen
        self.fonte = fonte
        self.x = 1260 if position else 20
        self.y = 20 if position else 680
        self.cor = (128, 128, 128)
        self.text = ""
        self.position = position

    def plot(self):
        if not self.text: return

        x = self.x
        if self.position: x -= self.fonte.size(self.text)[0]

        self.screen.blit(
            self.fonte.render(self.text, True, self.cor),
            (x, self.y)
        )


class TextInferior:
    def __init__(self, screen, fonte):
        self.screen = screen
        self.fonte = fonte
        self.x = lambda s : 640 - s // 2
        self.y = 350
        self.cor = (128, 128, 128)
        self.data = None

    def setData(self, data):
        self.data = data

    def plot(self):
        if self.data is None: return

        texto = str(self.data)

        size = self.fonte.size(texto)[0]

        self.screen.blit(
            self.fonte.render(texto, True, self.cor),
            (self.x(size), self.y)
        )

def dataJson():
    return {
        "Ponto": "",
        "Local": "",
        "Data": "00/00/00",
        "Espécie": "",
        "Sexo": "",
        "Maturidade": "",
        "Modelo (a ou b)": ""
    }