# view/PartidaFrame.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

from view.Jogador2Toplevel import Jogador2Toplevel


class PartidaFrame(tb.Frame):
    def __init__(self, master, partida_controller, on_iniciar=None):
        super().__init__(master, padding=16)
        self.__controller = partida_controller
        self.__on_iniciar = on_iniciar or (lambda partida: None)

        # Título
        tb.Label(self, text='Iniciar Partida', font=('Helvetica', 18, 'bold'))\
          .grid(row=0, column=0, columnspan=4, pady=(0, 12), sticky=W)

        # Adversário
        tb.Label(self, text='Adversário:')\
          .grid(row=1, column=0, sticky=E, padx=(0, 8), pady=6)
        self.var_adv = tk.StringVar(value='IA')
        self.cbx_adv = tb.Combobox(
            self, textvariable=self.var_adv, state='readonly',
            values=('IA', 'Humano'), width=18
        )
        self.cbx_adv.grid(row=1, column=1, sticky=W, pady=6)
        self.var_adv.trace_add('write', self.__on_adv_change)

        # Dificuldade (apenas para IA)
        tb.Label(self, text='Dificuldade IA:')\
          .grid(row=1, column=2, sticky=E, padx=(24, 8), pady=6)
        self.var_nivel = tk.StringVar(value='Fácil')
        self.cbx_nivel = tb.Combobox(
            self, textvariable=self.var_nivel, state='readonly',
            values=('Fácil', 'Médio', 'Difícil'), width=18
        )
        self.cbx_nivel.grid(row=1, column=3, sticky=W, pady=6)

        # Quem começa
        tb.Label(self, text='Quem começa:')\
          .grid(row=2, column=0, sticky=E, padx=(0, 8), pady=6)
        self.var_comeca = tk.StringVar(value='brancas')
        grp = tb.Frame(self)
        grp.grid(row=2, column=1, columnspan=3, sticky=W, pady=6)
        tb.Radiobutton(grp, text='Brancas', value='brancas',
                       variable=self.var_comeca, bootstyle=PRIMARY)\
          .pack(side=LEFT, padx=(0, 8))
        tb.Radiobutton(grp, text='Pretas', value='pretas',
                       variable=self.var_comeca, bootstyle=PRIMARY)\
          .pack(side=LEFT)

        # Barra de botões
        barra = tb.Frame(self)
        barra.grid(row=3, column=0, columnspan=4, sticky=EW, pady=(12, 0))
        tb.Button(barra, text='CANCELAR', bootstyle=SECONDARY,
                  command=self.__cancelar).pack(side=LEFT)
        tb.Button(barra, text='INICIAR', bootstyle=SUCCESS,
                  command=self.__iniciar).pack(side=LEFT, padx=8)

        # Responsivo
        for col in (1, 3):
            self.columnconfigure(col, weight=1)

        # Estado inicial (IA selecionada)
        self.__on_adv_change()

    # --- eventos/ações ---
    def __on_adv_change(self, *args):
        """Habilita dificuldade apenas quando adversário = IA."""
        adv = self.var_adv.get()
        if adv == 'IA':
            self.cbx_nivel.configure(state='readonly')
        else:
            # humano: dificuldade não se aplica
            self.cbx_nivel.configure(state='disabled')

    def __cancelar(self):
        self.master.event_generate('<<voltar-principal>>')

    def __iniciar(self):
        adv = self.var_adv.get()
        dif = self.var_nivel.get()
        comeca = self.var_comeca.get()

        jogador2 = None
        if adv == "Humano":
            # Abrir modal do Jogador 2 (pode logar ou criar conta)
            dlg = Jogador2Toplevel(
                self,
                autenticar_controller=self.__controller.get_auth_controller()
            )
            self.wait_window(dlg)
            if not getattr(dlg, "result_user", None):
                # usuário cancelou
                return
            jogador2 = dlg.result_user  # {'id':..., 'nome':...}

        ok, msg, partida = self.__controller.criar_partida(
            adversario=adv,
            dificuldade=dif,
            quem_comeca=comeca,
            jogador2=jogador2
        )
        if not ok:
            messagebox.showerror("Erro", msg, parent=self)
            return

        # Passa a partida para a janela principal
        self.__on_iniciar(partida)
