import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

class PartidaFrame(tb.Frame):
    def __init__(self, master, partida_controller, on_iniciar=None):
        super().__init__(master, padding=16)
        self.__controller = partida_controller
        self.__on_iniciar = on_iniciar or (lambda partida: None)

        # titulo
        lbl_tit = tb.Label(self, text='Iniciar Partida', font=('Helvetica', 18, 'bold'))
        lbl_tit.grid(row=0, column=0, columnspan=4, pady=(0, 12), sticky=W)

        # ====== linha 1: adversário / dificuldade ======
        tb.Label(self, text='Adversário:').grid(row=1, column=0, sticky=E, padx=(0, 8), pady=6)

        self.var_adv = tk.StringVar(value='IA')
        cbx_adv = tb.Combobox(self, textvariable=self.var_adv, state='readonly',
                              values=('IA', 'Humano'), width=18)
        cbx_adv.grid(row=1, column=1, sticky=W, pady=6)

        tb.Label(self, text='Dificuldade IA:').grid(row=1, column=2, sticky=E, padx=(24, 8), pady=6)

        self.var_nivel = tk.StringVar(value='Facil')
        cbx_nivel = tb.Combobox(self, textvariable=self.var_nivel, state='readonly',
                                values=('Facil', 'Medio', 'Dificil'), width=18)
        cbx_nivel.grid(row=1, column=3, sticky=W, pady=6)

        # ====== linha 2: quem começa ======
        tb.Label(self, text='Quem começa:').grid(row=2, column=0, sticky=E, padx=(0, 8), pady=6)

        self.var_comeca = tk.StringVar(value='brancas')
        grp = tb.Frame(self)
        grp.grid(row=2, column=1, columnspan=3, sticky=W, pady=6)

        tb.Radiobutton(grp, text='Brancas', value='brancas', variable=self.var_comeca, bootstyle=PRIMARY).pack(side=LEFT, padx=(0,8))
        tb.Radiobutton(grp, text='Pretas',  value='pretas',  variable=self.var_comeca, bootstyle=PRIMARY).pack(side=LEFT)


        # ====== linha 3: tema ======
        tb.Label(self, text='Tema do tabuleiro:').grid(row=3, column=0, sticky=E, padx=(0, 8), pady=6)

        self.var_tema = tk.StringVar(value='padrao')
        cbx_tema = tb.Combobox(self, textvariable=self.var_tema, state='readonly',
                               values=('padrao', 'escuro', 'alto-contraste'), width=18)
        cbx_tema.grid(row=3, column=1, sticky=W, pady=6)

        # ====== linha 4: botões ======
        barra = tb.Frame(self)
        barra.grid(row=4, column=0, columnspan=4, sticky=EW, pady=(12,0))

        btn_cancelar = tb.Button(barra, text='CANCELAR', bootstyle=SECONDARY, command=self.__cancelar)
        btn_cancelar.pack(side=LEFT)

        btn_iniciar = tb.Button(barra, text='INICIAR', bootstyle=SUCCESS, command=self.__iniciar)
        btn_iniciar.pack(side=LEFT, padx=8)

        # responsivo
        for col in (1,3):
            self.columnconfigure(col, weight=1)

    def __cancelar(self):
        # volta para a tela principal do app
        self.master.event_generate('<<voltar-principal>>')

    def __iniciar(self):
        adv = self.var_adv.get()
        dif = self.var_nivel.get()
        comeca = self.var_comeca.get()
        tema = self.var_tema.get()

        ok, msg, partida = self.__controller.criar_partida(
            adversario=adv,
            dificuldade=dif,
            quem_comeca=comeca,
            tema=tema
        )
        if not ok:
            messagebox.showerror("Erro", msg, parent=self)
            return

        # sinaliza para a JanelaPrincipal carregar a tela do tabuleiro/partida
        self.__on_iniciar(partida)
