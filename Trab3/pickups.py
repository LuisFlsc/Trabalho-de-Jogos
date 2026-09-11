import pygame
from util import colored_sprite, EventHandler, distance


class Pickup:
    """Item que fica no chão, é atraído pelo jogador dentro de um raio e some ao ser coletado."""

    def __init__(self, pos, player, value, color, radius=6, magnet_radius=90, speed=6):
        self.pos = pygame.Vector2(pos)
        self.player = player
        self.value = value
        self.radius = radius
        self.magnet_radius = magnet_radius
        self.speed = speed
        self.sprite = colored_sprite(color, (radius * 2, radius * 2))
        self.collected = False

    def update(self, dt):
        if self.collected:
            return
        player_pos = self.player.pos
        d = distance(self.pos, player_pos)
        if d < self.magnet_radius:
            direction = pygame.Vector2(player_pos) - self.pos
            if direction.length() > 0:
                direction = direction.normalize()
            self.pos += direction * self.speed * dt
        if d < 14:
            self.on_collect()

    def on_collect(self):
        self.collected = True
        EventHandler().notify("DestroyObj", self)

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.sprite, self.pos - pygame.Vector2(self.radius, self.radius))


class XPOrb(Pickup):
    def __init__(self, pos, player, value=1):
        super().__init__(pos, player, value, color=(80, 220, 255), radius=5)

    def on_collect(self):
        EventHandler().notify("AddXP", self.value)
        super().on_collect()


class Coin(Pickup):
    def __init__(self, pos, player, value=1):
        super().__init__(pos, player, value, color=(255, 215, 0), radius=6, magnet_radius=70)

    def on_collect(self):
        EventHandler().notify("AddCoin", self.value)
        super().on_collect()
