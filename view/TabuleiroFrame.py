# view/TabuleiroFrame.py
import time
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from model.jogo_damas import Game, Board, MinimaxAI

class TabuleiroFrame(tb.Frame):
    def __init__(self, master, partida, on_finalizar=None):
        super().__init__(master, padding=10)
        self.partida = partida
        self.on_finalizar = on_finalizar or (lambda r: None)

        self.game = Game()
        if partida.quem_comeca == 'pretas':
            self.game.current = 'black'

        self.ai = MinimaxAI(level=partida.dificuldade_ia)
        self.buttons = {}
        self.base_style = {}
        self.highlight_moves = {}
        self.selected = None

        # contadores / tempo de partida
        self._turnos = 0               # conta turnos (human+IA)
        self._t0 = time.time()         # início da partida
        self._encerrada = False        # trava cliques após o fim

        # estilo só para as casas do tabuleiro (não afeta o botão "Encerrar Partida")
        self._style = tb.Style()
        self.piece_font = ("Segoe UI Emoji", 20, "bold")  # ou "Segoe UI Symbol"/"Noto Color Emoji"
        self._style.configure('Casa.TButton', font=self.piece_font)

        self._build_ui()
        self._refresh_board()
        self._status_turno()

        if self.game.current == 'black':
            # pretas começam -> IA joga de cara
            self.after(1, self._ai_play)

    # ---------- UI ----------
    def _build_ui(self):
        top = tb.Frame(self); top.pack(anchor='w', pady=(0,8), fill='x')
        self.lbl_status = tb.Label(top, text="", font=("Segoe UI", 12, "bold"))
        self.lbl_status.pack(side=LEFT)

        tb.Button(top, text="Encerrar Partida",
                  bootstyle=SECONDARY, command=self._encerrar).pack(side=RIGHT, padx=10)

        board = tb.Frame(self); board.pack()

        lbl_font = ("Segoe UI", 11, "bold")
        tb.Label(board, text="").grid(row=0, column=0)
        for c in range(8):
            tb.Label(board, text=chr(ord('A') + c), font=lbl_font).grid(row=0, column=c+1, pady=2)
        tb.Label(board, text="").grid(row=0, column=9)

        for r in range(8):
            tb.Label(board, text=str(r+1), font=lbl_font).grid(row=r+1, column=0, padx=2)
            for c in range(8):
                btn = tb.Button(
                    board,
                    text="",
                    width=4,
                    style='Casa.TButton',
                    bootstyle=("dark" if Board.is_dark_square(r, c) else "secondary"),
                    command=lambda rr=r, cc=c: self._on_square_click(rr, cc)
                )
                btn.grid(row=r+1, column=c+1, ipadx=6, ipady=8, padx=1, pady=1)
                self.buttons[(r, c)] = btn
                self.base_style[(r, c)] = "dark" if Board.is_dark_square(r, c) else "secondary"
            tb.Label(board, text=str(r+1), font=lbl_font).grid(row=r+1, column=9, padx=2)

        tb.Label(board, text="").grid(row=9, column=0)
        for c in range(8):
            tb.Label(board, text=chr(ord('A') + c), font=lbl_font).grid(row=9, column=c+1, pady=2)
        tb.Label(board, text="").grid(row=9, column=9)

    def _status_turno(self, extra=""):
        msg = "Sua vez (BRANCAS ⛀)." if self.game.current == 'white' else "Vez da IA (PRETAS ⛂)…"
        self.lbl_status.configure(text=(msg + (" " + extra if extra else "")))

    def _encerrar(self):
        if self._encerrada:
            return
        self._encerrada = True
        payload = {
            "resultado": "encerrada",
            "movimentos": self._turnos,
            "duracao_segundos": int(time.time() - self._t0),
        }
        self.on_finalizar(payload)

    def _coord_label(self, r, c):
        return f"{chr(ord('A')+c)}{r+1}"

    def _glyph(self, piece):
        # homens: ⚪/⚫ — damas: ⛁/⛃
        if piece.color == 'white':
            return '⛁' if piece.king else '⚪'
        else:
            return '⛃' if piece.king else '⚫'

    # ---------- Interação ----------
    def _on_square_click(self, r, c):
        if self._encerrada:
            return
        if self.game.current != 'white':
            return

        # destino válido?
        if (r, c) in self.highlight_moves and self.selected is not None:
            fr, fc = self.selected
            captures = self.highlight_moves[(r, c)]
            info = self.game.move(fr, fc, r, c, captures)
            self.selected = (r, c) if info['continued'] else None
            self.highlight_moves.clear()
            self._refresh_board()

            # se finalizou a jogada do humano (não tem continuidade), conta 1 turno
            if not info['continued']:
                self._turnos += 1

            if self._check_game_over():
                return

            if info['continued']:
                self._status_turno("Continue a capturar com a mesma peça.")
                self._select_square(r, c)
            else:
                if self.game.current == 'black':
                    self._status_turno()
                    self._ai_play()  # IA joga já
                else:
                    self._status_turno()
            return

        # seleção de peça
        piece = self.game.board.get_piece(r, c)
        if self.game.forced_piece is not None and (r, c) != self.game.forced_piece:
            self._status_turno("Você deve continuar com a mesma peça.")
            return
        if piece is None or piece.color != 'white':
            return
        self._select_square(r, c)

    def _ai_play(self):
        if self._encerrada:
            return
        seq = self.ai.choose(self.game)
        if not seq:
            # IA sem movimentos -> vitória das brancas
            self._finalizar_com_vencedor('white')
            return

        for fr, fc, tr, tc, caps in seq:
            self.game.move(fr, fc, tr, tc, caps)

        # a IA completou o turno dela
        if self.game.current == 'white':
            self._turnos += 1

        self.selected = None
        self.highlight_moves.clear()
        self._refresh_board()

        if self._check_game_over():
            return

        self._status_turno()
        if self.game.current == 'black':
            # cadeia longa iniciada pela IA
            self.after(60, self._ai_play)

    def _select_square(self, r, c):
        self.selected = (r, c)
        self.highlight_moves = self.game.valid_moves_for_piece(r, c)
        self._refresh_board()
        self._status_turno(f"Selecione destino para {self._coord_label(r,c)}.")

    def _refresh_board(self):
        for (r, c), btn in self.buttons.items():
            piece = self.game.board.get_piece(r, c)
            btn.configure(text=self._glyph(piece) if piece else "")
            btn.configure(bootstyle=self.base_style[(r, c)])

        if self.selected is not None:
            sr, sc = self.selected
            self.buttons[(sr, sc)].configure(bootstyle="warning")

        for (dr, dc) in self.highlight_moves.keys():
            self.buttons[(dr, dc)].configure(bootstyle="info")

    # ---------- Helpers locais de fim de jogo ----------
    def _count_pieces(self, color: str) -> int:
        n = 0
        for r in range(8):
            for c in range(8):
                p = self.game.board.get_piece(r, c)
                if p and p.color == color:
                    n += 1
        return n

    def _has_any_move(self, color: str) -> bool:
        old_current, old_forced = self.game.current, self.game.forced_piece
        self.game.current, self.game.forced_piece = color, None
        ok = False
        for r in range(8):
            for c in range(8):
                p = self.game.board.get_piece(r, c)
                if p and p.color == color and self.game.valid_moves_for_piece(r, c):
                    ok = True
                    break
            if ok:
                break
        self.game.current, self.game.forced_piece = old_current, old_forced
        return ok

    def _winner_if_any(self):
        # sem peças
        if self._count_pieces('white') == 0:
            return 'black'
        if self._count_pieces('black') == 0:
            return 'white'
        # sem movimentos para quem está de turno -> oponente vence
        if not self._has_any_move(self.game.current):
            return 'white' if self.game.current == 'black' else 'black'
        return None

    # ---------- Fim de jogo ----------
    def _check_game_over(self) -> bool:
        winner = self._winner_if_any()
        if not winner:
            return False
        self._finalizar_com_vencedor(winner)
        return True

    def _finalizar_com_vencedor(self, winner: str):
        if self._encerrada:
            return
        self._encerrada = True

        msg = "Você ganhou!" if winner == 'white' else "Você perdeu."
        messagebox.showinfo("Fim de Jogo", msg, parent=self)

        # desabilita cliques
        for btn in self.buttons.values():
            btn.configure(state=DISABLED)

        payload = {
            "resultado": "vitoria" if winner == 'white' else "derrota",
            "movimentos": self._turnos,
            "duracao_segundos": int(time.time() - self._t0),
        }
        # volta para tela principal (ou salva e volta, a JanelaPrincipal cuida disso)
        self.after(150, lambda: self.on_finalizar(payload))
