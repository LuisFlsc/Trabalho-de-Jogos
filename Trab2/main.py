import pygame
from game import ChessGame

pygame.init()
pygame.font.init()

WIDTH = 800; HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xadrez em Pygame")

game = ChessGame(WIDTH, HEIGHT)
clock = pygame.time.Clock()

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            exit()
        else:
            game.handle_event(event)

    game.update(dt)
    game.draw(screen)
    pygame.display.flip()
