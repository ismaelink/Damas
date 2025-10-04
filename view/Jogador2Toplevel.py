# view/Jogador2Toplevel.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox


class Jogador2Toplevel(tk.Toplevel):
    """
    Modal para autenticar (ou criar) o Jogador 2.
    Em caso de sucesso, define self.result_user = {'id':..., 'nome':...} e fecha.
    """
    def __init__(self, master, autenticar_controller):
        super().__init__(master)
        self.title("Segundo Jogador")
        self.resizable(False, False)

        # modal
        self.transient(master)
        self.grab_set()

        self._auth = autenticar_controller
        self.result_user = None  # será setado em caso de sucesso

        # ===== UI =====
        frm = tb.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        tb.Label(frm, text="Jogador 2", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 12)
        )

        tb.Label(frm, text="Nome:").grid(row=1, column=0, sticky=E, padx=(0, 8), pady=4)
        self.ent_nome = tb.Entry(frm, width=36)
        self.ent_nome.grid(row=1, column=1, sticky=EW, pady=4)

        tb.Label(frm, text="Senha:").grid(row=2, column=0, sticky=E, padx=(0, 8), pady=4)
        self.ent_senha = tb.Entry(frm, width=36, show="*")
        self.ent_senha.grid(row=2, column=1, sticky=EW, pady=4)

        btnbar = tb.Frame(frm)
        btnbar.grid(row=3, column=0, columnspan=2, pady=(12, 0))

        tb.Button(btnbar, text="Entrar", bootstyle=SUCCESS, command=self._entrar).pack(side=LEFT, padx=(0, 8))
        tb.Button(btnbar, text="Criar conta", bootstyle=INFO, command=self._criar_conta).pack(side=LEFT, padx=(0, 8))
        tb.Button(btnbar, text="Cancelar", bootstyle=SECONDARY, command=self._cancelar).pack(side=LEFT)

        frm.columnconfigure(1, weight=1)

        # bindings
        self.ent_nome.bind("<Return>", lambda _: self._entrar())
        self.ent_senha.bind("<Return>", lambda _: self._entrar())

        # centraliza
        self.update_idletasks()
        w, h = 420, 210
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.ent_nome.focus_set()

    # ===== actions =====
    def _get_inputs(self):
        nome = (self.ent_nome.get() or "").strip()
        senha = (self.ent_senha.get() or "").strip()
        return nome, senha

    def _entrar(self):
        nome, senha = self._get_inputs()
        ok, msg = self._auth.autenticar_jogador2(nome, senha)
        if not ok:
            # mostra a razão, limpa a senha e mantém no modal
            messagebox.showerror("Erro", msg, parent=self)
            self.ent_senha.delete(0, "end")
            if "nome" in msg.lower() or "usuário" in msg.lower():
                self.ent_nome.focus_set()
            else:
                self.ent_senha.focus_set()
            return

        # sucesso -> pega o usuário e fecha
        u2 = self._auth.obter_jogador2_atual()
        if not u2:
            messagebox.showerror("Erro", "Falha ao carregar dados do Jogador 2.", parent=self)
            return

        self.result_user = {"id": u2.get("id"), "nome": u2.get("nome")}
        messagebox.showinfo("Ok", f"Jogador 2 autenticado: {u2.get('nome')}", parent=self)
        self.destroy()

    def _criar_conta(self):
        nome, senha = self._get_inputs()
        ok, msg = self._auth.registrar_e_autenticar_jogador2(nome, senha)
        if not ok:
            # casos típicos: nome já existe, campos vazios, etc.
            messagebox.showerror("Erro", msg, parent=self)
            if "existe" in msg.lower():
                # nome duplicado: sugere tentar "Entrar"
                # mantém os campos preenchidos para o usuário tentar logar
                self.ent_senha.focus_set()
            else:
                self.ent_senha.delete(0, "end")
                self.ent_nome.focus_set()
            return

        u2 = self._auth.obter_jogador2_atual()
        if not u2:
            messagebox.showerror("Erro", "Conta criada, mas não foi possível carregar o Jogador 2.", parent=self)
            return

        self.result_user = {"id": u2.get("id"), "nome": u2.get("nome")}
        messagebox.showinfo("Ok", f"Conta criada e Jogador 2 autenticado: {u2.get('nome')}", parent=self)
        self.destroy()

    def _cancelar(self):
        self.result_user = None
        self.destroy()
