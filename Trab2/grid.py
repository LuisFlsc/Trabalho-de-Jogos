# Classe base abstrata (Abstract Base Class)
from abc import ABC, abstractmethod


# objeto herda de classe abstrata
## nunca pode ser criada, só as filhas
class obj (ABC):

    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        #lista
        self.sprites = sprites


    def draw(self, screen):
        for s in self.sprites:
            screen.blit(self.sprites, (self.x, self.y))

    # avisa que o método é abstato e precisa ser feito pelos filhos
    @abstractmethod
    def update(self, dt):
        pass

class Grid (obj):

    # só avisa a construtora da mãe o que fazer
    # pode, e deve ser extendido para outras caracteristicas nescessárias
    def __init__(self, x, y, sprites, grid_size):
        # bom lugar para criar uma matriz de celulas
        super().__init__(x, y, sprites)

    def draw(self, screen):

        # chama o desenha já pronto de obj, mas pode ser extendido
        return super().draw(screen)

    def update(self, dt):
        # não chama o de super, porque ele não implementa, crie seu próprio
        return 


class Cell (obj):

    # só avisa a construtora da mãe o que fazer
    # pode, e deve ser extendido para outras caracteristicas nescessárias
    def __init__(self, x, y, sprites, grid_size):
        # bom lugar para definir coisas como o fundo da céula
        super().__init__(x, y, sprites)

    def draw(self, screen):

        # chama o desenha já pronto de obj, mas pode ser extendido
        return super().draw(screen)

    def update(self, dt):
        # não chama o de super, porque ele não implementa, crie seu próprio
        return 
