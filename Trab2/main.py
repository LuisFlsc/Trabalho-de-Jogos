import pygame
from grid import Grid, Cell


pygame.init()
pygame.font.init()

WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

# caso precise de usar fontes na main, descomente

#font_size
#font = pygame.font.Font(None, font_size)

# caso precise carregar imagens na main, descomente

#idle = pygame.image.load("images/duck/duck.png").convert_alpha()
#step = pygame.image.load("images/duck/step.png").convert_alpha()
#etc


#numero de celulas
grid_size = (5, 10)


# Cria a janela
WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

#criar objetos, adicione eles a lista
objects = []

while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        # uso do mouse é obrigatório
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]: # 0 botão esquedo 2, direito
                pass # faça algo

        #caso queira usar levantar o mouse, descomente
        #elif event.type == pygame.MOUSEBUTTONUP:
        #                    exit()


        # uso do teclado para controle é obrigatório
        elif event.type == pygame.KEYDOWN:
            #inclua outras funcionalidades para outras téclas
            if event.key == pygame.K_ESCAPE:
                exit()

        #atualiza
        for obj in objects:
            obj.update(1)

        # Desenha
        screen.fill((30, 30, 30))


        for obj in objects:
            obj.draw()

        pygame.display.flip()