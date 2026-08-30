import pygame
from grid import obj

class Piece(obj):
    ANIM_DURATION = 0.18  # segundos que a peça leva pra deslizar até o destino

    def __init__(self, x, y, color, piece_type, row, col, image_path, cell_size):
        img = pygame.image.load(image_path).convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))

        super().__init__(x, y, [img])

        self.color = color
        self.type = piece_type
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.selected = False
        self.has_moved = False

        # estado da animação
        self.target_x = x
        self.target_y = y
        self.anim_start_x = x
        self.anim_start_y = y
        self.anim_elapsed = 0.0
        self.animating = False

    def set_position(self, row, col, grid_x, grid_y):
        self.row = row
        self.col = col
        self.has_moved = True

        new_x = grid_x + col * self.cell_size
        new_y = grid_y + row * self.cell_size

        # começa a animar a partir de onde a peça está visualmente agora
        self.anim_start_x = self.x
        self.anim_start_y = self.y
        self.target_x = new_x
        self.target_y = new_y
        self.anim_elapsed = 0.0
        self.animating = True

    def update(self, dt):
        if not self.animating:
            return

        self.anim_elapsed += dt
        t = min(self.anim_elapsed / self.ANIM_DURATION, 1.0)

        # ease-out cúbico: começa rápido e desacelera no final
        eased = 1 - (1 - t) ** 3

        self.x = self.anim_start_x + (self.target_x - self.anim_start_x) * eased
        self.y = self.anim_start_y + (self.target_y - self.anim_start_y) * eased

        if t >= 1.0:
            self.x = self.target_x
            self.y = self.target_y
            self.animating = False
