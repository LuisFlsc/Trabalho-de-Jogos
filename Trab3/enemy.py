import pygame
import math
import random
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler, distance
from bullet import EnemyBullet, SkeletonBullet, BossTrailProjectile
from pickups import XPOrb, Coin


class Enemy(ABC):
    """Classe base para todo inimigo. Subclasses definem stats e comportamento."""

    # --- valores padrão, sobrescritos pelas subclasses ---
    base_hp = 10
    base_damage = 5
    speed = 1.0
    color = (200, 50, 50)
    radius = 14
    xp_value = 2
    coin_chance = 0.12
    weight = 1.0  # "peso" conceitual no orçamento de inimigos de uma onda (ver WaveManager)

    def __init__(self, pos, player, hp_mult=1.0, dmg_mult=1.0):
        self.pos = pygame.Vector2(pos)
        self.player = player
        self.max_hp = self.base_hp * hp_mult
        self.hp = self.max_hp
        self.damage = self.base_damage * dmg_mult
        self.sprite = colored_sprite(self.color, (self.radius * 2, self.radius * 2))
        self.alive = True
        self.attack_cooldown = 0

        # controle de efeitos de status (usados pelas magias do jogador)
        self.stun_timer = 0
        self.slow_timer = 0
        self.speed_mult = 1.0

    def take_damage(self, amount):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.die()

    def die(self):
        self.alive = False
        EventHandler().notify("SpawnObject", XPOrb(self.pos, self.player, self.xp_value))
        if random.random() < self.coin_chance:
            EventHandler().notify("SpawnObject", Coin(self.pos, self.player, random.randint(1, 3)))
        EventHandler().notify("EnemyDied", self)
        EventHandler().notify("DestroyObj", self)

    def update(self, dt):
        if not self.alive:
            return

        if self.stun_timer > 0:
            self.stun_timer -= dt
            return  # paralisado: não se move nem ataca

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.speed_mult = 1.0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        self.behavior(dt)

    @abstractmethod
    def behavior(self, dt):
        pass

    @property
    def effective_speed(self):
        return self.speed * self.speed_mult

    def move_towards_player(self, dt):
        direction = pygame.Vector2(self.player.pos) - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.effective_speed * dt

    def stun(self, duration):
        """Paralisa o inimigo por `duration` frames (raio em cadeia)."""
        self.stun_timer = max(self.stun_timer, duration)

    def apply_slow(self, duration, mult=0.4):
        """Reduz a velocidade do inimigo por `duration` frames (nevasca)."""
        self.slow_timer = max(self.slow_timer, duration)
        self.speed_mult = min(self.speed_mult, mult)

    def knockback(self, direction, distance_px):
        """Empurra o inimigo instantaneamente na direção informada (nevasca)."""
        if direction.length() > 0:
            self.pos += direction.normalize() * distance_px

    def draw(self, screen):
        if not self.alive:
            return
        self.draw_body(screen)
        if self.hp < self.max_hp:
            w = self.radius * 2
            x, y = self.pos.x - self.radius, self.pos.y - self.radius - 6
            pygame.draw.rect(screen, (60, 0, 0), (x, y, w, 4))
            pygame.draw.rect(screen, (0, 200, 0), (x, y, w * max(0.0, self.hp / self.max_hp), 4))

    def draw_body(self, screen):
        screen.blit(self.sprite, self.pos - pygame.Vector2(self.radius, self.radius))


