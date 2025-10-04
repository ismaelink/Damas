# view/JanelaPrincipal.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from controller.AutenticarController import AutenticarController
from controller.PartidaController import PartidaController

from model.UsuarioDAO import UsuarioDAO
from model.PartidaDAO import PartidaDAO

from view.LoginFrame import LoginFrame
from view.CadastroToplevel import CadastroToplevel
from view.AlterarDadosToplevel import AlterarDadosToplevel
from view.PartidaFrame import PartidaFrame
from view.AlterarTemaToplevel import AlterarTemaToplevel
from view.TabuleiroFrame import TabuleiroFrame
from view.EstatisticasFrame import EstatisticasFrame


class JanelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self._style = tb.Style('flatly')

        # Estilo global p/ botões
        self._style.configure(
            'App.TButton',
            font=('Segoe UI', 11, 'bold'),
            padding=6
        )

        self.title('Jogo de Damas')
        self.__maximizar()

        # DAOs e controllers
        self.__dao = UsuarioDAO()
        self.__autenticar = AutenticarController(self.__dao)
        self.__partida_controller = PartidaController(self.__autenticar)
        self.__partidas = PartidaDAO()

        self.__usuario_atual = None

        # menus
        self.mn_barra = tk.Menu(self)
        self.config(menu=self.mn_barra)

        self.mn_usuario = tk.Menu(self.mn_barra, tearoff=0)
        self.mn_usuario.add_command(label='Login', command=self.__mostrar_login)
        self.mn_usuario.add_command(label='Criar Conta', command=self.__abrir_cadastro)
        self.mn_usuario.add_separator()
        self.mn_usuario.add_command(label='Logout', command=self.__logout)
        self.mn_barra.add_cascade(label='Usuário', menu=self.mn_usuario)

        self.mn_acoes = tk.Menu(self.mn_barra, tearoff=0)
        self.mn_acoes.add_command(label='Iniciar Partida', command=self.__acao_iniciar_partida)
        self.mn_acoes.add_command(label='Estatísticas/Histórico', command=self.__acao_estatisticas)
        self.mn_acoes.add_command(label='Alterar Tema do Tabuleiro', command=self.__acao_alterar_tema)
        self.mn_acoes.add_command(label='Alterar Dados', command=self.__acao_alterar_dados)
        self.mn_barra.add_cascade(label='Ações', menu=self.mn_acoes)

        # corpo principal
        self.frm_corpo = tb.Frame(self, padding=16)
        self.frm_corpo.pack(fill='both', expand=True)

        # atalho
        self.bind('<<voltar-principal>>', lambda e: self.__mostrar_tela_principal())

        self.__atualizar_menu_por_estado()
        self.__mostrar_login()

    # ===== infra =====
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
        for w in list(self.frm_corpo.winfo_children()):
            w.destroy()

    # ===== login/cadastro =====
    def __mostrar_login(self):
        self.__limpar_corpo()
        self.frm_login = LoginFrame(
            self.frm_corpo,
            autenticar_controller=self.__autenticar,
            on_login_ok=self.__apos_login,
            on_abrir_cadastro=self.__abrir_cadastro
        )
        self.frm_login.pack(expand=True)

    def __abrir_cadastro(self):
        CadastroToplevel(self, autenticar_controller=self.__autenticar)

    def __apos_login(self, usuario_atual):
        self.__usuario_atual = usuario_atual
        tema = (usuario_atual.get('tema_preferido') or 'flatly') if usuario_atual else 'flatly'
        if tema == 'padrao':
            tema = 'flatly'

        try:
            atual = self._style.theme.name if hasattr(self._style, "theme") and hasattr(self._style.theme, "name") else None
        except Exception:
            atual = None

        if tema != atual:
            try:
                self._style.theme_use(tema)
            except Exception:
                try:
                    self._style.theme_use('flatly')
                except Exception:
                    pass

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

    # ===== telas =====
    def __mostrar_tela_principal(self):
        self.__limpar_corpo()
        lbl_titulo = tb.Label(self.frm_corpo, text='Tela Principal', font=('Helvetica', 18, 'bold'))
        lbl_titulo.pack(anchor='center', pady=8)
        nome = self.__usuario_atual['nome'] if self.__usuario_atual else '—'
        lbl_bemvindo = tb.Label(self.frm_corpo, text=f'Bem-vindo, {nome}!')
        lbl_bemvindo.pack(anchor='center')

    # ===== ações =====
    def __acao_iniciar_partida(self):
        if not self.__checar_protecao():
            return

        self.__limpar_corpo()

        def _on_iniciar(partida_obj):
            self._mostrar_tabuleiro(partida_obj)

        frm = PartidaFrame(
            self.frm_corpo,
            partida_controller=self.__partida_controller,
            on_iniciar=_on_iniciar
        )
        frm.pack(fill='both', expand=True)

    def __acao_estatisticas(self):
        if not self.__checar_protecao():
            return
        self.__limpar_corpo()
        frm = EstatisticasFrame(self.frm_corpo, usuario_atual=self.__usuario_atual)
        frm.pack(fill='both', expand=True)

    def __acao_alterar_tema(self):
        if not self.__checar_protecao():
            return
        AlterarTemaToplevel(
            self,
            autenticar_controller=self.__autenticar,
            on_aplicar=self.__aplicar_tema_global
        )

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

    # ===== tabuleiro =====
    def _mostrar_tabuleiro(self, partida_obj):  # <- corrigido
        self.__limpar_corpo()

        def _salvar_e_voltar(payload):
            try:
                u = self.__usuario_atual or {}
                self.__partidas.registrar(
                    usuario_id=u.get('id'),
                    adversario="IA",
                    dificuldade=partida_obj.dificuldade_ia,
                    comeca=partida_obj.quem_comeca,
                    tema=partida_obj.tema_tabuleiro,
                    resultado=payload.get("resultado", "encerrada"),
                    movimentos=payload.get("movimentos", 0),
                    duracao_segundos=payload.get("duracao_segundos", 0),
                )
            except Exception as e:
                messagebox.showwarning("Aviso", f"Não foi possível salvar o histórico: {e}", parent=self)
            finally:
                self.__mostrar_tela_principal()

        frm = TabuleiroFrame(
            self.frm_corpo,
            partida=partida_obj,
            on_finalizar=_salvar_e_voltar
        )
        frm.pack(fill='both', expand=True)

    # ===== tema =====
    def __aplicar_tema_global(self, tema_escolhido):
        if tema_escolhido == 'padrao':
            tema_escolhido = (self.__usuario_atual.get('tema_preferido') or 'flatly') if self.__usuario_atual else 'flatly'

        try:
            self._style.theme_use(tema_escolhido)
        except Exception:
            messagebox.showerror("Tema", f"Não foi possível aplicar o tema '{tema_escolhido}'.", parent=self)
            return

        if self.__usuario_atual:
            try:
                self.__autenticar.salvar_tema_preferido(tema_escolhido)
            except Exception:
                pass
