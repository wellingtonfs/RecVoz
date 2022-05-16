import sys, pygame, os
from src.screen_init import ScreenInit
from src.screen_input import ScreenInput
from src.screen_config import ScreenConfig
from src.data import GetDataFromTXT
from regraGeral import RegraDados

#definição das variáveis
pygame.init()
pygame.font.init()

pathRoot = os.path.dirname(os.path.abspath(__file__))

size = width, height = 1280, 720

pygame.display.set_caption("Só falar")
pygame.display.set_icon(
    pygame.image.load(os.path.join(pathRoot, "rec", "icon.png"))
)
screen = pygame.display.set_mode(size)

dados = GetDataFromTXT(pathRoot, os.path.join(pathRoot, "config.txt"), RegraDados)

screenInit = ScreenInit(screen, dados)
screenInput = ScreenInput(screen, dados)
screenConfig = ScreenConfig(screen, dados)

#estado
estado = 0

def NovoEstado(estado, v):
    estado += v
    if estado < 0: return 2
    return estado if estado <= 2 else 0

#inicio do programa
while True:
    #detecção do teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    if estado == 0: #init
        estado = NovoEstado(estado, screenInit())
    elif estado == 1: #config
        estado = NovoEstado(estado, screenConfig())
    elif estado == 2: #input
        estado = NovoEstado(estado, screenInput())

    pygame.display.update()

#texts.updateNumber(microfone.getNumber(tempo=2))