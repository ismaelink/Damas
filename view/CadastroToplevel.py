import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

class CadastroToplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller):
        super().__init__(master)
        self.title("Criar Conta")
        self.transient(master); self.grab_set()
        self.resizable(False, False)
        self.__autenticar = autenticar_controller

        frm = tb.Frame(self, padding=16); frm.pack(fill='both', expand=True)
        tb.Label(frm, text='Criar Conta', font=('Helvetica', 16, 'bold'))\
          .grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tb.Label(frm, text='Nome:').grid(row=1, column=0, sticky='e', padx=(0,8), pady=4)
        self.txte_nome = tb.Entry(frm); self.txte_nome.grid(row=1, column=1, sticky='ew', pady=4)

        tb.Label(frm, text='Senha:').grid(row=2, column=0, sticky='e', padx=(0,8), pady=4)
        self.txte_senha = tb.Entry(frm, show='*'); self.txte_senha.grid(row=2, column=1, sticky='ew', pady=4)

        tb.Label(frm, text='Confirmar Senha:').grid(row=3, column=0, sticky='e', padx=(0,8), pady=4)
        self.txte_confirma = tb.Entry(frm, show='*'); self.txte_confirma.grid(row=3, column=1, sticky='ew', pady=4)

        bar = tb.Frame(frm); bar.grid(row=4, column=0, columnspan=2, pady=(12,0), sticky='e')
        tb.Button(bar, text='Cancelar', bootstyle='secondary', command=self.destroy).pack(side='left', padx=(0,8))
        tb.Button(bar, text='Cadastrar', bootstyle='success', command=self.__cadastrar).pack(side='left')

        frm.columnconfigure(1, weight=1)
        self.txte_confirma.bind('<Return>', lambda _: self.__cadastrar())
        self.txte_nome.focus_set()

    def __cadastrar(self):
        nome = self.txte_nome.get()
        senha = self.txte_senha.get()
        conf  = self.txte_confirma.get()
        if senha != conf:
            messagebox.showerror("Erro", "As senhas não conferem.", parent=self); return
        ok, msg = self.__autenticar.registrar_usuario(nome, senha)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self); return
        messagebox.showinfo("Sucesso", msg, parent=self)
        self.destroy()
