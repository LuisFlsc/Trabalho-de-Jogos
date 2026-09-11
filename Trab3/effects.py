import pygame
import math
from util import EventHandler, distance
from enemy import Enemy


class DashEffect:
    """Rastro visual curto deixado pelo jogador ao executar o dash."""

    def __init__(self, start, end, life_time=12, color=(255, 80, 190)):
        self.start = pygame.Vector2(start)
        self.end = pygame.Vector2(end)
        self.life_time = life_time
        self.elapsed = 0
        self.color = color
        self.alive = True

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.life_time:
            self.alive = False
            EventHandler().notify("DestroyObj", self)

    def draw(self, screen):
        alpha = max(0, int(150 * (1 - self.elapsed / self.life_time)))
        surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.line(surface, (*self.color, alpha), self.start, self.end, 12)
        pygame.draw.circle(surface, (*self.color, alpha), self.start, 18)
        pygame.draw.circle(surface, (255, 220, 245, alpha), self.end, 12, 3)
        screen.blit(surface, (0, 0))


class ChainLightningEffect:
    """Efeito visual: raios ligando o jogador aos alvos atingidos pelo raio em cadeia."""

    def __init__(self, origin, target_positions, life_time=15, color=(120, 200, 255)):
        self.origin = origin
        self.targets = target_positions
        self.life_time = life_time
        self.elapsed = 0
        self.color = color
        self.alive = True

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.life_time:
            self.alive = False
            EventHandler().notify("DestroyObj", self)

    def draw(self, screen):
        previous = self.origin
        for target in self.targets:
            pygame.draw.line(screen, self.color, previous, target, 2)
            previous = target


class CrescentEffect:
    """Projétil de meia-lua que viaja, cresce e desaparece."""

    def __init__(self, origin, direction, max_range, half_angle_deg, life_time=36, speed=8,
                 color=(160, 220, 255), objects_ref=None):
        self.pos = pygame.Vector2(origin)
        self.direction = pygame.Vector2(direction).normalize()
        self.max_range = max_range
        self.half_angle_deg = half_angle_deg
        self.life_time = life_time
        self.speed = speed
        self.elapsed = 0
        self.color = color
        self.objects_ref = objects_ref if objects_ref is not None else []
        self.alive = True
        self.hit_enemies = set()

    def update(self, dt):
        self.elapsed += dt
        self.pos += self.direction * self.speed * dt
        progress = min(1.0, self.elapsed / self.life_time)
        self.radius = max(12, self.max_range * progress)

        for enemy in self._enemies_in_arc():
            if id(enemy) in self.hit_enemies:
                continue
            to_enemy = enemy.pos - self.pos
            enemy.knockback(to_enemy, 40)
            enemy.apply_slow(120, mult=0.4)
            self.hit_enemies.add(id(enemy))

        if self.elapsed >= self.life_time:
            self.alive = False
            EventHandler().notify("DestroyObj", self)

    def _enemies_in_arc(self):
        enemies = []
        for obj in list(self._objects):
            if not isinstance(obj, Enemy) or not obj.alive:
                continue
            to_enemy = obj.pos - self.pos
            if to_enemy.length() > self.radius + obj.radius:
                continue
            if to_enemy.length() == 0:
                enemies.append(obj)
                continue
            if abs(self.direction.angle_to(to_enemy)) <= self.half_angle_deg:
                enemies.append(obj)
        return enemies

    def draw(self, screen):
        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        rect.center = (int(self.pos.x), int(self.pos.y))
        angle = math.atan2(self.direction.y, self.direction.x)
        start = angle - math.radians(self.half_angle_deg)
        end = angle + math.radians(self.half_angle_deg)
        pygame.draw.arc(surf, (*self.color, 190), rect, start, end, max(3, int(self.radius * 0.16)))
        pygame.draw.arc(surf, (225, 250, 255, 110), rect.inflate(-8, -8), start, end, 3)
        screen.blit(surf, (0, 0))

    @property
    def _objects(self):
        return self.objects_ref


class ConeEffect(CrescentEffect):
    """Compatibilidade para chamadas antigas do efeito de cone."""

    def __init__(self, origin, direction, range_px, half_angle_deg, life_time=12,
                 color=(160, 220, 255)):
        super().__init__(origin, direction, range_px, half_angle_deg, life_time, speed=0, color=color)


class ForceField:
    """Aura ao redor do jogador que causa dano pequeno e contínuo por tempo limitado."""

    def __init__(self, player, radius=100, damage=4, tick_interval=20, duration=1800):
        self.player = player
        self.radius = radius
        self.damage = damage
        self.tick_interval = tick_interval
        self.tick_timer = 0
        self.duration = duration
        self.elapsed = 0
        self.alive = True

    @property
    def pos(self):
        return self.player.pos

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.alive = False
            EventHandler().notify("DestroyObj", self)
            return

        self.tick_timer -= dt
        if self.tick_timer <= 0:
            self.tick_timer = self.tick_interval
            for obj in list(self.player.objects_ref):
                if isinstance(obj, Enemy) and obj.alive:
                    if distance(obj.pos, self.player.pos) <= self.radius:
                        obj.take_damage(self.damage)

    def draw(self, screen):
        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        center = (int(self.pos.x), int(self.pos.y))
        pygame.draw.circle(surf, (120, 180, 255, 60), center, self.radius)
        pygame.draw.circle(surf, (150, 200, 255, 160), center, self.radius, 2)
        screen.blit(surf, (0, 0))
