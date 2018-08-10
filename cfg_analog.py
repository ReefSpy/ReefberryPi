import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common

LARGE_FONT= ("Verdana", 12)

class PageAnalogProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Analog Probes", font=LARGE_FONT)
        #label.pack(side=TOP, pady=10, anchor=W)
        label.grid(row=0, column=0, pady=10, sticky=W)

        # save button
        self.saveimg=PhotoImage(file="images/save-blue-24.png")
        self.btn_save = Button(self, text="Save", image=self.saveimg,
                               compound='left', relief=RAISED, command=self.saveChanges)
        self.btn_save.grid(row=1, column=0, sticky=W)


        # mcp3008 analog to digital converter
        self.adcframe = LabelFrame(self, text="MCP3008 10-bit Analog to Digital Converter", relief=GROOVE)
        #self.adcframe.pack(fill=X, side=TOP)
        self.adcframe.grid(row=2, column=0, pady=10, sticky=W)

        # channel 0 frame
        self.adcch0frame = LabelFrame(self.adcframe, relief=SUNKEN, text="Channel 0")
        #self.adcch0frame.pack(fill=X, side=TOP)
        self.adcch0frame.grid(row=0, column=0, padx=10, pady=10)

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
        self.ch0Enabled = IntVar()
        self.ch0enableframe = LabelFrame(self.adcch0frame, relief=FLAT)
        self.ch0enableframe.pack(fill=X, side=TOP)
        self.chk_ch0enable = Checkbutton(self.ch0enableframe,text="Enable", variable=self.ch0Enabled)
        self.chk_ch0enable.pack(side=LEFT, anchor=W, padx=20)


        # channel 1 frame
        self.adcch1frame = LabelFrame(self.adcframe, relief=SUNKEN, text="Channel 1")
        #self.adcch1frame.pack(fill=X, side=TOP)
        self.adcch1frame.grid(row=0, column=1, padx=10, pady=10)

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
        self.ch1Enabled = IntVar()
        self.ch1enableframe = LabelFrame(self.adcch1frame, relief=FLAT)
        self.ch1enableframe.pack(fill=X, side=TOP)
        self.chk_ch1enable = Checkbutton(self.ch1enableframe,text="Enable", variable=self.ch1Enabled)
        self.chk_ch1enable.pack(side=LEFT, anchor=W, padx=20)

        # read values from config file
        # Ch0 name
        val = cfg_common.readINIfile("mcp3008", "ch0_name", "Unnamed")
        self.txt_ch0name.delete(0,END)
        self.txt_ch0name.insert(0,val)
        # Ch0 enabled
        val = cfg_common.readINIfile("mcp3008", "ch0_enabled", "False")
        if str(val) == "True":
            self.chk_ch0enable.select()
        else:
            self.chk_ch0enable.deselect()
        # Ch0 type
        val = cfg_common.readINIfile("mcp3008", "ch0_type", "pH")
        self.ch0sensortype.set(val)
        

        # Ch1 name
        val = cfg_common.readINIfile("mcp3008", "ch1_name", "Unnamed")
        self.txt_ch1name.delete(0,END)
        self.txt_ch1name.insert(0,val)
        #Ch1 enabled
        val = cfg_common.readINIfile("mcp3008", "ch1_enabled", "False")
        if str(val) == "True":
            self.chk_ch1enable.select()
        else:
            self.chk_ch1enable.deselect()
        # Ch1 type
        val = cfg_common.readINIfile("mcp3008", "ch1_type", "pH")
        self.ch1sensortype.set(val)

    def saveChanges(self):
        # Channel 0
        if cfg_common.writeINIfile('mcp3008', 'ch0_name', str(self.txt_ch0name.get())) != True:
             messagebox.showerror("Analog Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        
        if self.ch0Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"
            
        if cfg_common.writeINIfile('mcp3008', 'ch0_enabled', str(chkstate)) != True:
           messagebox.showerror("Analog Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        
        if cfg_common.writeINIfile('mcp3008', 'ch0_type', str(self.ch0sensortype.get())) != True:
           messagebox.showerror("Analog Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
           
        # Channel 1
        if cfg_common.writeINIfile('mcp3008', 'ch1_name', str(self.txt_ch1name.get())) != True:
             messagebox.showerror("Analog Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")

        if self.ch1Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"
            
        if cfg_common.writeINIfile('mcp3008', 'ch1_enabled', str(chkstate)) != True:
           messagebox.showerror("Analog Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")

        if cfg_common.writeINIfile('mcp3008', 'ch1_type', str(self.ch1sensortype.get())) != True:
           messagebox.showerror("Analog Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        



        
        
