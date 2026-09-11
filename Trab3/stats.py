class PlayerStats:
    """Guarda todos os atributos que os upgrades e a loja podem modificar."""

    def __init__(self):
        self.level = 1
        self.xp = 0
        self.xp_to_next = 10
        self.coins = 0

        self.max_hp = 100
        self.hp = 100
        self.max_mana = 50
        self.mana = 50
        self.mana_regen = 1.0   # mana por segundo
        self.hp_regen = 0.5     # vida por segundo

        self.physical_damage = 10
        self.magic_damage = 5
        self.armor = 0          # reduz dano sofrido (fórmula com retorno decrescente)
        self.speed = 3.0        # pixels por frame
        self.attack_speed = 1.0 # multiplicador; 1.0 = velocidade base de ataque

        self.extra_projectiles = 0  # projéteis extras disparados por tiro/magia
        self.gold_bonus = 0         # ouro extra por moeda coletada
        self.xp_bonus = 0           # xp extra por orbe coletado

    def take_damage(self, amount, magic=False):
        # fórmula de armadura com retorno decrescente: 100 de armadura = 50% de redução
        reduction = self.armor / (self.armor + 100)
        final = amount * (1 - reduction)
        self.hp -= final
        return final

    def add_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.25) + 5
            leveled = True
        return leveled

    def add_coins(self, amount):
        self.coins += amount

    def is_dead(self):
        return self.hp <= 0
