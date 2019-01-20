##############################################################################
# cls_GraphPage.py
#
# this is the graphing page for the ReefBerry Pi gui app
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################

import tkinter as tk
from tkinter import * 
from tkinter import ttk
import cls_DashBoard

class GraphPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        label = tk.Label(self, text="Graph Page!")
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Dashboard",
                            command=lambda: controller.show_frame(cls_DashBoard.DashBoard))
        button1.pack()

        button2 = ttk.Button(self, text="Graphpage",
                            command=lambda: controller.show_frame(GraphPage))
        button2.pack()

