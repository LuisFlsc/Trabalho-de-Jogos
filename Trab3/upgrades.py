import random
from util import weighted_sample_without_replacement

# Quanto mais raro, menor o peso -> mais dificil de aparecer.
RARITIES = [
    {"name": "Comum",    "color": (150, 150, 150), "weight": 100, "mult": 1.0},
    {"name": "Incomum",  "color": (60, 200, 80),   "weight": 55,  "mult": 1.6},
    {"name": "Rara",     "color": (60, 120, 230),  "weight": 25,  "mult": 2.4},
    {"name": "Épica",    "color": (150, 60, 220),  "weight": 8,   "mult": 3.5},
    {"name": "Lendária", "color": (240, 140, 30),  "weight": 2,   "mult": 5.0},
]


class Upgrade:
    def __init__(self, key, label, rarity, base_value, apply_fn, desc_fmt, fixed=False):
        self.key = key
        self.label = label
        self.rarity = rarity
        # "fixed" pula a multiplicação por raridade: usado por upgrades com valor
        # fixo por raridade (ex: projéteis extras), em vez de escalar continuamente.
        self.value = base_value if fixed else base_value * rarity["mult"]
        self.apply_fn = apply_fn
        self.description = desc_fmt.format(self.value)

    def apply(self, player_stats):
        self.apply_fn(player_stats, self.value)


def _bump(attr):
    def fn(stats, v):
        setattr(stats, attr, getattr(stats, attr) + v)
    return fn


def _bump_int(attr):
    def fn(stats, v):
        setattr(stats, attr, getattr(stats, attr) + int(v))
    return fn


def _bump_with_current(max_attr, cur_attr):
    def fn(stats, v):
        setattr(stats, max_attr, getattr(stats, max_attr) + v)
        setattr(stats, cur_attr, getattr(stats, cur_attr) + v)
    return fn


# (chave, nome exibido, valor base (na raridade comum), função de aplicação, formato da descrição)
ATTRIBUTES = [
    ("physical_damage", "Dano Físico",         3,    _bump("physical_damage"),               "+{:.0f} de dano físico"),
    ("magic_damage",    "Dano Mágico",         3,    _bump("magic_damage"),                  "+{:.0f} de dano mágico"),
    ("armor",           "Armadura",            4,    _bump("armor"),                          "+{:.0f} de armadura"),
    ("max_hp",          "Vida Máxima",         15,   _bump_with_current("max_hp", "hp"),      "+{:.0f} de vida máxima"),
    ("speed",           "Velocidade",          0.3,  _bump("speed"),                          "+{:.1f} de velocidade"),
    ("max_mana",        "Mana Máxima",         10,   _bump_with_current("max_mana", "mana"),  "+{:.0f} de mana máxima"),
    ("mana_regen",      "Regen. de Mana",      0.4,  _bump("mana_regen"),                     "+{:.1f} de regeneração de mana/s"),
    ("hp_regen",        "Regen. de Vida",      0.5,  _bump("hp_regen"),                       "+{:.1f} de regeneração de vida/s"),
    ("attack_speed",    "Velocidade de Ataque", 0.08, _bump("attack_speed"),                  "+{:.0%} de velocidade de ataque"),
]

# Upgrade especial: só aparece nas raridades Épica (+1) e Lendária (+2), com valor fixo
# em vez de escalar pela raridade como os atributos comuns acima.
PROJECTILE_ATTRIBUTE = ("extra_projectiles", "Projéteis Extras", None,
                          _bump_int("extra_projectiles"), "+{:.0f} projétil(eis) disparado(s)")
PROJECTILE_RARITY_POOL = [RARITIES[3], RARITIES[4]]   # Épica, Lendária
PROJECTILE_FIXED_VALUES = {"Épica": 1, "Lendária": 2}

# Todas as opções que podem ser sorteadas num level up (atributos normais + especial)
ALL_ATTRIBUTES = ATTRIBUTES + [PROJECTILE_ATTRIBUTE]


def roll_rarity():
    weights = [r["weight"] for r in RARITIES]
    return random.choices(RARITIES, weights=weights, k=1)[0]


def _roll_projectile_upgrade():
    key, label, _base, fn, fmt = PROJECTILE_ATTRIBUTE
    weights = [r["weight"] for r in PROJECTILE_RARITY_POOL]
    rarity = random.choices(PROJECTILE_RARITY_POOL, weights=weights, k=1)[0]
    value = PROJECTILE_FIXED_VALUES[rarity["name"]]
    return Upgrade(key, label, rarity, value, fn, fmt, fixed=True)


def generate_choices(count=3):
    """Sorteia `count` atributos diferentes, cada um com uma raridade independente."""
    chosen_attrs = weighted_sample_without_replacement(
        ALL_ATTRIBUTES, [1] * len(ALL_ATTRIBUTES), count
    )
    upgrades = []
    for key, label, base, fn, fmt in chosen_attrs:
        if key == "extra_projectiles":
            upgrades.append(_roll_projectile_upgrade())
        else:
            rarity = roll_rarity()
            upgrades.append(Upgrade(key, label, rarity, base, fn, fmt))
    return upgrades
