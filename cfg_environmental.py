import tkinter as tk
from tkinter import *
from tkinter import ttk

LARGE_FONT= ("Verdana", 12)

class PageEnvironmental(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Environmental Sensors", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        # dht11/22 
        self.dhtframe = LabelFrame(self, text="DHT11/22 Temperature and Humidity Sensor", relief=RAISED)
        self.dhtframe.pack(fill=X, side=TOP)
        # temperature
        self.dhttempframe = LabelFrame(self.dhtframe, relief=FLAT)
        self.dhttempframe.pack(fill=X, side=TOP)
        self.lbl_dhttemp = Label(self.dhttempframe,text="Temperature Sensor Name:")
        self.lbl_dhttemp.pack(side=LEFT, anchor=W)
        self.txt_dhttemp = Entry(self.dhttempframe)
        self.txt_dhttemp.pack(side=LEFT, anchor=W)
        self.dhttempenableframe = LabelFrame(self.dhtframe, relief=FLAT)
        self.dhttempenableframe.pack(fill=X, side=TOP)
        self.chk_dhttemp = Checkbutton(self.dhttempenableframe,text="Enable Temperature Sensor")
        self.chk_dhttemp.pack(side=LEFT, anchor=W, padx=20)

        # spacer
        self.dhtspacer = LabelFrame(self.dhtframe, relief=FLAT)
        self.dhtspacer.pack(side=TOP, anchor=W, pady=5)

        # humidity
        self.dhthumframe = LabelFrame(self.dhtframe, relief=FLAT)
        self.dhthumframe.pack(fill=X, side=TOP)
        self.lbl_dhthum = Label(self.dhthumframe,text="Humidity Sensor Name:")
        self.lbl_dhthum.pack(side=LEFT, anchor=W)
        self.txt_dhthum = Entry(self.dhthumframe)
        self.txt_dhthum.pack(side=LEFT, anchor=W)
        
        self.dhthumenableframe = LabelFrame(self.dhtframe, relief=FLAT)
        self.dhthumenableframe.pack(fill=X, side=TOP)
        self.chk_dhthum = Checkbutton(self.dhthumenableframe,text="Enable Humidity Sensor")
        self.chk_dhthum.pack(side=LEFT, anchor=W, padx=20)
        
