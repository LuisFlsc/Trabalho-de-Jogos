def get_all_pieces(grid, color=None):
    result = []
    for row in grid.cells:
        for cell in row:
            if cell.piece is not None and (color is None or cell.piece.color == color):
                result.append(cell.piece)
    return result


def find_king(color, grid):
    for piece in get_all_pieces(grid, color):
        if piece.type == 'king':
            return piece.row, piece.col
    return None


def opponent_of(color):
    return 'black' if color == 'white' else 'white'


def is_square_attacked(row, col, attacker_color, grid):
    """Diz se a casa (row, col) está sob ataque de alguma peça de attacker_color."""

    # Peões
    if attacker_color == 'white':
        pawn_positions = [(row + 1, col - 1), (row + 1, col + 1)]
    else:
        pawn_positions = [(row - 1, col - 1), (row - 1, col + 1)]
    for pr, pc in pawn_positions:
        if 0 <= pr < grid.rows and 0 <= pc < grid.cols:
            p = grid.get_piece(pr, pc)
            if p is not None and p.color == attacker_color and p.type == 'pawn':
                return True

    # Cavalo
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < grid.rows and 0 <= nc < grid.cols:
            p = grid.get_piece(nr, nc)
            if p is not None and p.color == attacker_color and p.type == 'knight':
                return True

    # Rei
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols:
                p = grid.get_piece(nr, nc)
                if p is not None and p.color == attacker_color and p.type == 'king':
                    return True

    # Torre / Dama (retas)
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        while 0 <= nr < grid.rows and 0 <= nc < grid.cols:
            p = grid.get_piece(nr, nc)
            if p is not None:
                if p.color == attacker_color and p.type in ('rook', 'queen'):
                    return True
                break
            nr += dr
            nc += dc

    # Bispo / Dama (diagonais)
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nr, nc = row + dr, col + dc
        while 0 <= nr < grid.rows and 0 <= nc < grid.cols:
            p = grid.get_piece(nr, nc)
            if p is not None:
                if p.color == attacker_color and p.type in ('bishop', 'queen'):
                    return True
                break
            nr += dr
            nc += dc

    return False


def is_in_check(color, grid):
    king_pos = find_king(color, grid)
    if king_pos is None:
        return False
    return is_square_attacked(king_pos[0], king_pos[1], opponent_of(color), grid)


def _get_raw_moves(piece, grid, last_move):
    """Movimentos pseudo-legais (regra da peça), sem checar se deixa o próprio rei em xeque."""
    moves = []
    r, c = piece.row, piece.col
    color = piece.color

    def enemy(row, col):
        p = grid.get_piece(row, col)
        return p is not None and p.color != color

    def empty(row, col):
        return grid.get_piece(row, col) is None

    def in_bounds(row, col):
        return 0 <= row < grid.rows and 0 <= col < grid.cols

    if piece.type == 'pawn':
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        nr = r + direction

        if in_bounds(nr, c) and empty(nr, c):
            moves.append((nr, c, 'normal'))
            if r == start_row and empty(r + 2 * direction, c):
                moves.append((r + 2 * direction, c, 'double'))

        for dc in (-1, 1):
            nc = c + dc
            if not in_bounds(nr, nc):
                continue
            if enemy(nr, nc):
                moves.append((nr, nc, 'normal'))
            elif empty(nr, nc) and last_move is not None:
                if (last_move['piece_type'] == 'pawn'
                        and last_move['move_type'] == 'double'
                        and last_move['to'] == (r, nc)):
                    moves.append((nr, nc, 'en_passant'))

    elif piece.type == 'knight':
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and (empty(nr, nc) or enemy(nr, nc)):
                moves.append((nr, nc, 'normal'))

    elif piece.type in ('bishop', 'rook', 'queen'):
        directions = []
        if piece.type in ('bishop', 'queen'):
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if piece.type in ('rook', 'queen'):
            directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while in_bounds(nr, nc):
                if empty(nr, nc):
                    moves.append((nr, nc, 'normal'))
                else:
                    if enemy(nr, nc):
                        moves.append((nr, nc, 'normal'))
                    break
                nr += dr
                nc += dc

    elif piece.type == 'king':
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and (empty(nr, nc) or enemy(nr, nc)):
                    moves.append((nr, nc, 'normal'))

        if not piece.has_moved:
            opponent = opponent_of(color)
            # só pode rocar se o rei não estiver em xeque agora
            if not is_square_attacked(r, c, opponent, grid):
                row = r
                rook = grid.get_piece(row, 7)
                if (rook is not None and rook.type == 'rook' and not rook.has_moved
                        and empty(row, 5) and empty(row, 6)
                        and not is_square_attacked(row, 5, opponent, grid)
                        and not is_square_attacked(row, 6, opponent, grid)):
                    moves.append((row, 6, 'castle_king'))

                rook = grid.get_piece(row, 0)
                if (rook is not None and rook.type == 'rook' and not rook.has_moved
                        and empty(row, 1) and empty(row, 2) and empty(row, 3)
                        and not is_square_attacked(row, 2, opponent, grid)
                        and not is_square_attacked(row, 3, opponent, grid)):
                    moves.append((row, 2, 'castle_queen'))

    return moves


def _simulate_move_and_check(piece, r, c, move_type, grid):
    """Aplica o movimento temporariamente no tabuleiro, verifica se o próprio rei
    fica em xeque, e desfaz tudo em seguida. Retorna True se o movimento é seguro."""
    color = piece.color
    old_r, old_c = piece.row, piece.col
    captured = grid.cells[r][c].piece

    ep_row, ep_col, captured_ep = None, None, None
    if move_type == 'en_passant':
        ep_row, ep_col = old_r, c
        captured_ep = grid.cells[ep_row][ep_col].piece
        grid.cells[ep_row][ep_col].piece = None

    grid.cells[old_r][old_c].piece = None
    grid.cells[r][c].piece = piece
    piece.row, piece.col = r, c

    king_pos = find_king(color, grid)
    safe = not is_square_attacked(king_pos[0], king_pos[1], opponent_of(color), grid)

    # desfaz a simulação
    piece.row, piece.col = old_r, old_c
    grid.cells[old_r][old_c].piece = piece
    grid.cells[r][c].piece = captured
    if move_type == 'en_passant':
        grid.cells[ep_row][ep_col].piece = captured_ep

    return safe


def get_valid_moves(piece, grid, last_move):
    """Movimentos realmente legais: respeita a regra da peça E não deixa o próprio rei em xeque."""
    raw_moves = _get_raw_moves(piece, grid, last_move)
    legal_moves = []
    for r, c, move_type in raw_moves:
        if _simulate_move_and_check(piece, r, c, move_type, grid):
            legal_moves.append((r, c, move_type))
    return legal_moves


def is_checkmate(color, grid, last_move):
    if not is_in_check(color, grid):
        return False
    for piece in get_all_pieces(grid, color):
        if get_valid_moves(piece, grid, last_move):
            return False
    return True


def is_stalemate(color, grid, last_move):
    if is_in_check(color, grid):
        return False
    for piece in get_all_pieces(grid, color):
        if get_valid_moves(piece, grid, last_move):
            return False
    return True
