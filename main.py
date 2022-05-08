import sys, pygame, os
from src.screen_init import ScreenInit
from src.screen_input import ScreenInput
from src.screen_config import ScreenConfig

#definição das variáveis
pygame.init()
pygame.font.init()

pathRoot = os.path.dirname(os.path.abspath(__file__))

size = width, height = 1280, 720

pygame.display.set_caption("Só falar")
screen = pygame.display.set_mode(size)
screenInit = ScreenInit(screen, pathRoot)
screenInput = ScreenInput(screen, pathRoot)
screenConfig = ScreenConfig(screen, pathRoot)

estado = 0

#inicio do programa
while True:
    #detecção do teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    if estado == 0:
        if screenInit() is not None:
            screenConfig.setData(screenInit.getData())
            estado = 1
    elif estado == 1: #config
        if screenConfig() is not None:
            screenConfig.clear()
            screenInput.updateData(screenConfig.getData())
            estado = 2
    elif estado == 2: #input
        if screenInput() is not None:
            screenInput.clear()
            estado = 1

    pygame.display.update()

#texts.updateNumber(microfone.getNumber(tempo=2))