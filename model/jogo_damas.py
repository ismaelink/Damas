# model/jogo_damas.py
import math

class Piece:
    def __init__(self, color, king=False):
        self.color = color
        self.king = king

    @property
    def symbol(self):
        if self.color == 'white':
            return '⛁' if self.king else '⛀'
        else:
            return '⛃' if self.king else '⛂'


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial()

    @staticmethod
    def in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8
    @staticmethod
    def is_dark_square(r, c): return (r + c) % 2 == 1
    def get_piece(self, r, c): return self.grid[r][c]
    def set_piece(self, r, c, piece): self.grid[r][c] = piece
    def remove_piece(self, r, c): self.grid[r][c] = None

    def setup_initial(self):
        for r in range(8):
            for c in range(8):
                self.grid[r][c] = None
        for r in range(3):
            for c in range(8):
                if Board.is_dark_square(r, c):
                    self.grid[r][c] = Piece('black')
        for r in range(5, 8):
            for c in range(8):
                if Board.is_dark_square(r, c):
                    self.grid[r][c] = Piece('white')


class Game:
    def __init__(self):
        self.board = Board()
        self.current = 'white'    # brancas começam
        self.forced_piece = None  # (r,c) quando no meio de cadeia

    def clone(self):
        g = Game()
        g.current = self.current
        g.forced_piece = None if self.forced_piece is None else (self.forced_piece[0], self.forced_piece[1])
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                g.board.set_piece(r, c, None if p is None else Piece(p.color, p.king))
        return g

    def reset(self):
        self.board.setup_initial()
        self.current = 'white'
        self.forced_piece = None

    def opponent(self, color): return 'white' if color == 'black' else 'black'

    def piece_directions(self, piece):
        return [(-1,-1), (-1,1), (1,-1), (1,1)] if piece.king else (
            [(-1,-1), (-1,1)] if piece.color == 'white' else [(1,-1), (1,1)]
        )

    def valid_moves_for_piece(self, r, c):
        piece = self.board.get_piece(r, c)
        if not piece or piece.color != self.current: return {}
        return self._valid_moves_for_king(r, c) if piece.king else self._valid_moves_for_man(r, c)

    def _valid_moves_for_man(self, r, c):
        piece = self.board.get_piece(r, c)
        fwd_dirs = self.piece_directions(piece)
        cap_dirs = [(-1,-1), (-1,1), (1,-1), (1,1)]
        captures, moves = {}, {}

        for dr, dc in fwd_dirs:
            nr, nc = r+dr, c+dc
            if self.board.in_bounds(nr, nc) and self.board.get_piece(nr, nc) is None:
                moves[(nr, nc)] = []

        for dr, dc in cap_dirs:
            er, ec = r+dr, c+dc
            jr, jc = r+2*dr, c+2*dc
            if (self.board.in_bounds(er, ec) and self.board.in_bounds(jr, jc)
                and (q := self.board.get_piece(er, ec)) is not None
                and q.color == self.opponent(piece.color)
                and self.board.get_piece(jr, jc) is None):
                captures[(jr, jc)] = [(er, ec)]

        return captures if self.forced_piece is not None else {**moves, **captures}

    def _valid_moves_for_king(self, r, c):
        piece = self.board.get_piece(r, c)
        captures, moves = {}, {}
        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            step = 1
            while True:
                nr, nc = r+step*dr, c+step*dc
                if not self.board.in_bounds(nr, nc): break
                cur = self.board.get_piece(nr, nc)
                if cur is None:
                    if self.forced_piece is None:
                        moves[(nr, nc)] = []
                    step += 1; continue
                if cur.color == piece.color: break
                jr, jc = nr+dr, nc+dc
                if self.board.in_bounds(jr, jc) and self.board.get_piece(jr, jc) is None:
                    captures[(jr, jc)] = [(nr, nc)]
                break
        return captures if self.forced_piece is not None else {**moves, **captures}

    def _has_capture_from(self, r, c):
        p = self.board.get_piece(r, c)
        if not p: return False
        if not p.king:
            for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                er, ec = r+dr, c+dc; jr, jc = r+2*dr, c+2*dc
                if (self.board.in_bounds(er, ec) and self.board.in_bounds(jr, jc)
                    and (q := self.board.get_piece(er, ec)) is not None
                    and q.color == self.opponent(p.color)
                    and self.board.get_piece(jr, jc) is None):
                    return True
            return False
        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            step = 1
            while True:
                nr, nc = r+step*dr, c+step*dc
                if not self.board.in_bounds(nr, nc): break
                cur = self.board.get_piece(nr, nc)
                if cur is None: step += 1; continue
                if cur.color == p.color: break
                jr, jc = nr+dr, nc+dc
                if self.board.in_bounds(jr, jc) and self.board.get_piece(jr, jc) is None:
                    return True
                break
        return False

    def move(self, fr, fc, tr, tc, captured_list):
        piece = self.board.get_piece(fr, fc)
        self.board.set_piece(tr, tc, piece)
        self.board.remove_piece(fr, fc)
        for cr, cc in captured_list:
            self.board.remove_piece(cr, cc)

        promoted = False
        if (piece.color == 'white' and tr == 0 and not piece.king) or (piece.color == 'black' and tr == 7 and not piece.king):
            piece.king = True; promoted = True

        if captured_list and not promoted and self._has_capture_from(tr, tc):
            self.forced_piece = (tr, tc)
            return {'continued': True, 'switched': False, 'promoted': promoted}
        self.forced_piece = None
        self.current = self.opponent(self.current)
        return {'continued': False, 'switched': True, 'promoted': promoted}


