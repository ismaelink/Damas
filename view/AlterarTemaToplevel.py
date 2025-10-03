# view/AlterarTemaToplevel.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

# alguns temas comuns do ttkbootstrap
TEMAS = ["flatly", "litera", "journal", "darkly", "cyborg", "solar", "morph", "sandstone", "pulse"]

class AlterarTemaToplevel(tk.Toplevel):
    def __init__(self, master, autenticar_controller, on_aplicar=None):
        super().__init__(master)
        self.title("Alterar Tema do Tabuleiro")
        self.transient(master); self.grab_set()
        self.resizable(False, False)

        self.__aut = autenticar_controller
        self.__on_aplicar = on_aplicar or (lambda tema: None)

        frm = tb.Frame(self, padding=16); frm.pack(fill='both', expand=True)
        tb.Label(frm, text="Selecione o tema", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))

        tb.Label(frm, text="Tema:").grid(row=1, column=0, sticky=E, padx=(0,8))
        self.var_tema = tk.StringVar(value="flatly")
        self.cbx = tb.Combobox(frm, textvariable=self.var_tema, values=TEMAS, state="readonly", width=22)
        self.cbx.grid(row=1, column=1, sticky=W)

        bar = tb.Frame(frm); bar.grid(row=2, column=0, columnspan=2, pady=(12,0))
        tb.Button(bar, text="Pré-visualizar", bootstyle=INFO, command=self._preview).pack(side=LEFT, padx=6)
        tb.Button(bar, text="Salvar",         bootstyle=SUCCESS, command=self._salvar).pack(side=LEFT, padx=6)
        tb.Button(bar, text="Cancelar",       bootstyle=SECONDARY, command=self.destroy).pack(side=LEFT, padx=6)

        # centraliza
        self.update_idletasks()
        w,h = 420, 180
        x = (self.winfo_screenwidth()//2)-(w//2)
        y = (self.winfo_screenheight()//2)-(h//2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _preview(self):
        tema = self.var_tema.get()
        try:
            # aplica tema na hora
            style = tb.Style()
            style.theme_use(tema)
            # avisa JanelaPrincipal (se quiser ajustar outras coisas)
            self.__on_aplicar(tema)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível aplicar o tema '{tema}'.\n{e}", parent=self)

    def _salvar(self):
        tema = self.var_tema.get()
        ok, msg = self.__aut.salvar_tema_preferido(tema)  # ver patch abaixo no controller/DAO
        if not ok:
            messagebox.showerror("Erro", msg, parent=self); return
        # aplica de vez
        tb.Style().theme_use(tema)
        self.__on_aplicar(tema)
        messagebox.showinfo("Sucesso", "Tema atualizado com sucesso.", parent=self)
        self.destroy()
