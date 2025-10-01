import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

from controller.AutenticarController import AutenticarController
from model.UsuarioDAO import UsuarioDAO
from view.LoginFrame import LoginFrame
from view.CadastroToplevel import CadastroToplevel
from view.AlterarDadosToplevel import AlterarDadosToplevel


class JanelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        tb.Style('flatly')

        self.title('Jogo de Damas')
        self.__maximizar()

        self.__dao = UsuarioDAO()
        self.__autenticar = AutenticarController(self.__dao)
        self.__usuario_atual = None

        self.mn_barra = tk.Menu(self)
        self.config(menu=self.mn_barra)

        # usuário
        self.mn_usuario = tk.Menu(self.mn_barra, tearoff=0)
        self.mn_usuario.add_command(label='Login', command=self.__mostrar_login)
        self.mn_usuario.add_command(label='Criar Conta', command=self.__abrir_cadastro)
        self.mn_usuario.add_separator()
        self.mn_usuario.add_command(label='Logout', command=self.__logout)
        self.mn_barra.add_cascade(label='Usuário', menu=self.mn_usuario)

        # acoes, alterar mais tarde
        self.mn_acoes = tk.Menu(self.mn_barra, tearoff=0)
        self.mn_acoes.add_command(label='Iniciar Partida', command=self.__acao_iniciar_partida)
        self.mn_acoes.add_command(label='Estatísticas/Histórico', command=self.__acao_estatisticas)
        self.mn_acoes.add_command(label='Alterar Tema do Tabuleiro', command=self.__acao_alterar_tema)
        self.mn_acoes.add_command(label='Alterar Dados', command=self.__acao_alterar_dados)
        self.mn_barra.add_cascade(label='Ações', menu=self.mn_acoes)

        self.frm_corpo = tb.Frame(self, padding=16)
        self.frm_corpo.pack(fill='both', expand=True)

        self.__atualizar_menu_por_estado()
        self.__mostrar_login()

    def __maximizar(self):
        try:
            self.state('zoomed')
        except tk.TclError:
            try:
                self.attributes('-zoomed', True)
            except tk.TclError:
                largura = self.winfo_screenwidth()
                altura = self.winfo_screenheight()
                self.geometry(f'{largura}x{altura}+0+0')

    def __limpar_corpo(self):
        for w in self.frm_corpo.winfo_children():
            w.destroy()

    def __mostrar_login(self):
        self.__limpar_corpo()
        self.frm_login = LoginFrame(
            self.frm_corpo,
            autenticar_controller=self.__autenticar,
            on_login_ok=self.__apos_login,
            on_abrir_cadastro=self.__abrir_cadastro
        )
        self.frm_login.pack(expand=True)

    def __mostrar_tela_principal(self):
        self.__limpar_corpo()
        self.lbl_titulo = tb.Label(self.frm_corpo, text='Tela Principal', font=('Helvetica', 18, 'bold'))
        self.lbl_titulo.pack(anchor='center', pady=8)

        nome = self.__usuario_atual['nome'] if self.__usuario_atual else '—'
        self.lbl_bemvindo = tb.Label(self.frm_corpo, text=f'Bem-vindo, {nome}!')
        self.lbl_bemvindo.pack(anchor='center')

    def __abrir_cadastro(self):
        CadastroToplevel(self, autenticar_controller=self.__autenticar)

    def __apos_login(self, usuario_atual):
        self.__usuario_atual = usuario_atual
        self.__atualizar_menu_por_estado()
        self.__mostrar_tela_principal()

    def __logout(self):
        if not self.__usuario_atual:
            return
        if not messagebox.askyesno("Confirmar", "Deseja sair da conta?", parent=self):
            return
        self.__autenticar.deslogar()
        self.__usuario_atual = None
        messagebox.showinfo("Sessão encerrada", "Você saiu da conta.", parent=self)
        self.__atualizar_menu_por_estado()
        self.__mostrar_login()

    def __checar_protecao(self):
        ok, msg = self.__autenticar.exigir_login()
        if not ok:
            messagebox.showerror("Erro", msg, parent=self)
            return False
        return True

    def __acao_iniciar_partida(self):
        if not self.__checar_protecao(): return
        messagebox.showinfo("OK", "Iniciar Partida (em breve).", parent=self)

    def __acao_estatisticas(self):
        if not self.__checar_protecao(): return
        messagebox.showinfo("OK", "Estatísticas/Histórico (em breve).", parent=self)

    def __acao_alterar_tema(self):
        if not self.__checar_protecao(): return
        messagebox.showinfo("OK", "Alterar Tema do Tabuleiro (em breve).", parent=self)

    def __acao_alterar_dados(self):
        if not self.__checar_protecao():
            return

        def _refresh():
            self.__usuario_atual = self.__autenticar.obter_usuario_atual()
            self.__atualizar_menu_por_estado()
            self.__mostrar_tela_principal()

        AlterarDadosToplevel(self, autenticar_controller=self.__autenticar, on_sucesso=_refresh)

    def __atualizar_menu_por_estado(self):
        logado = self.__usuario_atual is not None

        self.mn_usuario.entryconfig('Login', state='disabled' if logado else 'normal')
        self.mn_usuario.entryconfig('Criar Conta', state='disabled' if logado else 'normal')
        self.mn_usuario.entryconfig('Logout', state='normal' if logado else 'disabled')

        estado_protegido = 'normal' if logado else 'disabled'
        end_index = self.mn_acoes.index('end')
        if end_index is not None:
            for i in range(end_index + 1):
                self.mn_acoes.entryconfig(i, state=estado_protegido)

