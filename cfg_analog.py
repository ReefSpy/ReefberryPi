import tkinter as tk
from tkinter import *
from tkinter import ttk

LARGE_FONT= ("Verdana", 12)

class PageAnalogProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Analog Probes", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        # mcp3008 analog to digital converter
        self.adcframe = LabelFrame(self, text="MCP3008 10-bit Analog to Digital Converter", relief=RAISED)
        self.adcframe.pack(fill=X, side=TOP)

        # channel 0 frame
        self.adcch0frame = LabelFrame(self.adcframe, relief=SUNKEN, text="Channel 0")
        self.adcch0frame.pack(fill=X, side=TOP)

        # channel 0 name
        self.ch0nameframe = LabelFrame(self.adcch0frame, relief=FLAT)
        self.ch0nameframe.pack(fill=X, side=TOP)
        self.lbl_ch0name = Label(self.ch0nameframe,text="Name:")
        self.lbl_ch0name.pack(side=LEFT, anchor=W)   
        self.txt_ch0name = Entry(self.ch0nameframe)
        self.txt_ch0name.pack(side=LEFT, anchor=W)

        # channel 0 sensor type drown down list
        self.ch0sensortypeframe = LabelFrame(self.adcch0frame, relief= FLAT)
        self.ch0sensortypeframe.pack(fill=X, side=TOP)
        self.ch0sensortype = StringVar()
        self.ch0sensortypelist = ["pH"]
        self.ch0sensortype.set("pH") # default value
        self.lbl_ch0sensortype = Label(self.ch0sensortypeframe,text="Sensor Type:")
        self.lbl_ch0sensortype.pack(side=LEFT, anchor=W)    
        self.ch0sensortypemenu = OptionMenu(self.ch0sensortypeframe,self.ch0sensortype,*self.ch0sensortypelist)
        self.ch0sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch0sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 0 enable checkbox
        self.ch0enableframe = LabelFrame(self.adcch0frame, relief=FLAT)
        self.ch0enableframe.pack(fill=X, side=TOP)
        self.chk_ch0enable = Checkbutton(self.ch0enableframe,text="Enable")
        self.chk_ch0enable.pack(side=LEFT, anchor=W, padx=20)


        # channel 1 frame
        self.adcch1frame = LabelFrame(self.adcframe, relief=SUNKEN, text="Channel 1")
        self.adcch1frame.pack(fill=X, side=TOP)

        # channel 1 name
        self.ch1nameframe = LabelFrame(self.adcch1frame, relief=FLAT)
        self.ch1nameframe.pack(fill=X, side=TOP)
        self.lbl_ch1name = Label(self.ch1nameframe,text="Name:")
        self.lbl_ch1name.pack(side=LEFT, anchor=W)   
        self.txt_ch1name = Entry(self.ch1nameframe)
        self.txt_ch1name.pack(side=LEFT, anchor=W)

        # channel 1 sensor type drown down list
        self.ch1sensortypeframe = LabelFrame(self.adcch1frame, relief= FLAT)
        self.ch1sensortypeframe.pack(fill=X, side=TOP)
        self.ch1sensortype = StringVar()
        self.ch1sensortypelist = ["pH"]
        self.ch1sensortype.set("pH") # default value
        self.lbl_ch1sensortype = Label(self.ch1sensortypeframe,text="Sensor Type:")
        self.lbl_ch1sensortype.pack(side=LEFT, anchor=W)    
        self.ch1sensortypemenu = OptionMenu(self.ch1sensortypeframe,self.ch1sensortype,*self.ch1sensortypelist)
        self.ch1sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch1sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 1 enable checkbox
        self.ch1enableframe = LabelFrame(self.adcch1frame, relief=FLAT)
        self.ch1enableframe.pack(fill=X, side=TOP)
        self.chk_ch1enable = Checkbutton(self.ch1enableframe,text="Enable")
        self.chk_ch1enable.pack(side=LEFT, anchor=W, padx=20)
