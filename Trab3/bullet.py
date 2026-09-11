import pygame
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler, distance


import math

def rotate(pos, angle, axis = (0,0)):
    angle = math.radians(angle)
    x, y = pos
    ax, ay = axis

    # Translate so axis is the origin
    x -= ax
    y -= ay

    # Rotate
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rx = x * cos_a - y * sin_a
    ry = x * sin_a + y * cos_a

    # Translate back
    return rx + ax, ry + ay

class Bullet (ABC):

    def __init__(self, pos, angle = 0, radius = 16, life_time = None):
        self.pos = pos
        self.origin = pygame.Vector2(pos)
        self.life_time = life_time
        self.angle = angle
        self.elapsed = 0
        self.radius = radius

        self.sprite = colored_sprite ((255, 0, 0), (self.radius*2, self.radius*2))

    def update(self, dt):

        self.elapsed += dt
        if self.life_time and self.elapsed >= self.life_time:
                self.destroy()       

        self.pos = rotate(self.move(), self.angle)+self.origin

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

    @abstractmethod
    def move(self):
        pass

    def destroy(self): # pede para deletar
        EventHandler().notify("DestroyObj", self) # avisa o mundo que saiu da tela

class sinBullet (Bullet):
    # exemplo, façam algo mais rebuscado

    def move(self):
        return pygame.Vector2(self.elapsed, math.sin(self.elapsed/50)*50) 


# ---------------------------------------------------------------------------
# Balas retas simples, usadas pelo jogador (auto-ataque/magia) e inimigos
# à distância (esqueleto). São mais leves que a Bullet abstrata acima,
# que foi pensada para trajetórias curvas de exemplo.
# ---------------------------------------------------------------------------

class SimpleBullet:
    def __init__(self, pos, angle_deg, speed=8, radius=5, life_time=90, color=(255, 255, 0)):
        self.pos = pygame.Vector2(pos)
        rad = math.radians(angle_deg)
        self.velocity = pygame.Vector2(math.cos(rad), math.sin(rad)) * speed
        self.radius = radius
        self.life_time = life_time
        self.elapsed = 0
        self.sprite = colored_sprite(color, (radius * 2, radius * 2))
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.elapsed += dt
        self.pos += self.velocity * dt
        if self.life_time is not None and self.elapsed >= self.life_time:
            self.destroy()
        elif self.life_time is None:
            screen = pygame.display.get_surface()
            if screen:
                width, height = screen.get_size()
                if (
                    self.pos.x < -self.radius
                    or self.pos.x > width + self.radius
                    or self.pos.y < -self.radius
                    or self.pos.y > height + self.radius
                ):
                    self.destroy()

    def draw(self, screen):
        if self.alive:
            screen.blit(self.sprite, self.pos - pygame.Vector2(self.radius, self.radius))

    def destroy(self):
        if self.alive:
            self.alive = False
            EventHandler().notify("DestroyObj", self)


class PlayerBullet(SimpleBullet):
    """Bala disparada pelo jogador (ataque automático ou magia)."""

    def __init__(self, pos, angle_deg, damage, magic=False, speed=9, pierce=0):
        color = (140, 100, 255) if magic else (255, 220, 80)
        super().__init__(pos, angle_deg, speed=speed, radius=4, life_time=70, color=color)
        self.damage = damage
        self.magic = magic
        self.pierce = pierce            # quantos inimigos além do primeiro pode atravessar
        self.hit_enemies = set()        # evita acertar o mesmo inimigo duas vezes


class EnemyBullet(SimpleBullet):
    """Bala disparada por inimigos à distância (esqueleto)."""

    def __init__(self, pos, angle_deg, damage, speed=5, radius=5, life_time=180):
        super().__init__(pos, angle_deg, speed=speed, radius=radius, life_time=life_time, color=(220, 60, 60))
        self.damage = damage


class SkeletonBullet(EnemyBullet):
    """Flecha vermelha disparada pelos esqueletos."""

    def __init__(self, pos, angle_deg, damage, speed=4):
        super().__init__(pos, angle_deg, damage, speed=speed, radius=7, life_time=180)
        self.sprite = colored_sprite((220, 60, 60), (18, 8), circle=False)

    def draw(self, screen):
        if self.alive:
            direction = self.velocity.normalize()
            perpendicular = pygame.Vector2(-direction.y, direction.x)
            tip = self.pos + direction * 11
            back = self.pos - direction * 8
            wing_left = back + perpendicular * 5
            wing_right = back - perpendicular * 5
            pygame.draw.line(screen, (220, 60, 60), back, tip, 3)
            pygame.draw.polygon(screen, (245, 90, 70), [tip, wing_left, wing_right])
            pygame.draw.line(screen, (125, 25, 25), wing_left, back - direction * 4, 2)
            pygame.draw.line(screen, (125, 25, 25), wing_right, back - direction * 4, 2)


class BossTrailProjectile(SimpleBullet):
    """Projétil laranja que deixa uma área perigosa por 5 segundos."""

    def __init__(self, pos, angle_deg, damage, player, speed=6, radius=10):
        super().__init__(pos, angle_deg, speed=speed, radius=radius, life_time=None, color=(255, 125, 20))
        self.damage = damage
        self.player = player
        self.projectile_elapsed = 0
        self.projectile_lifetime = 180
        self.trail_lifetime = 300
        self.trail_positions = []
        self.projectile_active = True

    def update(self, dt):
        if not self.alive:
            return

        if self.projectile_active:
            self.projectile_elapsed += dt
            self.pos += self.velocity * dt
            self.trail_positions.append([pygame.Vector2(self.pos), self.trail_lifetime])
            if distance(self.pos, self.player.pos) <= self.radius + 16:
                EventHandler().notify("DamagePlayer", {"amount": self.damage, "magic": False})
                self.projectile_active = False
            screen = pygame.display.get_surface()
            outside_screen = False
            if screen:
                width, height = screen.get_size()
                outside_screen = (
                    self.pos.x < -self.radius
                    or self.pos.x > width + self.radius
                    or self.pos.y < -self.radius
                    or self.pos.y > height + self.radius
                )
            if outside_screen:
                self.projectile_active = False

        for trail in self.trail_positions:
            trail[1] -= dt
        self.trail_positions = [trail for trail in self.trail_positions if trail[1] > 0]

        for trail_pos, _remaining in self.trail_positions:
            if distance(trail_pos, self.player.pos) <= self.radius + 14:
                EventHandler().notify("DamagePlayer", {"amount": self.damage, "magic": False})
                break

        if not self.projectile_active and not self.trail_positions:
            self.destroy()

    def draw(self, screen):
        if not self.alive:
            return
        for trail_pos, remaining in self.trail_positions:
            alpha = max(35, int(150 * remaining / self.trail_lifetime))
            trail_surface = pygame.Surface((self.radius * 2 + 8, self.radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                trail_surface,
                (255, 95, 15, alpha),
                (self.radius + 4, self.radius + 4),
                self.radius + 4,
            )
            screen.blit(trail_surface, trail_pos - pygame.Vector2(self.radius + 4, self.radius + 4))
        if self.projectile_active:
            screen.blit(self.sprite, self.pos - pygame.Vector2(self.radius, self.radius))
