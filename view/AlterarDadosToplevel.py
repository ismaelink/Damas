import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

class AlterarDadosToplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller, on_sucesso=None):
        super().__init__(master)
        self.title("Alterar Dados")
        self.__autenticar = autenticar_controller
        self.__on_sucesso = on_sucesso or (lambda: None)

        # modal
        self.transient(master)
        self.grab_set()

        largura = self.winfo_screenwidth()
        altura  = self.winfo_screenheight()
        self.geometry(f"{largura}x{altura}+0+0")

        self.frm_corpo = tb.Frame(self, padding=24)
        self.frm_corpo.pack(fill='both', expand=True)

        self.lbl_titulo = tb.Label(self.frm_corpo, text='Alterar Dados', font=('Helvetica', 20, 'bold'))
        self.lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 18))

        self.frm_corpo.columnconfigure(1, weight=1)

        self.lbl_nome = tb.Label(self.frm_corpo, text='Novo nome:')
        self.lbl_nome.grid(row=1, column=0, sticky='e', padx=(0, 12), pady=6)

        self.txte_nome = tb.Entry(self.frm_corpo, width=56)
        self.txte_nome.grid(row=1, column=1, sticky='ew', pady=6)

        self.lbl_senha = tb.Label(self.frm_corpo, text='Nova senha:')
        self.lbl_senha.grid(row=2, column=0, sticky='e', padx=(0, 12), pady=6)

        self.txte_senha = tb.Entry(self.frm_corpo, width=56, show='*')
        self.txte_senha.grid(row=2, column=1, sticky='ew', pady=6)

        self.lbl_conf = tb.Label(self.frm_corpo, text='Confirmar nova senha:')
        self.lbl_conf.grid(row=3, column=0, sticky='e', padx=(0, 12), pady=6)

        self.txte_conf = tb.Entry(self.frm_corpo, width=56, show='*')
        self.txte_conf.grid(row=3, column=1, sticky='ew', pady=6)

        self.frm_botoes = tb.Frame(self.frm_corpo, padding=(0, 12))
        self.frm_botoes.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(12, 0))

        self.btn_cancelar = tb.Button(self.frm_botoes, text='CANCELAR', bootstyle='secondary', command=self.__cancelar)
        self.btn_cancelar.pack(side='left', padx=(0, 12))

        self.btn_salvar = tb.Button(self.frm_botoes, text='SALVAR ALTERAÇÕES', command=self.__salvar)
        self.btn_salvar.pack(side='left')

        u = self.__autenticar.obter_usuario_atual()
        self.txte_nome.insert(0, u['nome'] if u else '')

        self.txte_conf.bind('<Return>', lambda _: self.__salvar())
        self.txte_nome.focus_set()

    def __cancelar(self):
        self.destroy()

    def __salvar(self):
        novo_nome = self.txte_nome.get()
        nova_senha = self.txte_senha.get()
        confirma   = self.txte_conf.get()

        if not novo_nome or not novo_nome.strip():
            messagebox.showerror("Erro", "O campo Nome está vazio.", parent=self)
            self.txte_nome.focus_set()
            return

        algum_preenchido = (nova_senha.strip() != "" or confirma.strip() != "")
        if algum_preenchido:
            if nova_senha.strip() == "" or confirma.strip() == "":
                messagebox.showerror("Erro", "Preencha os dois campos de senha.", parent=self)
                return
            if nova_senha != confirma:
                messagebox.showerror("Erro", "As senhas não conferem.", parent=self)
                self.txte_conf.delete(0, 'end')
                self.txte_conf.focus_set()
                return

        senha_para_enviar = nova_senha if algum_preenchido else None
        ok, msg = self.__autenticar.alterar_dados_usuario(novo_nome, senha_para_enviar)
        if not ok:
            messagebox.showerror("Erro", msg, parent=self)
            return

        messagebox.showinfo("Sucesso", msg, parent=self)
        self.__on_sucesso()
        self.destroy()

