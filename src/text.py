from turtle import back


class Texts:
    def __init__(self, screen, fonte) -> None:
        self.data = [
            ["LT", None],
            ["Largura", None],
            ["Altura", None],
            ["Peso", None]
        ]

        self.screen = screen
        self.fonte = fonte
        self.size = screen.get_size()
        self.ponteiro = 0

    def plot(self):
        x = 100
        startY = 100
        step = 50

        for i, v in enumerate(self.data):
            cor = (0, 0, 0)

            if i == self.ponteiro:
                cor = (200, 0, 0)

            if v[1] is None:
                self.screen.blit(
                    self.fonte.render("%s:" %(v[0]), True, cor)
                , (x, startY))
            else:
                self.screen.blit(
                    self.fonte.render("%s: %.2f" %(v[0], v[1]), True, cor)
                , (x, startY))

            startY += step

    def back(self):
        self.ponteiro -= 1

        if self.ponteiro < 0:
            self.ponteiro = len(self.data) - 1

    def updateNumber(self, number):
        self.data[self.ponteiro][1] = number
        self.ponteiro = (self.ponteiro + 1) % len(self.data)