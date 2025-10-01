import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

class CadastroToplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller):
        super().__init__(master)
        self.title("Criar Conta")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)

        self.__autenticar = autenticar_controller

        self.frm_corpo = tb.Frame(self, padding=16)
        self.frm_corpo.pack(fill='both', expand=True)

        self.lbl_titulo = tb.Label(self.frm_corpo, text='Criar Conta', font=('Helvetica', 16, 'bold'))
        self.lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 12))

        self.lbl_nome = tb.Label(self.frm_corpo, text='Nome:')
        self.lbl_nome.grid(row=1, column=0, sticky='e', padx=(0, 8), pady=4)

        self.txte_nome = tb.Entry(self.frm_corpo, width=48)
        self.txte_nome.grid(row=1, column=1, pady=4, sticky='ew')

        self.lbl_senha = tb.Label(self.frm_corpo, text='Senha:')
        self.lbl_senha.grid(row=2, column=0, sticky='e', padx=(0, 8), pady=4)

        self.txte_senha = tb.Entry(self.frm_corpo, width=48, show='*')
        self.txte_senha.grid(row=2, column=1, pady=4, sticky='ew')

        self.lbl_confirma = tb.Label(self.frm_corpo, text='Confirmar Senha:')
        self.lbl_confirma.grid(row=3, column=0, sticky='e', padx=(0, 8), pady=4)

        self.txte_confirma = tb.Entry(self.frm_corpo, width=48, show='*')
        self.txte_confirma.grid(row=3, column=1, pady=4, sticky='ew')

        self.frm_botoes = tb.Frame(self.frm_corpo)
        self.frm_botoes.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky='ew')

        self.btn_sair = tb.Button(self.frm_botoes, text='SAIR', bootstyle='secondary', command=self.__sair)
        self.btn_sair.pack(side='left', padx=(0, 8))

        self.btn_cadastrar = tb.Button(self.frm_botoes, text='CADASTRAR', command=self.__cadastrar)
        self.btn_cadastrar.pack(side='left')

        self.txte_confirma.bind('<Return>', lambda _: self.__cadastrar())
        self.txte_nome.focus_set()

    def __cadastrar(self):
        nome = self.txte_nome.get()
        senha = self.txte_senha.get()
        confirma = self.txte_confirma.get()

        if senha != confirma:
            messagebox.showerror("Erro", "As senhas não conferem.", parent=self)
            self.txte_confirma.delete(0, 'end')
            self.txte_confirma.focus_set()
            return

        ok, msg = self.__autenticar.registrar_usuario(nome, senha)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self)
            return

        messagebox.showinfo("Sucesso", msg, parent=self)
        self.destroy()

    def __sair(self):
        self.destroy()

