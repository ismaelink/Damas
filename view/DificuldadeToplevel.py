# view/DificuldadeToplevel.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class DificuldadeToplevel(tk.Toplevel):
    def __init__(self, master, on_iniciar):
        super().__init__(master)
        self.title("Nível de Dificuldade")
        self.transient(master); self.grab_set()
        self.resizable(False, False)

        frm = tb.Frame(self, padding=16); frm.pack(fill='both', expand=True)
        tb.Label(frm, text="Escolha o nível", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))

        self.var = tk.StringVar(value='easy')

        tb.Radiobutton(frm, text="Fácil",   value="easy",   variable=self.var, bootstyle=PRIMARY).grid(row=1, column=0, sticky=W, pady=4)
        tb.Radiobutton(frm, text="Médio",   value="medium", variable=self.var, bootstyle=PRIMARY).grid(row=2, column=0, sticky=W, pady=4)
        tb.Radiobutton(frm, text="Difícil", value="hard",   variable=self.var, bootstyle=PRIMARY).grid(row=3, column=0, sticky=W, pady=4)

        bar = tb.Frame(frm); bar.grid(row=4, column=0, columnspan=2, pady=(12,0), sticky=EW)
        tb.Button(bar, text="Cancelar", bootstyle=SECONDARY, command=self.destroy).pack(side=LEFT)
        tb.Button(bar, text="Iniciar",   bootstyle=SUCCESS,   command=lambda:(on_iniciar(self.var.get()), self.destroy())).pack(side=LEFT, padx=8)

        # centraliza
        self.update_idletasks()
        w,h = 320, 200
        x = (self.winfo_screenwidth()//2)-(w//2)
        y = (self.winfo_screenheight()//2)-(h//2)
        self.geometry(f"{w}x{h}+{x}+{y}")
