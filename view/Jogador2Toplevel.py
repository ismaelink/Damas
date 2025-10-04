# view/Jogador2Toplevel.py
import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox

class Jogador2Toplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller, on_ok=None):
        super().__init__(master)
        self.title("Segundo Jogador")
        self.transient(master); self.grab_set()
        self.resizable(False, False)

        self._aut = autenticar_controller
        self._on_ok = on_ok or (lambda user2: None)

        frm = tb.Frame(self, padding=16); frm.pack(fill='both', expand=True)
        tb.Label(frm, text="Jogador 2", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,12))

        tb.Label(frm, text="Nome:").grid(row=1, column=0, sticky='e', padx=(0,8), pady=4)
        self.e_nome = tb.Entry(frm, width=32); self.e_nome.grid(row=1, column=1, sticky='w', pady=4)

        tb.Label(frm, text="Senha:").grid(row=2, column=0, sticky='e', padx=(0,8), pady=4)
        self.e_senha = tb.Entry(frm, show='*', width=32); self.e_senha.grid(row=2, column=1, sticky='w', pady=4)

        bar = tb.Frame(frm); bar.grid(row=3, column=0, columnspan=2, pady=(12,0))
        tb.Button(bar, text="Entrar",     bootstyle='success',   command=self._entrar).pack(side='left', padx=4)
        tb.Button(bar, text="Criar conta",bootstyle='info',      command=self._criar).pack(side='left', padx=4)
        tb.Button(bar, text="Cancelar",   bootstyle='secondary', command=self.destroy).pack(side='left', padx=4)

        self.e_nome.focus_set()
        self.e_senha.bind('<Return>', lambda _: self._entrar())

    def _entrar(self):
        n = self.e_nome.get().strip()
        s = self.e_senha.get().strip()
        ok, msg = self._aut.autenticar_jogador2(n, s)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self); return
        self._on_ok(self._aut.obter_jogador2_atual())
        self.destroy()

    def _criar(self):
        n = self.e_nome.get().strip()
        s = self.e_senha.get().strip()
        if not n or not s:
            messagebox.showerror("Erro", "Preencha nome e senha.", parent=self); return
        ok, msg = self._aut.registrar_e_autenticar_jogador2(n, s)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self); return
        self._on_ok(self._aut.obter_jogador2_atual())
        self.destroy()
