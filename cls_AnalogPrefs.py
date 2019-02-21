import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common

LARGE_FONT= ("Verdana", 12)

class PageAnalogProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        label = tk.Label(self, text="Analog Probes", font=LARGE_FONT)
        #label.pack(side=TOP, pady=10, anchor=W)
        label.grid(row=0, column=0, sticky=W)

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
        self.adcch0frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 0")
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
        self.ch0sensortypelist = ["pH", "raw"]
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
        self.chk_ch0enable = Checkbutton(self.ch0enableframe,text="Enable",
                                         variable=self.ch0Enabled, command=self.enableControls)
        self.chk_ch0enable.pack(side=LEFT, anchor=W, padx=20)


        # channel 1 frame
        self.adcch1frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 1")
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
        self.ch1sensortypelist = ["pH", "raw"]
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
        self.chk_ch1enable = Checkbutton(self.ch1enableframe,text="Enable",
                                         variable=self.ch1Enabled, command=self.enableControls)
        self.chk_ch1enable.pack(side=LEFT, anchor=W, padx=20)

        # channel 2 frame
        self.adcch2frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 2")
        #self.adcch1frame.pack(fill=X, side=TOP)
        self.adcch2frame.grid(row=1, column=0, padx=10, pady=10)

        # channel 2 name
        self.ch2nameframe = LabelFrame(self.adcch2frame, relief=FLAT)
        self.ch2nameframe.pack(fill=X, side=TOP)
        self.lbl_ch2name = Label(self.ch2nameframe,text="Name:")
        self.lbl_ch2name.pack(side=LEFT, anchor=W)   
        self.txt_ch2name = Entry(self.ch2nameframe)
        self.txt_ch2name.pack(side=LEFT, anchor=W)

        # channel 2 sensor type drown down list
        self.ch2sensortypeframe = LabelFrame(self.adcch2frame, relief= FLAT)
        self.ch2sensortypeframe.pack(fill=X, side=TOP)
        self.ch2sensortype = StringVar()
        self.ch2sensortypelist = ["pH", "raw"]
        self.ch2sensortype.set("pH") # default value
        self.lbl_ch2sensortype = Label(self.ch2sensortypeframe,text="Sensor Type:")
        self.lbl_ch2sensortype.pack(side=LEFT, anchor=W)    
        self.ch2sensortypemenu = OptionMenu(self.ch2sensortypeframe,self.ch2sensortype,*self.ch2sensortypelist)
        self.ch2sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch2sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 2 enable checkbox
        self.ch2Enabled = IntVar()
        self.ch2enableframe = LabelFrame(self.adcch2frame, relief=FLAT)
        self.ch2enableframe.pack(fill=X, side=TOP)
        self.chk_ch2enable = Checkbutton(self.ch2enableframe,text="Enable",
                                         variable=self.ch2Enabled, command=self.enableControls)
        self.chk_ch2enable.pack(side=LEFT, anchor=W, padx=20)

        # channel 3 frame
        self.adcch3frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 3")
        #self.adcch3frame.pack(fill=X, side=TOP)
        self.adcch3frame.grid(row=1, column=1, padx=10, pady=10)

        # channel 3 name
        self.ch3nameframe = LabelFrame(self.adcch3frame, relief=FLAT)
        self.ch3nameframe.pack(fill=X, side=TOP)
        self.lbl_ch3name = Label(self.ch3nameframe,text="Name:")
        self.lbl_ch3name.pack(side=LEFT, anchor=W)   
        self.txt_ch3name = Entry(self.ch3nameframe)
        self.txt_ch3name.pack(side=LEFT, anchor=W)

        # channel 3 sensor type drown down list
        self.ch3sensortypeframe = LabelFrame(self.adcch3frame, relief= FLAT)
        self.ch3sensortypeframe.pack(fill=X, side=TOP)
        self.ch3sensortype = StringVar()
        self.ch3sensortypelist = ["pH", "raw"]
        self.ch3sensortype.set("pH") # default value
        self.lbl_ch3sensortype = Label(self.ch3sensortypeframe,text="Sensor Type:")
        self.lbl_ch3sensortype.pack(side=LEFT, anchor=W)    
        self.ch3sensortypemenu = OptionMenu(self.ch3sensortypeframe,self.ch3sensortype,*self.ch3sensortypelist)
        self.ch3sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch3sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 3 enable checkbox
        self.ch3Enabled = IntVar()
        self.ch3enableframe = LabelFrame(self.adcch3frame, relief=FLAT)
        self.ch3enableframe.pack(fill=X, side=TOP)
        self.chk_ch3enable = Checkbutton(self.ch3enableframe,text="Enable",
                                         variable=self.ch3Enabled, command=self.enableControls)
        self.chk_ch3enable.pack(side=LEFT, anchor=W, padx=20)

        # channel 4 frame
        self.adcch4frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 4")
        self.adcch4frame.grid(row=2, column=0, padx=10, pady=10)

        # channel 4 name
        self.ch4nameframe = LabelFrame(self.adcch4frame, relief=FLAT)
        self.ch4nameframe.pack(fill=X, side=TOP)
        self.lbl_ch4name = Label(self.ch4nameframe,text="Name:")
        self.lbl_ch4name.pack(side=LEFT, anchor=W)   
        self.txt_ch4name = Entry(self.ch4nameframe)
        self.txt_ch4name.pack(side=LEFT, anchor=W)

        # channel 4 sensor type drown down list
        self.ch4sensortypeframe = LabelFrame(self.adcch4frame, relief= FLAT)
        self.ch4sensortypeframe.pack(fill=X, side=TOP)
        self.ch4sensortype = StringVar()
        self.ch4sensortypelist = ["pH", "raw"]
        self.ch4sensortype.set("pH") # default value
        self.lbl_ch4sensortype = Label(self.ch4sensortypeframe,text="Sensor Type:")
        self.lbl_ch4sensortype.pack(side=LEFT, anchor=W)    
        self.ch4sensortypemenu = OptionMenu(self.ch4sensortypeframe,self.ch4sensortype,*self.ch4sensortypelist)
        self.ch4sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch4sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 4 enable checkbox
        self.ch4Enabled = IntVar()
        self.ch4enableframe = LabelFrame(self.adcch4frame, relief=FLAT)
        self.ch4enableframe.pack(fill=X, side=TOP)
        self.chk_ch4enable = Checkbutton(self.ch4enableframe,text="Enable",
                                         variable=self.ch4Enabled, command=self.enableControls)
        self.chk_ch4enable.pack(side=LEFT, anchor=W, padx=20)

        # channel 5 frame
        self.adcch5frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 5")
        self.adcch5frame.grid(row=2, column=1, padx=10, pady=10)

        # channel 5 name
        self.ch5nameframe = LabelFrame(self.adcch5frame, relief=FLAT)
        self.ch5nameframe.pack(fill=X, side=TOP)
        self.lbl_ch5name = Label(self.ch5nameframe,text="Name:")
        self.lbl_ch5name.pack(side=LEFT, anchor=W)   
        self.txt_ch5name = Entry(self.ch5nameframe)
        self.txt_ch5name.pack(side=LEFT, anchor=W)

        # channel 5 sensor type drown down list
        self.ch5sensortypeframe = LabelFrame(self.adcch5frame, relief= FLAT)
        self.ch5sensortypeframe.pack(fill=X, side=TOP)
        self.ch5sensortype = StringVar()
        self.ch5sensortypelist = ["pH", "raw"]
        self.ch5sensortype.set("pH") # default value
        self.lbl_ch5sensortype = Label(self.ch5sensortypeframe,text="Sensor Type:")
        self.lbl_ch5sensortype.pack(side=LEFT, anchor=W)    
        self.ch5sensortypemenu = OptionMenu(self.ch5sensortypeframe,self.ch5sensortype,*self.ch5sensortypelist)
        self.ch5sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch5sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 5 enable checkbox
        self.ch5Enabled = IntVar()
        self.ch5enableframe = LabelFrame(self.adcch5frame, relief=FLAT)
        self.ch5enableframe.pack(fill=X, side=TOP)
        self.chk_ch5enable = Checkbutton(self.ch5enableframe,text="Enable",
                                         variable=self.ch5Enabled, command=self.enableControls)
        self.chk_ch5enable.pack(side=LEFT, anchor=W, padx=20)

        # channel 6 frame
        self.adcch6frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 6")
        self.adcch6frame.grid(row=3, column=0, padx=10, pady=10)

        # channel 6 name
        self.ch6nameframe = LabelFrame(self.adcch6frame, relief=FLAT)
        self.ch6nameframe.pack(fill=X, side=TOP)
        self.lbl_ch6name = Label(self.ch6nameframe,text="Name:")
        self.lbl_ch6name.pack(side=LEFT, anchor=W)   
        self.txt_ch6name = Entry(self.ch6nameframe)
        self.txt_ch6name.pack(side=LEFT, anchor=W)

        # channel 6 sensor type drown down list
        self.ch6sensortypeframe = LabelFrame(self.adcch6frame, relief= FLAT)
        self.ch6sensortypeframe.pack(fill=X, side=TOP)
        self.ch6sensortype = StringVar()
        self.ch6sensortypelist = ["pH", "raw"]
        self.ch6sensortype.set("pH") # default value
        self.lbl_ch6sensortype = Label(self.ch6sensortypeframe,text="Sensor Type:")
        self.lbl_ch6sensortype.pack(side=LEFT, anchor=W)    
        self.ch6sensortypemenu = OptionMenu(self.ch6sensortypeframe,self.ch6sensortype,*self.ch6sensortypelist)
        self.ch6sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch6sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 6 enable checkbox
        self.ch6Enabled = IntVar()
        self.ch6enableframe = LabelFrame(self.adcch6frame, relief=FLAT)
        self.ch6enableframe.pack(fill=X, side=TOP)
        self.chk_ch6enable = Checkbutton(self.ch6enableframe,text="Enable",
                                         variable=self.ch6Enabled, command=self.enableControls)
        self.chk_ch6enable.pack(side=LEFT, anchor=W, padx=20)

        # channel 7 frame
        self.adcch7frame = LabelFrame(self.adcframe, relief=GROOVE, text="Channel 7")
        self.adcch7frame.grid(row=3, column=1, padx=10, pady=10)

        # channel 7 name
        self.ch7nameframe = LabelFrame(self.adcch7frame, relief=FLAT)
        self.ch7nameframe.pack(fill=X, side=TOP)
        self.lbl_ch7name = Label(self.ch7nameframe,text="Name:")
        self.lbl_ch7name.pack(side=LEFT, anchor=W)   
        self.txt_ch7name = Entry(self.ch7nameframe)
        self.txt_ch7name.pack(side=LEFT, anchor=W)

        # channel 7 sensor type drown down list
        self.ch7sensortypeframe = LabelFrame(self.adcch7frame, relief= FLAT)
        self.ch7sensortypeframe.pack(fill=X, side=TOP)
        self.ch7sensortype = StringVar()
        self.ch7sensortypelist = ["pH", "raw"]
        self.ch7sensortype.set("pH") # default value
        self.lbl_ch7sensortype = Label(self.ch7sensortypeframe,text="Sensor Type:")
        self.lbl_ch7sensortype.pack(side=LEFT, anchor=W)    
        self.ch7sensortypemenu = OptionMenu(self.ch7sensortypeframe,self.ch7sensortype,*self.ch7sensortypelist)
        self.ch7sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.ch7sensortypemenu.pack(side=LEFT, anchor=W)

        # channel 7 enable checkbox
        self.ch7Enabled = IntVar()
        self.ch7enableframe = LabelFrame(self.adcch7frame, relief=FLAT)
        self.ch7enableframe.pack(fill=X, side=TOP)
        self.chk_ch7enable = Checkbutton(self.ch7enableframe,text="Enable",
                                         variable=self.ch7Enabled, command=self.enableControls)
        self.chk_ch7enable.pack(side=LEFT, anchor=W, padx=20)

        # read values from config file
        # Ch0 name
        #val = cfg_common.readINIfile("mcp3008", "ch0_name", "Unnamed")
        val = controller.downloadsettings("mcp3008", "ch0_name", "Unnamed")
        self.txt_ch0name.delete(0,END)
        self.txt_ch0name.insert(0,val)
        # Ch0 enabled
        #val = cfg_common.readINIfile("mcp3008", "ch0_enabled", "False")
        val = controller.downloadsettings("mcp3008", "ch0_enabled", "False")
        if str(val) == "True":
            self.chk_ch0enable.select()
        else:
            self.chk_ch0enable.deselect()
        # Ch0 type
        #val = cfg_common.readINIfile("mcp3008", "ch0_type", "pH")
        val = controller.downloadsettings("mcp3008", "ch0_type", "pH")
        self.ch0sensortype.set(val)
        

        # Ch1 name
        #val = cfg_common.readINIfile("mcp3008", "ch1_name", "Unnamed")
        val = controller.downloadsettings("mcp3008", "ch1_name", "Unnamed")
        self.txt_ch1name.delete(0,END)
        self.txt_ch1name.insert(0,val)
        #Ch1 enabled
        #val = cfg_common.readINIfile("mcp3008", "ch1_enabled", "False")
        val = controller.downloadsettings("mcp3008", "ch1_enabled", "False")
        if str(val) == "True":
            self.chk_ch1enable.select()
        else:
            self.chk_ch1enable.deselect()
        # Ch1 type
        #val = cfg_common.readINIfile("mcp3008", "ch1_type", "pH")
        val = controller.downloadsettings("mcp3008", "ch1_type", "pH")
        self.ch1sensortype.set(val)

        # Ch2 name
        val = controller.downloadsettings("mcp3008", "ch2_name", "Unnamed")
        self.txt_ch2name.delete(0,END)
        self.txt_ch2name.insert(0,val)
        #Ch2 enabled
        val = controller.downloadsettings("mcp3008", "ch2_enabled", "False")
        if str(val) == "True":
            self.chk_ch2enable.select()
        else:
            self.chk_ch2enable.deselect()
        # Ch2 type
        val = controller.downloadsettings("mcp3008", "ch2_type", "pH")
        self.ch2sensortype.set(val)

        # Ch3 name
        val = controller.downloadsettings("mcp3008", "ch3_name", "Unnamed")
        self.txt_ch3name.delete(0,END)
        self.txt_ch3name.insert(0,val)
        #Ch3 enabled
        val = controller.downloadsettings("mcp3008", "ch3_enabled", "False")
        if str(val) == "True":
            self.chk_ch3enable.select()
        else:
            self.chk_ch3enable.deselect()
        # Ch3 type
        val = controller.downloadsettings("mcp3008", "ch3_type", "pH")
        self.ch3sensortype.set(val)

        # Ch4 name
        val = controller.downloadsettings("mcp3008", "ch4_name", "Unnamed")
        self.txt_ch4name.delete(0,END)
        self.txt_ch4name.insert(0,val)
        #Ch4 enabled
        val = controller.downloadsettings("mcp3008", "ch4_enabled", "False")
        if str(val) == "True":
            self.chk_ch4enable.select()
        else:
            self.chk_ch4enable.deselect()
        # Ch4 type
        val = controller.downloadsettings("mcp3008", "ch4_type", "pH")
        self.ch4sensortype.set(val)

        # Ch5 name
        val = controller.downloadsettings("mcp3008", "ch5_name", "Unnamed")
        self.txt_ch5name.delete(0,END)
        self.txt_ch5name.insert(0,val)
        #Ch5 enabled
        val = controller.downloadsettings("mcp3008", "ch5_enabled", "False")
        if str(val) == "True":
            self.chk_ch5enable.select()
        else:
            self.chk_ch5enable.deselect()
        # Ch5 type
        val = controller.downloadsettings("mcp3008", "ch5_type", "pH")
        self.ch5sensortype.set(val)

        # Ch6 name
        val = controller.downloadsettings("mcp3008", "ch6_name", "Unnamed")
        self.txt_ch6name.delete(0,END)
        self.txt_ch6name.insert(0,val)
        #Ch6 enabled
        val = controller.downloadsettings("mcp3008", "ch6_enabled", "False")
        if str(val) == "True":
            self.chk_ch6enable.select()
        else:
            self.chk_ch6enable.deselect()
        # Ch6 type
        val = controller.downloadsettings("mcp3008", "ch6_type", "pH")
        self.ch6sensortype.set(val)

        # Ch7 name
        val = controller.downloadsettings("mcp3008", "ch7_name", "Unnamed")
        self.txt_ch7name.delete(0,END)
        self.txt_ch7name.insert(0,val)
        #Ch7 enabled
        val = controller.downloadsettings("mcp3008", "ch7_enabled", "False")
        if str(val) == "True":
            self.chk_ch7enable.select()
        else:
            self.chk_ch7enable.deselect()
        # Ch7 type
        val = controller.downloadsettings("mcp3008", "ch7_type", "pH")
        self.ch7sensortype.set(val)

        # enable/disable controls
        self.enableControls()

    def enableControls(self):
        # ch 0
        if self.ch0Enabled.get() == True:
            self.lbl_ch0name.config(state='normal')
            self.txt_ch0name.config(state='normal')
            self.lbl_ch0sensortype.config(state='normal')
            self.ch0sensortypemenu.config(state='normal')
        else:
            self.lbl_ch0name.config(state='disabled')
            self.txt_ch0name.config(state='disabled')
            self.lbl_ch0sensortype.config(state='disabled')
            self.ch0sensortypemenu.config(state='disabled')
        # ch 1
        if self.ch1Enabled.get() == True:
            self.lbl_ch1name.config(state='normal')
            self.txt_ch1name.config(state='normal')
            self.lbl_ch1sensortype.config(state='normal')
            self.ch1sensortypemenu.config(state='normal')
        else:
            self.lbl_ch1name.config(state='disabled')
            self.txt_ch1name.config(state='disabled')
            self.lbl_ch1sensortype.config(state='disabled')
            self.ch1sensortypemenu.config(state='disabled')
        # ch 2
        if self.ch2Enabled.get() == True:
            self.lbl_ch2name.config(state='normal')
            self.txt_ch2name.config(state='normal')
            self.lbl_ch2sensortype.config(state='normal')
            self.ch2sensortypemenu.config(state='normal')
        else:
            self.lbl_ch2name.config(state='disabled')
            self.txt_ch2name.config(state='disabled')
            self.lbl_ch2sensortype.config(state='disabled')
            self.ch2sensortypemenu.config(state='disabled')
        # ch 3
        if self.ch3Enabled.get() == True:
            self.lbl_ch3name.config(state='normal')
            self.txt_ch3name.config(state='normal')
            self.lbl_ch3sensortype.config(state='normal')
            self.ch3sensortypemenu.config(state='normal')
        else:
            self.lbl_ch3name.config(state='disabled')
            self.txt_ch3name.config(state='disabled')
            self.lbl_ch3sensortype.config(state='disabled')
            self.ch3sensortypemenu.config(state='disabled')
        # ch 4
        if self.ch4Enabled.get() == True:
            self.lbl_ch4name.config(state='normal')
            self.txt_ch4name.config(state='normal')
            self.lbl_ch4sensortype.config(state='normal')
            self.ch4sensortypemenu.config(state='normal')
        else:
            self.lbl_ch4name.config(state='disabled')
            self.txt_ch4name.config(state='disabled')
            self.lbl_ch4sensortype.config(state='disabled')
            self.ch4sensortypemenu.config(state='disabled')
        # ch 5
        if self.ch5Enabled.get() == True:
            self.lbl_ch5name.config(state='normal')
            self.txt_ch5name.config(state='normal')
            self.lbl_ch5sensortype.config(state='normal')
            self.ch5sensortypemenu.config(state='normal')
        else:
            self.lbl_ch5name.config(state='disabled')
            self.txt_ch5name.config(state='disabled')
            self.lbl_ch5sensortype.config(state='disabled')
            self.ch5sensortypemenu.config(state='disabled')

        # ch 6
        if self.ch6Enabled.get() == True:
            self.lbl_ch6name.config(state='normal')
            self.txt_ch6name.config(state='normal')
            self.lbl_ch6sensortype.config(state='normal')
            self.ch6sensortypemenu.config(state='normal')
        else:
            self.lbl_ch6name.config(state='disabled')
            self.txt_ch6name.config(state='disabled')
            self.lbl_ch6sensortype.config(state='disabled')
            self.ch6sensortypemenu.config(state='disabled')

        # ch 7
        if self.ch7Enabled.get() == True:
            self.lbl_ch7name.config(state='normal')
            self.txt_ch7name.config(state='normal')
            self.lbl_ch7sensortype.config(state='normal')
            self.ch7sensortypemenu.config(state='normal')
        else:
            self.lbl_ch7name.config(state='disabled')
            self.txt_ch7name.config(state='disabled')
            self.lbl_ch7sensortype.config(state='disabled')
            self.ch7sensortypemenu.config(state='disabled')

            

    def saveChanges(self):
        # Channel 0
