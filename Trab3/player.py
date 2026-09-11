import pygame
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler, distance
from bullet import PlayerBullet
from stats import PlayerStats
from enemy import Enemy
from effects import DashEffect, ChainLightningEffect, CrescentEffect, ForceField


def _spread_angles(base_angle, count, spread_deg=12):
    """Gera `count` ângulos em leque ao redor de base_angle, para o efeito de
    'projéteis extras' (a carta épica/lendária)."""
    if count <= 1:
        return [base_angle]
    start = -spread_deg * (count - 1) / 2
    return [base_angle + start + i * spread_deg for i in range(count)]


class Player:

    def __init__(self, pos, objects_ref=None):
        self.pos = pygame.Vector2(pos)
        self.stats = PlayerStats()
        self.objects_ref = objects_ref if objects_ref is not None else []
        self.invuln_timer = 0
        self.damage_flash_timer = 0

        # magias desbloqueáveis na loja
        self.has_fireball = False
        self.has_chain_lightning = False
        self.has_blizzard = False
        self.has_force_field = False

        self.state = MoveShootState(self)

        EventHandler().subscribe("DamagePlayer", self.on_damage)

    def on_damage(self, data):
        if self.invuln_timer > 0 or self.stats.is_dead():
            return
        self.stats.take_damage(data["amount"], data.get("magic", False))
        self.invuln_timer = 30  # ~0.5s de invencibilidade a 60 fps
        self.damage_flash_timer = 10

    def update(self, dt):
        if self.stats.is_dead():
            return
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
        self.stats.mana = min(
            self.stats.max_mana, self.stats.mana + self.stats.mana_regen * (dt / 60)
        )
        self.stats.hp = min(
            self.stats.max_hp, self.stats.hp + self.stats.hp_regen * (dt / 60)
        )
        self.state.update(dt)

    def draw(self, screen):
        self.state.draw(screen)
        if self.damage_flash_timer > 0:
            flash = pygame.Surface((42, 42), pygame.SRCALPHA)
            pygame.draw.circle(flash, (255, 55, 55, 80), (21, 21), 20)
            screen.blit(flash, self.pos - pygame.Vector2(21, 21))

    def action_1(self):
        self.state.action_1()

    def action_2(self):
        self.state.action_2()

    def action_3(self):
        self.state.action_3()

    def action_4(self, target_pos):
        self.state.action_4(target_pos)

    def action_5(self):
        self.state.action_5()

    def cast_basic_spell(self, target_pos):
        self.state.cast_basic_spell(target_pos)

    def change_state(self, new_state):
        self.state.delete()
        self.state = new_state(self)

    def nearest_enemy(self, max_range=None):
        enemies = [o for o in self.objects_ref if isinstance(o, Enemy) and o.alive]
        if not enemies:
            return None
        target = min(enemies, key=lambda e: distance(self.pos, e.pos))
        if max_range and distance(self.pos, target.pos) > max_range:
            return None
        return target

    def enemies_in_range(self, max_range):
        return [
            o for o in self.objects_ref
            if isinstance(o, Enemy) and o.alive and distance(self.pos, o.pos) <= max_range
        ]


class PlayerState(ABC):

    sprite = colored_sprite((255, 20, 147))  # rosa-choque

    def __init__(self, player):
        self.P = player

    def draw(self, screen):
        screen.blit(self.sprite, self.P.pos - pygame.Vector2(16, 16))

    def delete(self):
        pass  # se precisar apagar algo na mudança de estados

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def action_1(self):
        pass

    @abstractmethod
    def action_2(self):
        pass

    # ações adicionais: implementação padrão vazia, estados que não usam
    # magia não precisam sobrescrever.
    def action_3(self):
        pass

    def action_4(self, target_pos):
        pass

    def action_5(self):
        pass

    def cast_basic_spell(self, target_pos):
        pass


