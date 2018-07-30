import tkinter as tk
from tkinter import *
from tkinter import ttk

LARGE_FONT= ("Verdana", 12)

class PageFeedTimers(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Feed Timers", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        ###########################################################################
        # frame for feed timers
        ###########################################################################
        self.frame_feed = LabelFrame(self, text="Feed Timers", relief= RAISED)
        self.frame_feed.pack(fill=X, side=TOP)

        # timer A
        self.Aframe = LabelFrame(self.frame_feed, relief= FLAT)
        self.Aframe.pack(fill=X, side=TOP)
        self.lbl_nameA = Label(self.Aframe,text="Timer A:")
        self.lbl_nameA.pack(side=LEFT, anchor=W, padx=10)
        self.spn_A = Spinbox(self.Aframe, from_=60,to=3600, increment=1)
        self.spn_A.pack(side=LEFT, anchor=W)
        
        # timer B
        self.Bframe = LabelFrame(self.frame_feed, relief= FLAT)
        self.Bframe.pack(fill=X, side=TOP)
        self.lbl_nameB = Label(self.Bframe,text="Timer B:")
        self.lbl_nameB.pack(side=LEFT, anchor=W, padx=10)
        self.spn_B = Spinbox(self.Bframe, from_=60,to=3600, increment=1)
        self.spn_B.pack(side=LEFT, anchor=W)

        # timer C
        self.Cframe = LabelFrame(self.frame_feed, relief= FLAT)
        self.Cframe.pack(fill=X, side=TOP)
        self.lbl_nameC = Label(self.Cframe,text="Timer C:")
        self.lbl_nameC.pack(side=LEFT, anchor=W, padx=10)
        self.spn_C = Spinbox(self.Cframe, from_=60,to=3600, increment=1)
        self.spn_C.pack(side=LEFT, anchor=W)

        # timer D
        self.Dframe = LabelFrame(self.frame_feed, relief= FLAT)
        self.Dframe.pack(fill=X, side=TOP)
        self.lbl_nameD = Label(self.Dframe,text="Timer D:")
        self.lbl_nameD.pack(side=LEFT, anchor=W, padx=10)
        self.spn_D = Spinbox(self.Dframe, from_=60,to=3600, increment=1)
        self.spn_D.pack(side=LEFT, anchor=W)

        # description text
        self.lbl_desc = Label(self.frame_feed,text= "all time in seconds (60-3600)")
        self.lbl_desc.pack(side=LEFT, anchor=W, padx=20, pady=10)
        