##        if cfg_common.writeINIfile('mcp3008', 'ch0_name', str(self.txt_ch0name.get())) != True:
##             messagebox.showerror("Analog Settings",
##                                 "Error: Could not save changes! \nNew configuration not saved.")
##        
        if self.ch0Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"
##            
##        if cfg_common.writeINIfile('mcp3008', 'ch0_enabled', str(chkstate)) != True:
##           messagebox.showerror("Analog Settings",
##                                 "Error: Could not save changes! \nNew configuration not saved.")
##        
##        if cfg_common.writeINIfile('mcp3008', 'ch0_type', str(self.ch0sensortype.get())) != True:
##           messagebox.showerror("Analog Settings",
##                                 "Error: Could not save changes! \nNew configuration not saved.")
           
        self.controller.uploadsettings('mcp3008', 'ch0_name', str(self.txt_ch0name.get()))
        self.controller.uploadsettings('mcp3008', 'ch0_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch0_type', str(self.ch0sensortype.get()))
        

        # Channel 1
##        if cfg_common.writeINIfile('mcp3008', 'ch1_name', str(self.txt_ch1name.get())) != True:
##             messagebox.showerror("Analog Settings",
##                                 "Error: Could not save changes! \nNew configuration not saved.")
##
        if self.ch1Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"
