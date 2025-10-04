import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

class AlterarDadosToplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller, on_sucesso=None):
        super().__init__(master)
        self.title("Alterar Dados")
        self.__autenticar = autenticar_controller
        self.__on_sucesso = on_sucesso or (lambda: None)

        self.transient(master); self.grab_set()
        self.resizable(False, False)

        frm = tb.Frame(self, padding=16); frm.pack(fill='both', expand=True)
        tb.Label(frm, text='Alterar Dados', font=('Helvetica', 16, 'bold'))\
          .grid(row=0, column=0, columnspan=2, pady=(0,12))

        tb.Label(frm, text='Novo nome:').grid(row=1, column=0, sticky='e', padx=(0,8), pady=4)
        self.txte_nome = tb.Entry(frm); self.txte_nome.grid(row=1, column=1, sticky='ew', pady=4)

        tb.Label(frm, text='Nova senha:').grid(row=2, column=0, sticky='e', padx=(0,8), pady=4)
        self.txte_senha = tb.Entry(frm, show='*'); self.txte_senha.grid(row=2, column=1, sticky='ew', pady=4)

        tb.Label(frm, text='Confirmar nova senha:').grid(row=3, column=0, sticky='e', padx=(0,8), pady=4)
        self.txte_conf = tb.Entry(frm, show='*'); self.txte_conf.grid(row=3, column=1, sticky='ew', pady=4)

        bar = tb.Frame(frm); bar.grid(row=4, column=0, columnspan=2, pady=(12,0), sticky='e')
        tb.Button(bar, text='Cancelar', bootstyle='secondary', command=self.destroy).pack(side='left', padx=(0,8))
        tb.Button(bar, text='Salvar alterações', bootstyle='primary', command=self.__salvar).pack(side='left')

        frm.columnconfigure(1, weight=1)
        u = self.__autenticar.obter_usuario_atual()
        self.txte_nome.insert(0, u['nome'] if u else '')
        self.txte_conf.bind('<Return>', lambda _: self.__salvar())
        self.txte_nome.focus_set()

    def __salvar(self):
        novo_nome = self.txte_nome.get()
        nova_senha = self.txte_senha.get()
        conf = self.txte_conf.get()

        if not novo_nome.strip():
            messagebox.showerror("Erro", "O campo Nome está vazio.", parent=self); return

        if (nova_senha.strip() or conf.strip()):
            if not nova_senha.strip() or not conf.strip():
                messagebox.showerror("Erro", "Preencha os dois campos de senha.", parent=self); return
            if nova_senha != conf:
                messagebox.showerror("Erro", "As senhas não conferem.", parent=self); return
            senha_para_enviar = nova_senha
        else:
            senha_para_enviar = None

        ok, msg = self.__autenticar.alterar_dados_usuario(novo_nome, senha_para_enviar)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self); return

        messagebox.showinfo("Sucesso", msg, parent=self)
        self.__on_sucesso()
        self.destroy()
