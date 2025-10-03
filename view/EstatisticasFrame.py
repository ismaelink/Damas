# view/EstatisticasFrame.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from model.PartidaDAO import PartidaDAO

# tenta habilitar gráficos se houver matplotlib
_has_mpl = True
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    _has_mpl = False

class EstatisticasFrame(tb.Frame):
    def __init__(self, master, usuario_atual):
        super().__init__(master, padding=16)
        self.usuario = usuario_atual or {}
        self.dao = PartidaDAO()

        self.notebook = tb.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # abas
        self.tab_resumo = tb.Frame(self.notebook, padding=12)
        self.tab_hist   = tb.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_resumo, text='Resumo')
        self.notebook.add(self.tab_hist, text='Histórico')

        # --- Resumo ---
        box_totais = tb.Labelframe(self.tab_resumo, text='Totais', padding=10)
        box_totais.pack(fill='x', expand=False, pady=(0,10))
        self.lbl_totais = tb.Label(box_totais, text='—')
        self.lbl_totais.pack(anchor='w')

        box_nivel = tb.Labelframe(self.tab_resumo, text='Por nível', padding=10)
        box_nivel.pack(fill='x', expand=False)

        grid = tb.Frame(box_nivel)
        grid.pack(anchor='w')
        tb.Label(grid, text='Nível', width=10).grid(row=0, column=0, sticky='w')
        tb.Label(grid, text='Vitórias', width=10).grid(row=0, column=1, sticky='w')
        tb.Label(grid, text='Derrotas', width=10).grid(row=0, column=2, sticky='w')
        tb.Label(grid, text='Empates', width=10).grid(row=0, column=3, sticky='w')

        self.niveis_labels = {}
        for i, nivel in enumerate(['Facil','Médio','Dificil'], start=1):
            tb.Label(grid, text=nivel, width=10).grid(row=i, column=0, sticky='w')
            v = tb.Label(grid, text='0', width=10); v.grid(row=i, column=1, sticky='w')
            d = tb.Label(grid, text='0', width=10); d.grid(row=i, column=2, sticky='w')
            e = tb.Label(grid, text='0', width=10); e.grid(row=i, column=3, sticky='w')
            self.niveis_labels[nivel] = (v,d,e)

        if _has_mpl:
            box_chart = tb.Labelframe(self.tab_resumo, text='Gráfico (Vitórias por nível)', padding=10)
            box_chart.pack(fill='both', expand=True, pady=(10,0))
            self.fig = Figure(figsize=(4.5,2.2), dpi=100)
            self.ax  = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=box_chart)
            self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # --- Histórico ---
        box_hist = tb.Labelframe(self.tab_hist, text='Últimas partidas', padding=10)
        box_hist.pack(fill='both', expand=True)

        cols = ('data','resultado','dificuldade','comeca','mov','duracao')
        self.tv = tb.Treeview(box_hist, columns=cols, show='headings', height=12, bootstyle=INFO)
        self.tv.pack(fill='both', expand=True)

        self.tv.heading('data',        text='Data')
        self.tv.heading('resultado',   text='Resultado')
        self.tv.heading('dificuldade', text='Nível')
        self.tv.heading('comeca',      text='Começou')
        self.tv.heading('mov',         text='Mov.')
        self.tv.heading('duracao',     text='Duração (s)')

        for c in cols:
            self.tv.column(c, width=110, anchor='center')

        self._carregar_dados()

    # ---------- Carregamento ----------
    def _carregar_dados(self):
        self._carregar_historico()
        self._carregar_agregados()

    def _carregar_historico(self):
        self.tv.delete(*self.tv.get_children())
        rows = self.dao.listar_por_usuario(self.usuario.get('id'), limite=500)
        for r in rows:
            self.tv.insert('', 'end', values=(
                r.get('criado_em', '')[:19] if r.get('criado_em') else '',
                r.get('resultado',''),
                r.get('dificuldade',''),
                r.get('comeca',''),
                r.get('movimentos',0),
                r.get('duracao_segundos',0),
            ))

    def _carregar_agregados(self):
        ag = self.dao.agregados(self.usuario.get('id'))
        total    = ag.get('total', 0)
        vitorias = ag.get('vitorias', 0)
        derrotas = ag.get('derrotas', 0)
        empates  = ag.get('empates', 0)

        self.lbl_totais.configure(
            text="Total: %d  |  Vitórias: %d  |  Derrotas: %d  |  Empates: %d" %
                 (total, vitorias, derrotas, empates)
        )

        dist = self.dao.agregados_por_nivel(self.usuario.get('id'))
        for nivel, (v_lbl, d_lbl, e_lbl) in self.niveis_labels.items():
            v_lbl.configure(text=str(dist.get(nivel, {}).get('vitorias', 0)))
            d_lbl.configure(text=str(dist.get(nivel, {}).get('derrotas', 0)))
            e_lbl.configure(text=str(dist.get(nivel, {}).get('empates', 0)))

        if _has_mpl:
            self.ax.clear()
            niveis = ['Facil','Médio','Dificil']
            valores = [dist.get(n, {}).get('vitorias', 0) for n in niveis]
            self.ax.bar(niveis, valores)
            self.ax.set_ylabel('Vitórias')
            self.ax.set_ylim(0, max(valores + [1]))
            self.ax.grid(True, axis='y', alpha=0.3)
            self.canvas.draw_idle()
