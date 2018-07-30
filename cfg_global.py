import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common
from tkinter import messagebox

LARGE_FONT= ("Verdana", 12)

class PageGlobal(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Global Settings", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        # top frame for toolbar
        self.frame_toolbar = LabelFrame(self, relief= FLAT)
        self.frame_toolbar.pack(fill=X, side=TOP)
        # save button
        self.saveimg=PhotoImage(file="images/upload-to-cloud-24.png")
        self.btn_save = Button(self.frame_toolbar, text="Save", image=self.saveimg,
                               compound='left', relief=FLAT, command=self.saveChanges)
        self.btn_save.pack(side=TOP, anchor=W)

        # setting for temperature scale, F or C
        self.tempscale = IntVar() 
        tempscaleframe = LabelFrame(self, text="Temperature Scale", relief=RAISED)
        tempscaleframe.pack(fill=X, side=TOP)

        lbltempscale = tk.Label(tempscaleframe, text="Units:")
        lbltempscale.pack(pady=10, side=LEFT)
        rdocelciusscale = Radiobutton(tempscaleframe, text="Celcius", variable=self.tempscale,
                                   value=0, indicatoron=1)
        rdocelciusscale.pack(pady=10, padx=10, side=LEFT)
        rdofahrenheitscale = Radiobutton(tempscaleframe, text="Fahrenheit", variable=self.tempscale,
                                   value=1, indicatoron=1)
        rdofahrenheitscale.pack(pady=10, side=LEFT)

        # read value from config file
        scalesetting = cfg_common.readINIfile("global", "tempscale", cfg_common.SCALE_F,
                                              cfg_common.SCALE_F)
        print(scalesetting)
        
        if str(scalesetting) == str(cfg_common.SCALE_C):
            self.tempscale.set(str(cfg_common.SCALE_C))
        else:
            self.tempscale.set(str(cfg_common.SCALE_F))
        

    def saveChanges(self):

        if cfg_common.writeINIfile('global', 'tempscale', str(self.tempscale.get())):
            messagebox.showinfo("Global Settings",
                                "New configuration saved succesfully.")
        else:
            messagebox.showerror("Global Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        
