import tkinter as tk
from tkinter import *
from tkinter import ttk

LARGE_FONT= ("Verdana", 12)

class PageGlobal(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Global Settings", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        # setting for temperature scale, F or C
        tempscale = IntVar() 
        tempscaleframe = LabelFrame(self, text="Temperature Scale")
        tempscaleframe.pack(fill=X, side=TOP)

        lbltempscale = tk.Label(tempscaleframe, text="Units:")
        lbltempscale.pack(pady=10, side=LEFT)
        rdocelciusscale = Radiobutton(tempscaleframe, text="Celcius", variable=tempscale,
                                   value=0, indicatoron=1)
        rdocelciusscale.pack(pady=10, padx=10, side=LEFT)
        rdofahrenheitscale = Radiobutton(tempscaleframe, text="Fahrenheit", variable=tempscale,
                                   value=1, indicatoron=1)
        rdofahrenheitscale.pack(pady=10, side=LEFT)
