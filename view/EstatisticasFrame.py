# view/EstatisticasFrame.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np  # para barras agrupadas
from model.PartidaDAO import PartidaDAO


class EstatisticasFrame(tb.Frame):
    def __init__(self, master, usuario_atual):
        super().__init__(master, padding=12)
        self.usuario = usuario_atual or {}
        self.dao = PartidaDAO()

        # ---------- UI ----------
        self.nb = tb.Notebook(self)
        self.tab_resumo = tb.Frame(self.nb, padding=8)
        self.tab_hist = tb.Frame(self.nb, padding=8)
        self.nb.add(self.tab_resumo, text="Resumo")
        self.nb.add(self.tab_hist, text="Histórico")
        self.nb.pack(fill="both", expand=True)

        # --- Resumo: Totais
        frm_totais = tb.Labelframe(self.tab_resumo, text="Totais", padding=8)
        frm_totais.pack(fill="x", pady=(0, 10))
        self.lbl_totais = tb.Label(frm_totais, text="—")
        self.lbl_totais.pack(anchor="w")

        # --- Resumo: Por nível
        frm_nivel = tb.Labelframe(self.tab_resumo, text="Por nível", padding=8)
        frm_nivel.pack(fill="x", pady=(0, 10))

        # Cabeçalhos
        tb.Label(frm_nivel, text="Nível", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=4)
        tb.Label(frm_nivel, text="Vitórias", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, padx=8)
        tb.Label(frm_nivel, text="Derrotas", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=8)
        tb.Label(frm_nivel, text="Empates", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, padx=8)

        def mk_row(row_idx, nome):
            tb.Label(frm_nivel, text=nome).grid(row=row_idx, column=0, sticky="w", padx=4)
            lv = tb.Label(frm_nivel, text="0"); lv.grid(row=row_idx, column=1)
            ld = tb.Label(frm_nivel, text="0"); ld.grid(row=row_idx, column=2)
            le = tb.Label(frm_nivel, text="0"); le.grid(row=row_idx, column=3)
            return lv, ld, le

        # rótulos por nível
        self.lbl_Fácil_v,   self.lbl_Fácil_d,   self.lbl_Fácil_e   = mk_row(1, "Fácil")
        self.lbl_Médio_v,   self.lbl_Médio_d,   self.lbl_Médio_e   = mk_row(2, "Médio")
        self.lbl_Difícil_v, self.lbl_Difícil_d, self.lbl_Difícil_e = mk_row(3, "Difícil")

        # --- Resumo: Gráfico
        frm_chart = tb.Labelframe(self.tab_resumo, text="Gráfico (Vitórias/Derrotas/Empates por nível)", padding=8)
        frm_chart.pack(fill="both", expand=True)

        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("Quantidade")
        self.canvas = FigureCanvasTkAgg(self.fig, master=frm_chart)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # --- Histórico (lista)
        frm_hist = tb.Labelframe(self.tab_hist, text="Histórico", padding=8)
        frm_hist.pack(fill="both", expand=True)

        cols = ("data", "nivel", "resultado", "mov", "dur")
        self.tv = ttk.Treeview(frm_hist, columns=cols, show="headings", height=12)
        self.tv.heading("data", text="Data/Hora")
        self.tv.heading("nivel", text="Dificuldade")
        self.tv.heading("resultado", text="Resultado")
        self.tv.heading("mov", text="Movimentos")
        self.tv.heading("dur", text="Duração (s)")
        self.tv.column("data", width=160)
        self.tv.column("nivel", width=100, anchor="center")
        self.tv.column("resultado", width=100, anchor="center")
        self.tv.column("mov", width=100, anchor="e")
        self.tv.column("dur", width=100, anchor="e")
        self.tv.pack(fill="both", expand=True)

        # Carrega dados
        self._carregar_dados()

    # ---------- Carregadores ----------
    def _carregar_dados(self):
        self._carregar_agregados()
        self._carregar_historico()

    def _carregar_agregados(self):
        """Totais + por nível + gráfico."""
        uid = self.usuario.get("id")
        if not uid:
            # Fallback se não estiver logado
            self.lbl_totais.configure(text="Total: 0 | Vitórias: 0 | Derrotas: 0 | Empates: 0")
            for lbl in (
                self.lbl_Fácil_v, self.lbl_Fácil_d, self.lbl_Fácil_e,
                self.lbl_Médio_v, self.lbl_Médio_d, self.lbl_Médio_e,
                self.lbl_Difícil_v, self.lbl_Difícil_d, self.lbl_Difícil_e,
            ):
                lbl.configure(text="0")
            self.ax.clear()
            xs = np.arange(3); larg = 0.25
            self.ax.bar(xs - larg, [0, 0, 0], width=larg, label="Vitórias")
            self.ax.bar(xs,        [0, 0, 0], width=larg, label="Derrotas")
            self.ax.bar(xs + larg, [0, 0, 0], width=larg, label="Empates")
            self.ax.set_xticks(xs); self.ax.set_xticklabels(['Fácil', 'Médio', 'Difícil'])
            self.ax.set_ylabel("Quantidade"); self.ax.legend()
            self.ax.set_ylim(0, 1)
            self.canvas.draw_idle()
            return

        # Totais gerais (com fallback para 'encerradas')
        ag = self.dao.agregados(uid)
        total       = ag.get('total', 0)
        vitorias    = ag.get('vitorias', 0)
        derrotas    = ag.get('derrotas', 0)
        empates     = ag.get('empates', 0)
        encerradas  = ag.get('encerradas', 0)

        # Mostra "Encerradas" se existir no DAO
        if 'encerradas' in ag:
            self.lbl_totais.configure(
                text=f"Total: {total}  |  Vitórias: {vitorias}  |  Derrotas: {derrotas}  |  Empates: {empates}  |  Encerradas: {encerradas}"
            )
        else:
            self.lbl_totais.configure(
                text=f"Total: {total}  |  Vitórias: {vitorias}  |  Derrotas: {derrotas}  |  Empates: {empates}"
            )

        # Por nível
        dist = self.dao.agregados_por_nivel(uid)

        def get_vals(nkey):
            dd = dist.get(nkey, {})
            return (
                dd.get("vitorias", 0),
                dd.get("derrotas", 0),
                dd.get("empates", 0),
            )

        v_Fácil, d_Fácil, e_Fácil         = get_vals('Fácil')
        v_Médio, d_Médio, e_Médio         = get_vals('Médio')
        v_Difícil, d_Difícil, e_Difícil   = get_vals('Difícil')

        # Atualiza tabela por nível
        self.lbl_Fácil_v.configure(text=str(v_Fácil))
        self.lbl_Fácil_d.configure(text=str(d_Fácil))
        self.lbl_Fácil_e.configure(text=str(e_Fácil))

        self.lbl_Médio_v.configure(text=str(v_Médio))
        self.lbl_Médio_d.configure(text=str(d_Médio))
        self.lbl_Médio_e.configure(text=str(e_Médio))

        self.lbl_Difícil_v.configure(text=str(v_Difícil))
        self.lbl_Difícil_d.configure(text=str(d_Difícil))
        self.lbl_Difícil_e.configure(text=str(e_Difícil))

        # Gráfico: barras agrupadas (V/D/E) por nível
        xs = np.arange(3)  # 0=Fácil, 1=Médio, 2=Difícil
        larg = 0.25

        self.ax.clear()
        self.ax.bar(xs - larg, [v_Fácil, v_Médio, v_Difícil], width=larg, label="Vitórias")
        self.ax.bar(xs,        [d_Fácil, d_Médio, d_Difícil], width=larg, label="Derrotas")
        self.ax.bar(xs + larg, [e_Fácil, e_Médio, e_Difícil], width=larg, label="Empates")
        self.ax.set_xticks(xs)
        self.ax.set_xticklabels(['Fácil', 'Médio', 'Difícil'])
        self.ax.set_ylabel('Quantidade')
        self.ax.legend()

        ymax = max([v_Fácil, v_Médio, v_Difícil, d_Fácil, d_Médio, d_Difícil, e_Fácil, e_Médio, e_Difícil] + [1])
        self.ax.set_ylim(0, ymax)
        self.canvas.draw_idle()

    def _carregar_historico(self):
        """Últimas partidas do usuário logado."""
        for i in self.tv.get_children():
            self.tv.delete(i)

        uid = self.usuario.get("id")
        if not uid:
            return

        rows = self.dao.listar_por_usuario(uid, limite=500)
        for r in rows:
            self.tv.insert(
                "",
                "end",
                values=(
                    r.get("criado_em", ""),
                    r.get("dificuldade", ""),
                    r.get("resultado", ""),
                    r.get("movimentos", 0),
                    r.get("duracao_segundos", 0),
                )
            )
