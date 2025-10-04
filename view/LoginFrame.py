import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

class LoginFrame(tb.Frame):
    def __init__(self, master, autenticar_controller, on_login_ok, on_abrir_cadastro):
        super().__init__(master, padding=16)
        self.__autenticar = autenticar_controller
        self.__on_login_ok = on_login_ok
        self.__on_abrir_cadastro = on_abrir_cadastro

        self.frm_form = tb.Frame(self, padding=12)
        self.frm_form.pack(anchor='center', fill='x', expand=True)
        self.frm_form.columnconfigure(1, weight=1)

        tb.Label(self.frm_form, text='Login', font=('Helvetica', 18, 'bold'))\
          .grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tb.Label(self.frm_form, text='Nome:')\
          .grid(row=1, column=0, sticky='e', padx=(0, 8), pady=4)
        self.txte_nome = tb.Entry(self.frm_form)
        self.txte_nome.grid(row=1, column=1, pady=4, sticky='ew')

        tb.Label(self.frm_form, text='Senha:')\
          .grid(row=2, column=0, sticky='e', padx=(0, 8), pady=4)
        self.txte_senha = tb.Entry(self.frm_form, show='*')
        self.txte_senha.grid(row=2, column=1, pady=4, sticky='ew')

        self.btn_entrar = tb.Button(self.frm_form, text='ENTRAR',
                                    bootstyle='primary',
                                    command=self.__entrar)
        self.btn_entrar.grid(row=3, column=0, columnspan=2, pady=(12, 4), sticky='ew')

        self.btn_criar_conta = tb.Button(self.frm_form, text='Criar Conta',
                                         bootstyle='info',
                                         command=self.__abrir_cadastro)
        self.btn_criar_conta.grid(row=4, column=0, columnspan=2, sticky='ew')

        # espaçador para largura “mínima” visual
        tb.Frame(self, width=420, height=6).pack()

        self.txte_senha.bind('<Return>', lambda _: self.__entrar())
        self.txte_nome.focus_set()

    def __entrar(self):
        nome = self.txte_nome.get()
        senha = self.txte_senha.get()
        ok, msg = self.__autenticar.autenticar_usuario(nome, senha)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self); return
        messagebox.showinfo("Sucesso", msg, parent=self)
        self.__on_login_ok(self.__autenticar.obter_usuario_atual())

    def __abrir_cadastro(self):
        self.__on_abrir_cadastro()