class MinimaxAI:
    def __init__(self, level='medium'):
        depths = {'easy': 2, 'medium': 4, 'hard': 6}
        self.depth = depths.get(level, 4)
        self.ai_color = 'black'

    def choose(self, game):
        best_score, best_seq = self._minimax(game.clone(), self.depth, -math.inf, math.inf)
        return best_seq or []

    def _minimax(self, game, depth, alpha, beta):
        terminal, score = self._is_terminal(game, depth)
        if terminal: return score, None

        is_max = (game.current == self.ai_color)
        sequences = self._all_turn_sequences(game, game.current)
        if not sequences: return (self._eval(game), None)

        best_seq = None
        if is_max:
            best_val = -math.inf
            for seq in sequences:
                child = game.clone(); self._apply_sequence(child, seq)
                val, _ = self._minimax(child, depth-1, alpha, beta)
                if val > best_val: best_val, best_seq = val, seq
                alpha = max(alpha, val)
                if beta <= alpha: break
            return best_val, best_seq
        else:
            best_val = math.inf
            for seq in sequences:
                child = game.clone(); self._apply_sequence(child, seq)
                val, _ = self._minimax(child, depth-1, alpha, beta)
                if val < best_val: best_val, best_seq = val, seq
                beta = min(beta, val)
                if beta <= alpha: break
            return best_val, best_seq

    def _is_terminal(self, game, depth):
        if depth <= 0: return True, self._eval(game)
        if not self._has_any_move(game, game.current): return True, self._eval(game)
        return False, 0

    def _apply_sequence(self, game, seq):
        for fr, fc, tr, tc, caps in seq:
            game.move(fr, fc, tr, tc, caps)

    def _has_any_move(self, game, color):
        old_current, old_forced = game.current, game.forced_piece
        game.current, game.forced_piece = color, None
        ok = any(
            (p and p.color == color and game.valid_moves_for_piece(r, c))
            for r in range(8) for c in range(8)
            for p in [game.board.get_piece(r, c)]
        )
        game.current, game.forced_piece = old_current, old_forced
        return ok

    def _all_turn_sequences(self, game, color):
        old_current, old_forced = game.current, game.forced_piece
        game.current, game.forced_piece = color, None
        sequences = []
        for r in range(8):
            for c in range(8):
                p = game.board.get_piece(r, c)
                if not p or p.color != color: continue
                moves = game.valid_moves_for_piece(r, c)
                for (tr, tc), caps in moves.items():
                    g2 = game.clone()
                    g2.current, g2.forced_piece = color, None
                    info = g2.move(r, c, tr, tc, caps)
                    seq = [(r, c, tr, tc, caps)]
                    if info['continued']:
                        sequences.extend(self._continue_chain(g2, seq))
                    else:
                        sequences.append(seq)
        game.current, game.forced_piece = old_current, old_forced
        return sequences

    def _continue_chain(self, game, seq_so_far):
        fr, fc = game.forced_piece
        sequences, moves = [], game.valid_moves_for_piece(fr, fc)
        extended = False
        for (tr, tc), caps in moves.items():
            g2 = game.clone()
            info = g2.move(fr, fc, tr, tc, caps)
            new_seq = seq_so_far + [(fr, fc, tr, tc, caps)]
            if info['continued']: sequences.extend(self._continue_chain(g2, new_seq))
            else: sequences.append(new_seq)
            extended = True
        if not extended: sequences.append(seq_so_far)
        return sequences

    def _eval(self, game):
        blacks = whites = b_kings = w_kings = 0
        for r in range(8):
            for c in range(8):
                p = game.board.get_piece(r, c)
                if not p: continue
                if p.color == 'black':
                    blacks += 1; b_kings += int(p.king)
                else:
                    whites += 1; w_kings += int(p.king)
        material = 100*(blacks - whites) + 75*(b_kings - w_kings)
        mob_b = self._mobility(game, 'black')
        mob_w = self._mobility(game, 'white')
        return material + 0.1*(mob_b - mob_w)

    def _mobility(self, game, color):
        old_current, old_forced = game.current, game.forced_piece
        game.current, game.forced_piece = color, None
        count = sum(len(game.valid_moves_for_piece(r, c)) 
                    for r in range(8) for c in range(8)
                    if (p:=game.board.get_piece(r, c)) and p.color == color)
        game.current, game.forced_piece = old_current, old_forced
        return count
    
        # --- utilitários para detecção de fim de partida ---
    def count_pieces(self, color: str) -> int:
        """Conta quantas peças de 'color' existem no tabuleiro."""
        n = 0
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p and p.color == color:
                    n += 1
        return n

    def has_any_move(self, color: str) -> bool:
        """Retorna True se 'color' tem ao menos um movimento válido."""
        old_current, old_forced = self.current, self.forced_piece
        self.current, self.forced_piece = color, None
        ok = False
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p and p.color == color and self.valid_moves_for_piece(r, c):
                    ok = True
                    break
            if ok:
                break
        self.current, self.forced_piece = old_current, old_forced
        return ok

    def winner_if_any(self):
        """
        Retorna 'white' se brancas venceram, 'black' se pretas venceram,
        ou None se a partida continua. Critérios:
        - um dos lados não tem peças; ou
        - lado a jogar não tem movimentos.
        """
        if self.count_pieces('white') == 0:
            return 'black'
        if self.count_pieces('black') == 0:
            return 'white'
        if not self.has_any_move(self.current):
            # sem movimentos para quem está de turno -> oponente vence
            return self.opponent(self.current)
        return None

