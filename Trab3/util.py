import pygame
import random


def singleton(class_):
    instances = { }
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)	# cria se ainda não existe
        return instances[class_] # armazena para mais tarde
    return getinstance # devolve a instância unica

@singleton
class EventHandler:
    def __init__(self):
        self.observers = { }  # passa a ser um dicionário onde chave é o tipo de evento

    def subscribe(self, type, callback): # passa o tipo de evento também
        if type not in self.observers: # caso não exista ainda
            self.observers[type] = [ ]  # cria um novo tipo de evento para notificar
        self.observers[type].append(callback) # inscreve a chamada ao evento

    def notify(self, type, data):
        if type in self.observers: # checa se tem eventos desse tipo
            for o in self.observers[type]: # para todos os inscritos nele
                o(data) # avise que o evento ocorreu


def colored_sprite(color, size=(32, 32), circle = True):
    sprite = pygame.Surface(size)
    if circle:
        sprite.set_colorkey((0,0,0))
        pygame.draw.circle(sprite, color, (size[0]//2, size[1]//2), size[0]//2)
    else:
        sprite.fill(color)
    return sprite

def circle_collistiion (p1, r1, p2, r2):
    euc_distance = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(1/2)
    return  euc_distance <= r1 + r2


# ---------------------------------------------------------------------------
# Helpers novos, adicionados para o sistema de progressão / ondas / loja
# ---------------------------------------------------------------------------

def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


_FONT_CACHE = {}

def _get_font(size, font_name=None):
    key = (font_name, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(font_name, size)
    return _FONT_CACHE[key]


def draw_text(screen, text, pos, size=20, color=(255, 255, 255), center=False, font_name=None):
    font = _get_font(size, font_name)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surf, rect)
    return rect


def draw_bar(screen, pos, size, ratio, bg_color, fill_color, border_color=(0, 0, 0)):
    x, y = pos
    w, h = size
    ratio = clamp(ratio, 0, 1)
    pygame.draw.rect(screen, bg_color, (x, y, w, h))
    pygame.draw.rect(screen, fill_color, (x, y, w * ratio, h))
    pygame.draw.rect(screen, border_color, (x, y, w, h), 2)


def weighted_sample_without_replacement(population, weights, k):
    """Sorteia k itens sem repetição, respeitando pesos relativos."""
    population = list(population)
    weights = list(weights)
    result = []
    for _ in range(min(k, len(population))):
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        for i, w in enumerate(weights):
            upto += w
            if upto >= r:
                result.append(population.pop(i))
                weights.pop(i)
                break
    return result
