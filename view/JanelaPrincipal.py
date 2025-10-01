import tkinter as tk
import ttkbootstrap as tb

class JanelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Jogo de Damas')

        tb.Style('flatly')

        self._maximizar()

        self.frm_corpo = tb.Frame(self, padding=16)
        self.frm_corpo.pack(fill='both', expand=True)

        self.lbl_titulo = tb.Label(
            self.frm_corpo,
            text='Jogo de Damas',
            font=('Helvetica', 20, 'bold')
        )
        self.lbl_titulo.pack(anchor='center', pady=12)

        self.lbl_subtitulo = tb.Label(
            self.frm_corpo,
            text='Teste',
            font=('Helvetica', 11)
        )
        self.lbl_subtitulo.pack(anchor='center')

    def _maximizar(self):
        try:
            self.state('zoomed')
        except tk.TclError:
            try:
                self.attributes('-zoomed', True)
            except tk.TclError:
                largura = self.winfo_screenwidth()
                altura = self.winfo_screenheight()
                self.geometry(f'{largura}x{altura}+0+0')

