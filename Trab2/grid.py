from abc import ABC, abstractmethod
import pygame

class obj(ABC):
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        self.sprites = sprites

    def draw(self, screen):
        for s in self.sprites:
            screen.blit(s, (self.x, self.y))

    @abstractmethod
    def update(self, dt):
        pass


class Cell(obj):
    def __init__(self, x, y, size, color, row, col):
        super().__init__(x, y, [])
        self.size = size
        self.color = color
        self.row = row
        self.col = col
        self.piece = None

        surface = pygame.Surface((size, size))
        surface.fill(self.color)
        self.sprites = [surface]

    def update(self, dt):
        pass


class Grid(obj):
    def __init__(self, x, y, grid_size=(8, 8), cell_size=70):
        super().__init__(x, y, [])
        self.rows, self.cols = grid_size
        self.cell_size = cell_size
        self.cells = []

        color_light = (235, 226, 240)
        color_dark = (150, 120, 170)

        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                cx = self.x + c * cell_size
                cy = self.y + r * cell_size
                color = color_light if (r + c) % 2 == 0 else color_dark
                row_cells.append(Cell(cx, cy, cell_size, color, r, c))
            self.cells.append(row_cells)

    def get_cell_from_mouse(self, mouse_pos):
        mx, my = mouse_pos
        col = (mx - self.x) // self.cell_size
        row = (my - self.y) // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col
        return None

    def get_piece(self, row, col):
        """Retorna a peça em (row, col) ou None se fora do tabuleiro/vazia."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col].piece
        return None

    def draw(self, screen):
        for row in self.cells:
            for cell in row:
                cell.draw(screen)

    def update(self, dt):
        for row in self.cells:
            for cell in row:
                cell.update(dt)