class Slime(Enemy):
    """Fraquinho: 1 de vida. Em grupos de 10, conta como 1 inimigo no orçamento da onda."""
    base_hp = 1
    base_damage = 5
    speed = 1.6
    color = (80, 200, 80)
    radius = 8
    xp_value = 1
    coin_chance = 0.04
    weight = 0.1

    def draw_body(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.ellipse(screen, (40, 125, 55), (x - 10, y - 5, 20, 14))
        pygame.draw.polygon(screen, self.color, [(x - 9, y + 3), (x - 7, y - 8),
                          (x, y - 13), (x + 8, y - 8), (x + 10, y + 3)])
        pygame.draw.circle(screen, (235, 255, 210), (x - 3, y - 5), 2)
        pygame.draw.circle(screen, (235, 255, 210), (x + 4, y - 5), 2)
        pygame.draw.circle(screen, (20, 60, 25), (x - 3, y - 5), 1)
        pygame.draw.circle(screen, (20, 60, 25), (x + 4, y - 5), 1)

    def behavior(self, dt):
        self.move_towards_player(dt)
        if distance(self.pos, self.player.pos) < self.radius + 16 and self.attack_cooldown <= 0:
            EventHandler().notify("DamagePlayer", {"amount": self.damage, "magic": False})
            self.attack_cooldown = 40


class Zombie(Enemy):
    """Corpo a corpo, velocidade média, resistência alta."""
    base_hp = 30
    base_damage = 8
    speed = 1.0
    color = (35, 80, 40)   # verde bem escuro
    radius = 16
    xp_value = 4
    coin_chance = 0.2

    def draw_body(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.ellipse(screen, (20, 45, 25), (x - 13, y + 1, 26, 22))
        pygame.draw.rect(screen, self.color, (x - 10, y - 5, 20, 24), border_radius=5)
        pygame.draw.circle(screen, (75, 105, 65), (x, y - 12), 10)
        pygame.draw.line(screen, (190, 205, 150), (x - 5, y - 14), (x - 2, y - 9), 2)
        pygame.draw.line(screen, (190, 205, 150), (x + 3, y - 9), (x + 7, y - 14), 2)
        pygame.draw.circle(screen, (235, 55, 40), (x - 4, y - 13), 2)
        pygame.draw.circle(screen, (235, 55, 40), (x + 4, y - 13), 2)
        pygame.draw.line(screen, (15, 35, 20), (x - 7, y + 5), (x + 7, y + 5), 2)
    weight = 1.0

    def behavior(self, dt):
        self.move_towards_player(dt)
        if distance(self.pos, self.player.pos) < self.radius + 18 and self.attack_cooldown <= 0:
            EventHandler().notify("DamagePlayer", {"amount": self.damage, "magic": False})
            self.attack_cooldown = 50


class Skeleton(Enemy):
    """Ataca à distância, velocidade média, resistência um pouco menor que o zumbi."""
    base_hp = 18
    base_damage = 6
    speed = 1.1
    color = (210, 210, 180)
    radius = 14
    xp_value = 5
    coin_chance = 0.2
    weight = 1.0
    attack_range = 260

    def draw_body(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        bone = (225, 225, 195)
        shadow = (105, 105, 95)
        pygame.draw.line(screen, shadow, (x, y - 1), (x, y + 17), 4)
        pygame.draw.line(screen, bone, (x, y - 1), (x, y + 17), 3)
        pygame.draw.line(screen, bone, (x - 11, y + 4), (x + 11, y + 4), 3)
        pygame.draw.line(screen, bone, (x - 7, y + 17), (x - 11, y + 24), 3)
        pygame.draw.line(screen, bone, (x + 7, y + 17), (x + 11, y + 24), 3)
        pygame.draw.circle(screen, bone, (x, y - 11), 11)
        pygame.draw.circle(screen, (35, 35, 32), (x - 4, y - 13), 3)
        pygame.draw.circle(screen, (35, 35, 32), (x + 4, y - 13), 3)
        pygame.draw.polygon(screen, shadow, [(x - 3, y - 5), (x + 3, y - 5), (x, y - 1)])

    def behavior(self, dt):
        d = distance(self.pos, self.player.pos)
        if d > self.attack_range:
            self.move_towards_player(dt)
        elif d < self.attack_range * 0.5:
            direction = self.pos - pygame.Vector2(self.player.pos)
            if direction.length() > 0:
                self.pos += direction.normalize() * self.effective_speed * dt

        if self.attack_cooldown <= 0 and d <= self.attack_range:
            self.shoot()
            self.attack_cooldown = 90

    def shoot(self):
        direction = pygame.Vector2(self.player.pos) - self.pos
        if direction.length() == 0:
            return
        angle = math.degrees(math.atan2(direction.y, direction.x))
        bullet = SkeletonBullet(tuple(self.pos), angle, damage=self.damage, speed=4)
        EventHandler().notify("SpawnObject", bullet)


class Knight(Enemy):
    """Cavaleiro de armadura: alta resistência e alto dano, mas extremamente lento."""
    base_hp = 70
    base_damage = 20
    speed = 0.4
    color = (170, 170, 190)
    radius = 18
    xp_value = 9
    coin_chance = 0.35

    def draw_body(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        metal = (185, 190, 205)
        dark_metal = (75, 80, 100)
        pygame.draw.ellipse(screen, dark_metal, (x - 17, y - 1, 34, 30))
        pygame.draw.rect(screen, metal, (x - 13, y - 10, 26, 27), border_radius=6)
        pygame.draw.circle(screen, (135, 140, 155), (x, y - 15), 13)
        pygame.draw.polygon(screen, metal, [(x - 11, y - 20), (x - 6, y - 31),
                          (x - 2, y - 20)])
        pygame.draw.polygon(screen, metal, [(x + 11, y - 20), (x + 6, y - 31),
                          (x + 2, y - 20)])
        pygame.draw.rect(screen, (35, 38, 48), (x - 10, y - 16, 20, 5))
        pygame.draw.line(screen, (225, 230, 240), (x, y - 27), (x, y + 8), 2)
    weight = 1.5

    def behavior(self, dt):
        self.move_towards_player(dt)
        if distance(self.pos, self.player.pos) < self.radius + 20 and self.attack_cooldown <= 0:
            EventHandler().notify("DamagePlayer", {"amount": self.damage, "magic": False})
            self.attack_cooldown = 70


class Elite(Enemy):
    """Elite de rodada: resistente, ligeiramente mais rapido que o cavaleiro e ataca a distancia."""
    base_hp = Knight.base_hp * 10
    base_damage = Skeleton.base_damage + 10
    speed = 0.55
    color = (245, 125, 25)
    radius = 22
    xp_value = 25
    attack_range = 300

    def draw_body(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        armor = (230, 105, 20)
        shadow = (105, 42, 12)
        pygame.draw.polygon(screen, shadow, [(x - 20, y + 16), (x - 16, y - 11),
                          (x, y - 21), (x + 16, y - 11), (x + 20, y + 16)])
        pygame.draw.polygon(screen, armor, [(x - 15, y + 14), (x - 12, y - 9),
                          (x, y - 16), (x + 12, y - 9), (x + 15, y + 14)])
        pygame.draw.circle(screen, (255, 170, 45), (x, y - 14), 10)
        pygame.draw.rect(screen, (55, 25, 12), (x - 9, y - 16, 18, 5))
        pygame.draw.polygon(screen, (255, 205, 70), [(x - 8, y - 22), (x - 4, y - 31),
                          (x, y - 23), (x + 5, y - 32), (x + 9, y - 22)])
        pygame.draw.line(screen, (255, 220, 100), (x - 9, y + 1), (x + 9, y + 1), 2)

    def behavior(self, dt):
        d = distance(self.pos, self.player.pos)
        if d > self.attack_range:
            self.move_towards_player(dt)
        elif d < self.attack_range * 0.5:
            direction = self.pos - pygame.Vector2(self.player.pos)
            if direction.length() > 0:
                self.pos += direction.normalize() * self.effective_speed * dt

        if self.attack_cooldown <= 0 and d <= self.attack_range:
            self.shoot()
            self.attack_cooldown = 120

    def shoot(self):
        direction = pygame.Vector2(self.player.pos) - self.pos
        if direction.length() == 0:
            return
        angle = math.degrees(math.atan2(direction.y, direction.x))
        bullet = EnemyBullet(tuple(self.pos), angle, damage=self.damage, speed=2.5, radius=9)
        EventHandler().notify("SpawnObject", bullet)


class Boss(Enemy):
    """Boss gigante das dezenas: muita vida e rajadas de seis projeteis."""
    base_hp = 7000
    base_damage = Elite.base_damage * 5
    speed = 0.3
    color = (220, 35, 35)
    radius = 50
    xp_value = 60
    attack_range = None

    def draw_body(self, screen):
        x, y = int(self.pos.x), int(self.pos.y)
        body = (220, 35, 35)
        dark_body = (105, 12, 18)
        wing = (150, 20, 28)
        pygame.draw.polygon(screen, wing, [(x - 28, y - 3), (x - 65, y - 32),
                          (x - 45, y + 18), (x - 22, y + 25)])
        pygame.draw.polygon(screen, wing, [(x + 28, y - 3), (x + 65, y - 32),
                          (x + 45, y + 18), (x + 22, y + 25)])
        pygame.draw.ellipse(screen, dark_body, (x - 31, y - 15, 62, 64))
        pygame.draw.ellipse(screen, body, (x - 25, y - 11, 50, 55))
        pygame.draw.circle(screen, body, (x, y - 25), 26)
        pygame.draw.polygon(screen, body, [(x - 18, y - 38), (x - 25, y - 66),
                          (x - 6, y - 43)])
        pygame.draw.polygon(screen, body, [(x + 18, y - 38), (x + 25, y - 66),
                          (x + 6, y - 43)])
        pygame.draw.polygon(screen, (255, 185, 45), [(x - 14, y - 27), (x - 5, y - 31),
                          (x - 5, y - 22), (x - 14, y - 19)])
        pygame.draw.polygon(screen, (255, 185, 45), [(x + 14, y - 27), (x + 5, y - 31),
                          (x + 5, y - 22), (x + 14, y - 19)])
        pygame.draw.polygon(screen, dark_body, [(x - 9, y - 10), (x + 9, y - 10),
                          (x, y - 2)])
        pygame.draw.line(screen, (255, 100, 55), (x - 17, y + 7), (x - 10, y + 18), 3)
        pygame.draw.line(screen, (255, 100, 55), (x - 5, y + 5), (x, y + 18), 3)
        pygame.draw.line(screen, (255, 100, 55), (x + 7, y + 5), (x + 12, y + 17), 3)

    def __init__(self, pos, player, hp_mult=1.0, dmg_mult=1.0):
        super().__init__(pos, player, hp_mult, dmg_mult)
        self.next_attack_is_burst = True

    def behavior(self, dt):
        d = distance(self.pos, self.player.pos)
        if d > 260:
            self.move_towards_player(dt)
        elif d < 110:
            direction = self.pos - pygame.Vector2(self.player.pos)
            if direction.length() > 0:
                self.pos += direction.normalize() * self.effective_speed * dt

        if self.attack_cooldown <= 0:
            if self.next_attack_is_burst:
                self.shoot_burst()
            else:
                self.shoot_trail_projectile()
            self.next_attack_is_burst = not self.next_attack_is_burst
            self.attack_cooldown = 120

    def shoot_burst(self):
        direction = pygame.Vector2(self.player.pos) - self.pos
        if direction.length() == 0:
            return
        base_angle = math.degrees(math.atan2(direction.y, direction.x))
        for offset in (-25, -15, -5, 5, 15, 25):
            bullet = EnemyBullet(
                tuple(self.pos), base_angle + offset, damage=self.damage, speed=2.0, radius=12,
                life_time=None
            )
            EventHandler().notify("SpawnObject", bullet)

    def shoot_trail_projectile(self):
        direction = pygame.Vector2(self.player.pos) - self.pos
        if direction.length() == 0:
            return
        angle = math.degrees(math.atan2(direction.y, direction.x))
        projectile = BossTrailProjectile(
            tuple(self.pos), angle, damage=self.damage, player=self.player, speed=6, radius=10
        )
        EventHandler().notify("SpawnObject", projectile)
