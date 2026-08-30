import pygame
from grid import Grid
from piece import Piece
from rules import get_valid_moves, is_in_check, is_checkmate, is_stalemate

PROMOTION_TYPES = ['queen', 'rook', 'bishop', 'knight']
PROMO_ICON_SIZE = 60


def opponent_of(color):
    return 'black' if color == 'white' else 'white'


class ChessGame:
    def __init__(self, width, height, grid_rows=8, grid_cols=8, cell_size=65):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_x = (width - (grid_cols * cell_size)) // 2
        self.grid_y = (height - (grid_rows * cell_size)) // 2

        self.grid = Grid(self.grid_x, self.grid_y, (grid_rows, grid_cols), cell_size)
        self.objects = [self.grid]
        self.pieces = []

        self.current_turn = 'white'
        self.last_move = None
        self.selected_piece = None
        self.valid_moves = {}
        self.game_status = ""
        self.game_over = False
        self.promotion_pending = None
        self._promotion_images_cache = {}

        # cursor de teclado (linha/coluna navegadas com WASD / setas)
        self.cursor_row = 7
        self.cursor_col = 4
        self.promotion_cursor = 0

        self.font = pygame.font.SysFont(None, 36)
        self.highlight_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        pygame.draw.circle(self.highlight_surf, (30, 200, 30, 140),
                            (cell_size // 2, cell_size // 2), cell_size // 6)

        self._setup_board()

    # ---------- montagem inicial ----------
    def _create_piece(self, color, p_type, row, col):
        img_path = f"images/chess/{p_type}_{color}.png"
        px = self.grid_x + col * self.cell_size
        py = self.grid_y + row * self.cell_size
        piece = Piece(px, py, color, p_type, row, col, img_path, self.cell_size)
        self.grid.cells[row][col].piece = piece
        self.pieces.append(piece)
        self.objects.append(piece)
        return piece

    def _setup_board(self):
        order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for c in range(8):
            self._create_piece('black', order[c], 0, c)
            self._create_piece('black', 'pawn', 1, c)
            self._create_piece('white', 'pawn', 6, c)
            self._create_piece('white', order[c], 7, c)

    # ---------- status de jogo ----------
    def _update_game_status(self):
        if is_checkmate(self.current_turn, self.grid, self.last_move):
            winner = 'Pretas' if self.current_turn == 'white' else 'Brancas'
            self.game_status = f"Xeque-mate! {winner} vencem!"
            self.game_over = True
        elif is_stalemate(self.current_turn, self.grid, self.last_move):
            self.game_status = "Empate por afogamento!"
            self.game_over = True
        elif is_in_check(self.current_turn, self.grid):
            self.game_status = "Xeque!"
            self.game_over = False
        else:
            self.game_status = ""
            self.game_over = False

    # ---------- promoção ----------
    def _get_promotion_image(self, p_type, color):
        key = (p_type, color)
        if key not in self._promotion_images_cache:
            img = pygame.image.load(f"images/chess/{p_type}_{color}.png").convert_alpha()
            img = pygame.transform.scale(img, (PROMO_ICON_SIZE, PROMO_ICON_SIZE))
            self._promotion_images_cache[key] = img
        return self._promotion_images_cache[key]

    def _get_promotion_rects(self):
        total_width = PROMO_ICON_SIZE * 4
        start_x = self.width // 2 - total_width // 2
        y = self.height // 2 - PROMO_ICON_SIZE // 2
        return [
            (pygame.Rect(start_x + i * PROMO_ICON_SIZE, y, PROMO_ICON_SIZE, PROMO_ICON_SIZE), p_type)
            for i, p_type in enumerate(PROMOTION_TYPES)
        ]

    def _start_promotion(self, piece, row, col):
        self.promotion_pending = {'piece': piece, 'row': row, 'col': col, 'color': piece.color}
        self.promotion_cursor = 0

    def _complete_promotion(self, p_type):
        row, col = self.promotion_pending['row'], self.promotion_pending['col']
        color = self.promotion_pending['color']
        old_pawn = self.promotion_pending['piece']

        self.grid.cells[row][col].piece = None
        if old_pawn in self.pieces:
            self.pieces.remove(old_pawn)
        if old_pawn in self.objects:
            self.objects.remove(old_pawn)

        self._create_piece(color, p_type, row, col)

        self.promotion_pending = None
        self.current_turn = opponent_of(self.current_turn)
        self._update_game_status()

    # ---------- movimentação ----------
    def _move_piece(self, piece, r, c, move_type):
        old_r, old_c = piece.row, piece.col
        self.grid.cells[old_r][old_c].piece = None

        target = self.grid.cells[r][c].piece
        if target is not None:
            self.objects.remove(target)
            self.pieces.remove(target)

        if move_type == 'en_passant':
            captured = self.grid.cells[old_r][c].piece
            self.grid.cells[old_r][c].piece = None
            if captured in self.pieces:
                self.objects.remove(captured)
                self.pieces.remove(captured)

        if move_type == 'castle_king':
            rook = self.grid.cells[old_r][7].piece
            self.grid.cells[old_r][7].piece = None
            rook.set_position(old_r, 5, self.grid_x, self.grid_y)
            self.grid.cells[old_r][5].piece = rook
        elif move_type == 'castle_queen':
            rook = self.grid.cells[old_r][0].piece
            self.grid.cells[old_r][0].piece = None
            rook.set_position(old_r, 3, self.grid_x, self.grid_y)
            self.grid.cells[old_r][3].piece = rook

        piece.set_position(r, c, self.grid_x, self.grid_y)
        self.grid.cells[r][c].piece = piece

        self.last_move = {
            'piece_type': piece.type,
            'from': (old_r, old_c),
            'to': (r, c),
            'move_type': move_type,
        }

        self.selected_piece.selected = False
        self.selected_piece = None

        if piece.type == 'pawn' and (r == 0 or r == 7):
            self._start_promotion(piece, r, c)
        else:
            self.current_turn = opponent_of(self.current_turn)
            self._update_game_status()

    # ---------- seleção (compartilhada entre mouse e teclado) ----------
    def _handle_cell_click(self, r, c):
        clicked_cell = self.grid.cells[r][c]

        if self.selected_piece is None:
            if clicked_cell.piece is not None and clicked_cell.piece.color == self.current_turn:
                self.selected_piece = clicked_cell.piece
                self.selected_piece.selected = True
                moves = get_valid_moves(self.selected_piece, self.grid, self.last_move)
                self.valid_moves = {(mr, mc): mt for mr, mc, mt in moves}
        else:
            if (r, c) in self.valid_moves:
                self._move_piece(self.selected_piece, r, c, self.valid_moves[(r, c)])
                self.valid_moves = {}
            elif clicked_cell.piece is not None and clicked_cell.piece.color == self.current_turn:
                self.selected_piece.selected = False
                self.selected_piece = clicked_cell.piece
                self.selected_piece.selected = True
                moves = get_valid_moves(self.selected_piece, self.grid, self.last_move)
                self.valid_moves = {(mr, mc): mt for mr, mc, mt in moves}
            else:
                self.selected_piece.selected = False
                self.selected_piece = None
                self.valid_moves = {}

    def _handle_board_click(self, pos):
        cell_pos = self.grid.get_cell_from_mouse(pos)
        if not cell_pos:
            return
        r, c = cell_pos
        self._handle_cell_click(r, c)

    # ---------- teclado ----------
    def _move_cursor(self, dr, dc):
        self.cursor_row = max(0, min(self.grid.rows - 1, self.cursor_row + dr))
        self.cursor_col = max(0, min(self.grid.cols - 1, self.cursor_col + dc))

    def _handle_keydown(self, key):
        if self.promotion_pending is not None or self.game_over:
            return

        if key in (pygame.K_w, pygame.K_UP):
            self._move_cursor(-1, 0)
        elif key in (pygame.K_s, pygame.K_DOWN):
            self._move_cursor(1, 0)
        elif key in (pygame.K_a, pygame.K_LEFT):
            self._move_cursor(0, -1)
        elif key in (pygame.K_d, pygame.K_RIGHT):
            self._move_cursor(0, 1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._handle_cell_click(self.cursor_row, self.cursor_col)

    # ---------- entrada do usuário ----------
    def handle_event(self, event):
        if self.is_animating():
            return
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            if self.promotion_pending is not None:
                for rect, p_type in self._get_promotion_rects():
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        self._complete_promotion(p_type)
                        break
            elif not self.game_over:
                self._handle_board_click(pygame.mouse.get_pos())

        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)

    # ---------- atualização e desenho ----------
    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)

    def draw(self, screen):
        screen.fill((30, 30, 30))
        for obj in self.objects:
            obj.draw(screen)

        for (r, c) in self.valid_moves:
            screen.blit(self.highlight_surf,
                        (self.grid_x + c * self.cell_size, self.grid_y + r * self.cell_size))

        # borda da peça atualmente selecionada
        if self.selected_piece is not None:
            sel_rect = pygame.Rect(
                self.grid_x + self.selected_piece.col * self.cell_size,
                self.grid_y + self.selected_piece.row * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(screen, (255, 20, 147), sel_rect, 4)

        # borda do cursor de teclado
        if not self.game_over:
            cursor_rect = pygame.Rect(
                self.grid_x + self.cursor_col * self.cell_size,
                self.grid_y + self.cursor_row * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(screen, (255, 20, 147), cursor_rect, 3)

        if self.game_status:
            text_surf = self.font.render(self.game_status, True, (255, 60, 60))
            screen.blit(text_surf, (self.width // 2 - text_surf.get_width() // 2, 15))

        if self.promotion_pending is not None:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            for rect, p_type in self._get_promotion_rects():
                pygame.draw.rect(screen, (255, 255, 255), rect)
                img = self._get_promotion_image(p_type, self.promotion_pending['color'])
                screen.blit(img, rect.topleft)
        # mensagem de turno
        if not self.game_over:
            turn_label = "Brancas jogam" if self.current_turn == 'white' else "Pretas jogam"
            turn_surf = self.font.render(turn_label, True, (245, 230, 240))
            screen.blit(turn_surf, (self.width // 2 - turn_surf.get_width() // 2, self.height - 40))

        if self.game_status:
            text_surf = self.font.render(self.game_status, True, (255, 60, 150))
            screen.blit(text_surf, (self.width // 2 - text_surf.get_width() // 2, 15))

        if self.promotion_pending is not None:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            for rect, p_type in self._get_promotion_rects():
                pygame.draw.rect(screen, (255, 255, 255), rect)
                img = self._get_promotion_image(p_type, self.promotion_pending['color'])
                screen.blit(img, rect.topleft)
    def is_animating(self):
        return any(p.animating for p in self.pieces)
    