class MoveShootState(PlayerState):
    """Estado principal: move com WASD/setas, atira automaticamente no inimigo mais
    próximo e dá acesso às magias (clique direito + SPACE/TAB/Q/E/R)."""

    sprite = colored_sprite((255, 20, 147))  # rosa-choque

    ATTACK_RANGE = 600
    ATTACK_COOLDOWN = 20  # frames entre tiros, na velocidade de ataque base (1.0)

    DASH_COST = 10
    DASH_COOLDOWN = 60

    FIREBALL_COST = 15
    FIREBALL_COOLDOWN = 30

    BASIC_SPELL_COST = 8
    BASIC_SPELL_COOLDOWN = 25
    BASIC_SPELL_DAMAGE_MULT = 1.3
    BASIC_SPELL_PIERCE = 3

    CHAIN_COST = 25
    CHAIN_COOLDOWN = 180        # 3s
    CHAIN_RANGE = 380
    CHAIN_MAX_TARGETS = 5
    CHAIN_STUN = 30              # 0.5s a 60 fps
    CHAIN_DAMAGE_MULT = 1.1

    BLIZZARD_COST = 30
    BLIZZARD_COOLDOWN = 240      # 4s
    BLIZZARD_RANGE = 220
    BLIZZARD_HALF_ANGLE = 35
    BLIZZARD_PUSH = 40
    BLIZZARD_SLOW_DURATION = 120  # 2s
    BLIZZARD_SLOW_MULT = 0.4

    FORCE_FIELD_COST = 35
    FORCE_FIELD_COOLDOWN = 900   # 15s até poder reativar
    FORCE_FIELD_RADIUS = 100
    FORCE_FIELD_DAMAGE = 4
    FORCE_FIELD_TICK = 20
    FORCE_FIELD_DURATION = 1800  # 30s

    def __init__(self, player):
        super().__init__(player)
        self.attack_cooldown = 0
        self.dash_cooldown = 0
        self.fireball_cooldown = 0
        self.basic_spell_cooldown = 0
        self.chain_cooldown = 0
        self.blizzard_cooldown = 0
        self.force_field_cooldown = 0

    def update(self, dt):
        self.handle_movement(dt)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        else:
            self.try_attack()

        for attr in ("dash_cooldown", "fireball_cooldown", "basic_spell_cooldown",
                     "chain_cooldown", "blizzard_cooldown", "force_field_cooldown"):
            val = getattr(self, attr)
            if val > 0:
                setattr(self, attr, val - dt)

    def handle_movement(self, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1
        if move.length() > 0:
            move = move.normalize()

        self.P.pos += move * self.P.stats.speed * dt

        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.P.pos.x = max(16, min(screen_width - 16, self.P.pos.x))
        self.P.pos.y = max(16, min(screen_height - 16, self.P.pos.y))

    def _fire_bullets(self, base_angle, damage, magic=False, speed=9, pierce=0):
        count = 1 + self.P.stats.extra_projectiles
        for angle in _spread_angles(base_angle, count):
            bullet = PlayerBullet(
                tuple(self.P.pos), angle, damage=damage, magic=magic, speed=speed, pierce=pierce
            )
            EventHandler().notify("SpawnObject", bullet)

    def try_attack(self):
        target = self.P.nearest_enemy(max_range=self.ATTACK_RANGE)
        if not target:
            return
        direction = target.pos - self.P.pos
        if direction.length() == 0:
            return
        angle = pygame.math.Vector2(1, 0).angle_to(direction)
        self._fire_bullets(angle, damage=self.P.stats.physical_damage)
        self.attack_cooldown = self.ATTACK_COOLDOWN / max(0.01, self.P.stats.attack_speed)

    def cast_basic_spell(self, target_pos):
        """Magia básica: projétil perfurante, um pouco mais forte que o tiro comum.
        Disparada com o botão direito do mouse, mirando no cursor."""
        if self.basic_spell_cooldown > 0 or self.P.stats.mana < self.BASIC_SPELL_COST:
            return
        direction = pygame.Vector2(target_pos) - self.P.pos
        if direction.length() == 0:
            return
        angle = pygame.math.Vector2(1, 0).angle_to(direction)
        damage = self.P.stats.magic_damage * self.BASIC_SPELL_DAMAGE_MULT
        self._fire_bullets(angle, damage=damage, magic=True, speed=11, pierce=self.BASIC_SPELL_PIERCE)
        self.P.stats.mana -= self.BASIC_SPELL_COST
        self.basic_spell_cooldown = self.BASIC_SPELL_COOLDOWN

    def action_1(self):
        """Dash curto, custa mana."""
        if self.dash_cooldown > 0 or self.P.stats.mana < self.DASH_COST:
            return
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1
        if move.length() == 0:
            move = pygame.Vector2(1, 0)
        else:
            move = move.normalize()

        start_pos = pygame.Vector2(self.P.pos)
        self.P.pos += move * 80
        EventHandler().notify("SpawnObject", DashEffect(start_pos, self.P.pos))
        self.P.stats.mana -= self.DASH_COST
        self.dash_cooldown = self.DASH_COOLDOWN

    def action_2(self):
        """Bola de fogo (TAB): só funciona se comprada na loja (Grimório de Fogo)."""
        if not self.P.has_fireball:
            return
        if self.fireball_cooldown > 0 or self.P.stats.mana < self.FIREBALL_COST:
            return
        target = self.P.nearest_enemy()
        if not target:
            return
        direction = target.pos - self.P.pos
        if direction.length() == 0:
            return
        angle = pygame.math.Vector2(1, 0).angle_to(direction)
        self._fire_bullets(angle, damage=self.P.stats.magic_damage * 2.5, magic=True, speed=12)
        self.P.stats.mana -= self.FIREBALL_COST
        self.fireball_cooldown = self.FIREBALL_COOLDOWN

    def action_3(self):
        """Raio em cadeia (Q): salta entre inimigos e continua após uma morte."""
        if not self.P.has_chain_lightning:
            return
        if self.chain_cooldown > 0 or self.P.stats.mana < self.CHAIN_COST:
            return
        available = self.P.enemies_in_range(self.CHAIN_RANGE)
        if not available:
            return

        targets = []
        current_pos = pygame.Vector2(self.P.pos)
        while available and len(targets) < self.CHAIN_MAX_TARGETS:
            next_target = min(available, key=lambda enemy: distance(current_pos, enemy.pos))
            if distance(current_pos, next_target.pos) > self.CHAIN_RANGE:
                break
            targets.append(next_target)
            available.remove(next_target)
            current_pos = pygame.Vector2(next_target.pos)

        damage = self.P.stats.magic_damage * self.CHAIN_DAMAGE_MULT
        hit_positions = []
        for enemy in targets:
            hit_positions.append(tuple(enemy.pos))
            enemy.take_damage(damage)
            if enemy.alive:
                enemy.stun(self.CHAIN_STUN)

        EventHandler().notify(
            "SpawnObject", ChainLightningEffect(tuple(self.P.pos), hit_positions)
        )
        self.P.stats.mana -= self.CHAIN_COST
        self.chain_cooldown = self.CHAIN_COOLDOWN

    def action_4(self, target_pos):
        """Nevasca em cone (E): empurra e reduz a velocidade dos inimigos por 2s.
        Mira na direção do cursor do mouse."""
        if not self.P.has_blizzard:
            return
        if self.blizzard_cooldown > 0 or self.P.stats.mana < self.BLIZZARD_COST:
            return
        direction = pygame.Vector2(target_pos) - self.P.pos
        if direction.length() == 0:
            return
        cone_dir = direction.normalize()
        EventHandler().notify(
            "SpawnObject",
            CrescentEffect(
                tuple(self.P.pos), cone_dir, self.BLIZZARD_RANGE, self.BLIZZARD_HALF_ANGLE,
                speed=8, objects_ref=self.P.objects_ref,
            ),
        )
        self.P.stats.mana -= self.BLIZZARD_COST
        self.blizzard_cooldown = self.BLIZZARD_COOLDOWN

    def action_5(self):
        """Campo de força (R): aura ao redor do jogador, dano contínuo por 30s."""
        if not self.P.has_force_field:
            return
        if self.force_field_cooldown > 0 or self.P.stats.mana < self.FORCE_FIELD_COST:
            return
        field = ForceField(
            self.P,
            radius=self.FORCE_FIELD_RADIUS,
            damage=self.FORCE_FIELD_DAMAGE,
            tick_interval=self.FORCE_FIELD_TICK,
            duration=self.FORCE_FIELD_DURATION,
        )
        EventHandler().notify("SpawnObject", field)
        self.P.stats.mana -= self.FORCE_FIELD_COST
        self.force_field_cooldown = self.FORCE_FIELD_COOLDOWN

        pass # faça sua implementação