##            
##        if cfg_common.writeINIfile('mcp3008', 'ch1_enabled', str(chkstate)) != True:
##           messagebox.showerror("Analog Settings",
##                                 "Error: Could not save changes! \nNew configuration not saved.")
##
##        if cfg_common.writeINIfile('mcp3008', 'ch1_type', str(self.ch1sensortype.get())) != True:
##           messagebox.showerror("Analog Settings",
##                                 "Error: Could not save changes! \nNew configuration not saved.")

        self.controller.uploadsettings('mcp3008', 'ch1_name', str(self.txt_ch1name.get()))
        self.controller.uploadsettings('mcp3008', 'ch1_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch1_type', str(self.ch1sensortype.get()))

        # Channel 2
        if self.ch2Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        self.controller.uploadsettings('mcp3008', 'ch2_name', str(self.txt_ch2name.get()))
        self.controller.uploadsettings('mcp3008', 'ch2_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch2_type', str(self.ch1sensortype.get()))
        

        # Channel 3
        if self.ch3Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        self.controller.uploadsettings('mcp3008', 'ch3_name', str(self.txt_ch3name.get()))
        self.controller.uploadsettings('mcp3008', 'ch3_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch3_type', str(self.ch3sensortype.get()))

        # Channel 4
        if self.ch4Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        self.controller.uploadsettings('mcp3008', 'ch4_name', str(self.txt_ch4name.get()))
        self.controller.uploadsettings('mcp3008', 'ch4_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch4_type', str(self.ch4sensortype.get()))

        # Channel 5
        if self.ch5Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        self.controller.uploadsettings('mcp3008', 'ch5_name', str(self.txt_ch5name.get()))
        self.controller.uploadsettings('mcp3008', 'ch5_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch5_type', str(self.ch5sensortype.get()))

        # Channel 6
        if self.ch6Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        self.controller.uploadsettings('mcp3008', 'ch6_name', str(self.txt_ch6name.get()))
        self.controller.uploadsettings('mcp3008', 'ch6_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch6_type', str(self.ch6sensortype.get()))

        # Channel 7
        if self.ch7Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        self.controller.uploadsettings('mcp3008', 'ch7_name', str(self.txt_ch7name.get()))
        self.controller.uploadsettings('mcp3008', 'ch7_enabled', str(chkstate))
        self.controller.uploadsettings('mcp3008', 'ch7_type', str(self.ch7sensortype.get()))
        


        
        
