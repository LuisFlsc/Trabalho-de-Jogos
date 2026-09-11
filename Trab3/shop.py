import random


class ShopItem:
    def __init__(self, name, cost, description, effect):
        self.name = name
        self.cost = cost
        self.description = description
        self.effect = effect
        self.purchased = False

    def buy(self, player):
        if self.purchased or player.stats.coins < self.cost:
            return False
        player.stats.coins -= self.cost
        self.effect(player)
        self.purchased = True
        return True


def heal_effect(amount):
    def fn(player):
        player.stats.hp = min(player.stats.max_hp, player.stats.hp + amount)
    return fn


def stat_effect(attr, amount):
    def fn(player):
        setattr(player.stats, attr, getattr(player.stats, attr) + amount)
        if attr == "max_hp":
            player.stats.hp += amount
        if attr == "max_mana":
            player.stats.mana += amount
    return fn


def unlock_fireball(player):
    """Habilidade: bola de fogo em TAB (action_2)."""
    player.has_fireball = True


def unlock_chain_lightning(player):
    """Habilidade: raio em cadeia em Q (action_3)."""
    player.has_chain_lightning = True


def unlock_blizzard(player):
    """Habilidade: nevasca em cone em E (action_4), mira no cursor."""
    player.has_blizzard = True


def unlock_force_field(player):
    """Habilidade: campo de força em R (action_5)."""
    player.has_force_field = True


# (nome, custo base, descrição, efeito)
ITEM_POOL = [
    ("Poção de Vida",          5, "Recupera 20 de vida",                                    heal_effect(20)),
    ("Elmo de Ferro",          12, "+8 de armadura",                                          stat_effect("armor", 8)),
    ("Amuleto Arcano",         10, "+15 de mana máxima",                                      stat_effect("max_mana", 15)),
    ("Botas Rápidas",          30, "+0.5 de velocidade",                                       stat_effect("speed", 0.5)),
    ("Lâmina Afiada",          15, "+6 de dano físico",                                        stat_effect("physical_damage", 6)),
    ("Cajado Rúnico",          17, "+6 de dano mágico",                                        stat_effect("magic_damage", 6)),
    ("Coração Robusto",        40, "+25 de vida máxima",                                      stat_effect("max_hp", 25)),
    ("Bolsa Encantada",        50, "+1 de ouro por moeda coletada",                            stat_effect("gold_bonus", 1)),
    ("Cristal do Conhecimento",50, "+1 de XP por orbe coletado",                               stat_effect("xp_bonus", 1)),
    ("Grimório de Fogo",       0, "Magia: Bola de Fogo (TAB)",                                unlock_fireball),
    ("Cristal de Gelo",        0, "Magia: Nevasca em Cone (E)",                               unlock_blizzard),
    ("Cajado do Raio",         0, "Magia: Raio em Cadeia (Q)",                                unlock_chain_lightning),
    ("Núcleo Arcano",          0, "Magia: Campo de Força (R)",                                unlock_force_field),
]


def generate_shop(wave, count=5):
    pool = random.sample(ITEM_POOL, min(count, len(ITEM_POOL)))
    items = []
    for name, cost, desc, effect in pool:
        scaled_cost = int(cost * (1 + wave * 0.05))  # loja fica mais cara conforme as ondas avançam
        items.append(ShopItem(name, scaled_cost, desc, effect))
    return items
