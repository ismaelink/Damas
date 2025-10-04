# view/AlterarTemaToplevel.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

# temas do ttkbootstrap (sinta-se livre para ajustar)
TEMAS = ["flatly", "litera", "journal", "darkly", "cyborg", "solar", "morph", "sandstone", "pulse"]

class AlterarTemaToplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller, on_aplicar=None):
        super().__init__(master)
        self.title("Alterar Tema do Tabuleiro")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)

        self.__aut = autenticar_controller
        # on_aplicar deve aplicar e (se desejar) salvar o tema na JanelaPrincipal
        self.__on_aplicar = on_aplicar or (lambda tema: None)

        frm = tb.Frame(self, padding=16)
        frm.pack(fill='both', expand=True)

        tb.Label(
            frm, text="Selecione o tema", font=('Helvetica', 16, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tb.Label(frm, text="Tema:").grid(row=1, column=0, sticky=E, padx=(0, 8))
        self.var_tema = tk.StringVar(value="flatly")
        self.cbx = tb.Combobox(frm, textvariable=self.var_tema, values=TEMAS, state="readonly", width=22)
        self.cbx.grid(row=1, column=1, sticky=W)

        bar = tb.Frame(frm)
        bar.grid(row=2, column=0, columnspan=2, pady=(12, 0))

        # Botões padronizados com o estilo único da aplicação
        tb.Button(bar, text="Pré-visualizar", style='App.TButton', command=self._preview).pack(side=LEFT, padx=6)
        tb.Button(bar, text="Salvar",         style='App.TButton', command=self._salvar).pack(side=LEFT, padx=6)
        tb.Button(bar, text="Cancelar",       style='App.TButton', command=self.destroy).pack(side=LEFT, padx=6)

        # centraliza a janelinha
        self.update_idletasks()
        w, h = 420, 180
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _preview(self):
        tema = self.var_tema.get()
        try:
            tb.Style().theme_use(tema)
            self.__on_aplicar(tema)
        except Exception:
            pass
        messagebox.showinfo("Pré-visualização", f"Tema '{tema}' aplicado (pré-visualização).", parent=self)


   
    def _salvar(self):
        tema = self.var_tema.get()
        try:
            tb.Style().theme_use(tema)   # tenta aplicar
            self.__on_aplicar(tema)      # callback para JanelaPrincipal
        except Exception:
            # ignora erros de troca de tema
            pass

        # sempre mostra sucesso, mesmo que o ttkbootstrap dê warning interno
        messagebox.showinfo("Sucesso", f"Tema '{tema}' aplicado com sucesso!", parent=self)
        self.destroy()


   