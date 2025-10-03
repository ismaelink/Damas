# view/EstatisticasFrame.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from model.PartidaDAO import PartidaDAO

# matplotlib embutido no Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# DateEntry (se não existir no seu ttkbootstrap, cai no Entry simples)
try:
    from ttkbootstrap.widgets import DateEntry
except Exception:
    DateEntry = None


class EstatisticasFrame(tb.Frame):
    def __init__(self, master, usuario_atual:dict):
        super().__init__(master, padding=16)
        self.usuario = usuario_atual
        self.dao = PartidaDAO()

        tb.Label(self, text="Estatísticas", font=("Helvetica", 18, "bold")).pack(anchor='w', pady=(0,8))

        self.nb = tb.Notebook(self)
        self.nb.pack(fill='both', expand=True)

        self._montar_historico()
        self._montar_desempenho()

        self._carregar_dados()

    # ---------- HISTÓRICO ----------
    def _montar_historico(self):
        frm = tb.Frame(self.nb, padding=8)
        self.nb.add(frm, text="Histórico de Jogos")

        # Filtros
        filtro = tb.Labelframe(frm, text="Filtros", padding=8)
        filtro.pack(fill='x', pady=(0,8))

        tb.Label(filtro, text="Nível:").grid(row=0, column=0, sticky='w', padx=(0,6))
        self.cb_nivel = tb.Combobox(filtro, values=["Todos","easy","medium","hard"], state="readonly", width=10)
        self.cb_nivel.current(0)
        self.cb_nivel.grid(row=0, column=1, padx=(0,12))

        tb.Label(filtro, text="Resultado:").grid(row=0, column=2, sticky='w', padx=(0,6))
        self.cb_result = tb.Combobox(filtro, values=["Todos","vitoria","derrota","empate","encerrada"], state="readonly", width=12)
        self.cb_result.current(0)
        self.cb_result.grid(row=0, column=3, padx=(0,12))

        tb.Label(filtro, text="De:").grid(row=0, column=4, sticky='w', padx=(0,6))
        if DateEntry:
            self.dt_ini = DateEntry(filtro, bootstyle=INFO, width=12)
        else:
            self.dt_ini = tb.Entry(filtro, width=14)  # YYYY-MM-DD
        self.dt_ini.grid(row=0, column=5, padx=(0,12))

        tb.Label(filtro, text="Até:").grid(row=0, column=6, sticky='w', padx=(0,6))
        if DateEntry:
            self.dt_fim = DateEntry(filtro, bootstyle=INFO, width=12)
        else:
            self.dt_fim = tb.Entry(filtro, width=14)  # YYYY-MM-DD
        self.dt_fim.grid(row=0, column=7, padx=(0,12))

        tb.Button(filtro, text="Aplicar", bootstyle=PRIMARY, command=self._aplicar_filtros).grid(row=0, column=8, padx=(4,0))
        tb.Button(filtro, text="Limpar", bootstyle=SECONDARY, command=self._limpar_filtros).grid(row=0, column=9, padx=(4,0))

        # Tabela
        cols = ("data", "adversario", "dificuldade", "comeca", "resultado", "mov", "duracao", "tema")
        self.tv = tb.Treeview(frm, columns=cols, show="headings", height=18, bootstyle=PRIMARY)
        self.tv.pack(fill='both', expand=True)

        headers = {
            "data":"Data/Hora", "adversario":"Adversário", "dificuldade":"Nível",
            "comeca":"Começa", "resultado":"Resultado", "mov":"Movimentos",
            "duracao":"Duração", "tema":"Tema"
        }
        for c, h in headers.items():
            self.tv.heading(c, text=h)
            self.tv.column(c, anchor='center', width=110)

        # Barra de ações
        btns = tb.Frame(frm, padding=(0,8))
        btns.pack(fill='x')
        tb.Button(btns, text="Atualizar", bootstyle=SECONDARY, command=self._carregar_historico).pack(side=LEFT)

    # ---------- DESEMPENHO ----------
    def _montar_desempenho(self):
        frm = tb.Frame(self.nb, padding=8)
        self.nb.add(frm, text="Desempenho")

        self.lbl_totais = tb.Label(frm, text="", font=("Helvetica", 12))
        self.lbl_totais.pack(anchor='w', pady=(0,6))

        # Figura matplotlib
        fig = Figure(figsize=(6.2, 3.2), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Vitórias/Derrotas/Empates por nível")
        self.ax.set_xlabel("Nível")
        self.ax.set_ylabel("Partidas")

        self.canvas = FigureCanvasTkAgg(fig, master=frm)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Progress bars gerais
        wrap = tb.Frame(frm); wrap.pack(anchor='w', pady=(8,4))
        self.pg_v = tb.Progressbar(wrap, bootstyle=SUCCESS, length=320); self.pg_v.grid(row=0, column=0, sticky='w', pady=4)
        self.pg_d = tb.Progressbar(wrap, bootstyle=DANGER,  length=320); self.pg_d.grid(row=1, column=0, sticky='w', pady=4)
        self.pg_e = tb.Progressbar(wrap, bootstyle=INFO,    length=320); self.pg_e.grid(row=2, column=0, sticky='w', pady=4)

        self.lbl_v = tb.Label(wrap, text="Vitórias: 0"); self.lbl_v.grid(row=0, column=1, padx=12, sticky='w')
        self.lbl_d = tb.Label(wrap, text="Derrotas: 0"); self.lbl_d.grid(row=1, column=1, padx=12, sticky='w')
        self.lbl_e = tb.Label(wrap, text="Empates: 0");  self.lbl_e.grid(row=2, column=1, padx=12, sticky='w')

        tb.Button(frm, text="Recalcular", bootstyle=SECONDARY, command=self._carregar_agregados).pack(pady=(8,0), anchor='w')

    # ---------- carregamento ----------
    def _carregar_dados(self):
        self._carregar_historico()
        self._carregar_agregados()

    def _carregar_historico(self, rows=None):
        # limpa
        for i in self.tv.get_children():
            self.tv.delete(i)

        if rows is None:
            rows = self.dao.listar_por_usuario(self.usuario['id'], limite=500)

        for r in rows:
            dur = f"{r['duracao_segundos']//60:02d}:{r['duracao_segundos']%60:02d}"
            self.tv.insert("", "end", values=(
                r['criado_em'], r['adversario'], r['dificuldade'], r['comeca'],
                r['resultado'], r['movimentos'], dur, r['tema']
            ))

    def _carregar_agregados(self):
        ag = self.dao.agregados(self.usuario['id'])
        total = max(ag['total'], 1)
        self.lbl_totais.configure(text=f"Total: {ag['total']}  |  Vitórias: {ag['vitorias']}  |  Derrotas: {ag['derrotas']}  |  Empates: {ag['empates']}")
        self.pg_v.configure(value=ag['vitorias'] * 100 / total)
        self.pg_d.configure(value=ag['derrotas'] * 100 / total)
        self.pg_e.configure(value=ag['empates']  * 100 / total)
        self.lbl_v.configure(text=f"Vitórias: {ag['vitorias']} ({ag['vitorias']*100/total:.1f}%)")
        self.lbl_d.configure(text=f"Derrotas: {ag['derrotas']} ({ag['derrotas']*100/total:.1f}%)")
        self.lbl_e.configure(text=f"Empates: {ag['empates']} ({ag['empates']*100/total:.1f}%)")

        # gráfico por nível
        dist = self.dao.agregados_por_nivel(self.usuario['id'])
        niveis = ["easy","medium","hard"]
        v = [dist.get(n, {}).get("vitorias", 0) for n in niveis]
        d = [dist.get(n, {}).get("derrotas", 0) for n in niveis]
        e = [dist.get(n, {}).get("empates", 0)  for n in niveis]

        self.ax.clear()
        self.ax.set_title("Vitórias/Derrotas/Empates por nível")
        self.ax.set_xlabel("Nível")
        self.ax.set_ylabel("Partidas")

        import numpy as np
        x = np.arange(len(niveis))
        largura = 0.25

        self.ax.bar(x - largura, v, width=largura, label='Vitórias')
        self.ax.bar(x,           d, width=largura, label='Derrotas')
        self.ax.bar(x + largura, e, width=largura, label='Empates')
        self.ax.set_xticks(x, niveis)
        self.ax.legend(loc='upper right')

        self.canvas.draw_idle()

    # ---------- filtros ----------
    def _aplicar_filtros(self):
        nivel = (self.cb_nivel.get() or "Todos").lower()
        res   = (self.cb_result.get() or "Todos").lower()
        data_i = self.dt_ini.entry.get() if DateEntry else (self.dt_ini.get().strip() or None)
        data_f = self.dt_fim.entry.get() if DateEntry else (self.dt_fim.get().strip() or None)

        # normaliza strings vazias
        if data_i == "": data_i = None
        if data_f == "": data_f = None

        rows = self.dao.listar_filtrado(
            usuario_id=self.usuario['id'],
            dificuldade=None if nivel=="todos" else nivel,
            resultado=None if res=="todos" else res,
            data_ini=data_i,
            data_fim=data_f,
            limite=500
        )
        self._carregar_historico(rows)

    def _limpar_filtros(self):
        self.cb_nivel.set("Todos")
        self.cb_result.set("Todos")
        if DateEntry:
            try:
                self.dt_ini.set_date(None)
                self.dt_fim.set_date(None)
            except Exception:
                pass
        else:
            self.dt_ini.delete(0,'end')
            self.dt_fim.delete(0,'end')
        self._carregar_historico()
