import random
from enemy import Slime, Zombie, Skeleton, Knight, Elite, Boss
from util import EventHandler


class WaveManager:
    """
    Controla as ondas infinitas de inimigos.

    - A cada onda o número de inimigos cresce em 10 unidades.
    - A cada 10 ondas, o total de inimigos dobra e resistência/dano sobem.
    - Slimes são fracos: um grupo de 10 slimes consome só 1 unidade de inimigos.
    """

    def __init__(self, player):
        self.player = player
        self.wave = 0
        self.spawn_queue = []
        self.spawn_timer = 0
        self.spawn_interval = 8  # frames entre cada spawn individual
        self.wave_active = False
        self.enemies_alive = 0

        EventHandler().subscribe("EnemyDied", self.on_enemy_died)

    def on_enemy_died(self, enemy):
        self.enemies_alive = max(0, self.enemies_alive - 1)

    def start_next_wave(self):
        self.wave += 1

        tier = (self.wave - 1) // 10  # a cada 10 ondas sobe um "tier" de dificuldade
        budget = 10 * self.wave * (2 ** tier)
        hp_mult = 1.15 ** tier
        dmg_mult = 1.15 ** tier

        if self.wave % 10 == 0:
            self.spawn_queue = [(Boss, hp_mult, dmg_mult)]
        else:
            self.spawn_queue = self._build_spawn_list(budget, hp_mult, dmg_mult)

        if self.wave % 10 == 5:
            self.spawn_queue.append((Elite, hp_mult, dmg_mult))
            random.shuffle(self.spawn_queue)
        self.spawn_timer = 0
        self.wave_active = True
        self.enemies_alive = 0

    def _build_spawn_list(self, budget, hp_mult, dmg_mult):
        queue = []
        remaining = budget
        while remaining > 0:
            choice = random.choices(
                ["slime", "zombie", "skeleton", "knight"], weights=[40, 27, 20, 13], k=1
            )[0]
            if choice == "slime":
                for _ in range(10):
                    queue.append((Slime, hp_mult, dmg_mult))
                remaining -= 1
            elif choice == "zombie":
                queue.append((Zombie, hp_mult, dmg_mult))
                remaining -= 1
            elif choice == "skeleton":
                queue.append((Skeleton, hp_mult, dmg_mult))
                remaining -= 1
            else:
                queue.append((Knight, hp_mult, dmg_mult))
                remaining -= 1
        random.shuffle(queue)
        return queue

    def update(self, dt, screen_size):
        if not self.wave_active:
            return

        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                cls, hp_mult, dmg_mult = self.spawn_queue.pop(0)
                pos = self._random_edge_position(screen_size)
                enemy = cls(pos, self.player, hp_mult, dmg_mult)
                EventHandler().notify("SpawnObject", enemy)
                self.enemies_alive += 1
                self.spawn_timer = self.spawn_interval
        elif self.enemies_alive <= 0:
            self.wave_active = False
            EventHandler().notify("WaveCleared", self.wave)

    def _random_edge_position(self, screen_size):
        w, h = screen_size
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return (random.uniform(0, w), -20)
        if side == "bottom":
            return (random.uniform(0, w), h + 20)
        if side == "left":
            return (-20, random.uniform(0, h))
        return (w + 20, random.uniform(0, h))
