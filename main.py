import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from gui.accueil import AccueilScreen
from gui.gestion_clients_livreurs import GestionScreen
from gui.commandes import CommandesScreen


class Application(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Système intelligent de gestion de livraison")
        self.geometry("1000x700")
        self.minsize(900, 600)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for screen_class in (AccueilScreen, GestionScreen, CommandesScreen):
            frame = screen_class(container, self)
            self.frames[screen_class.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("AccueilScreen")

    def show_frame(self, name):
        self.frames[name].tkraise()


if __name__ == "__main__":
    # Point d'entrée de l'application
    app = Application()
    app.mainloop()
