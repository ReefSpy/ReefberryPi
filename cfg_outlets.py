import tkinter as tk
from tkinter import *
from tkinter import ttk
import configparser

LARGE_FONT= ("Verdana", 12)

class PageOutlets(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Outlet Configuration", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)
        # top frame for toolbar
        self.frame_toolbar = LabelFrame(self, relief= FLAT)
        self.frame_toolbar.pack(fill=X, side=TOP)
                
        # drop down list for outlets
        self.outletchoice = StringVar()
        self.outletlist = ["Outlet 1","Outlet 2","Outlet 3","Outlet 4"]
        self.outletchoice.set("Outlet 1") # default value

        self.outletmenu = OptionMenu(self.frame_toolbar,self.outletchoice,*self.outletlist,
                                           command=self.select_outlet)
        self.outletimg=PhotoImage(file="images/socket-24.png")
        self.outletmenu.configure(indicatoron=True, compound='left', image=self.outletimg, relief=FLAT)

        self.outletmenu.pack(side=LEFT, anchor=W)

        self.select_outlet("Outlet 1")

        self.saveimg=PhotoImage(file="images/upload-to-cloud-24.png")
        self.btn_save = Button(self.frame_toolbar, text="Save", image=self.saveimg, compound='left', relief=FLAT)
        self.btn_save.pack(side=LEFT, anchor=W)

        # read in config file
        config = configparser.ConfigParser()
        config.read('ReefberryPi.ini')
        print(config.sections())

    def readinifile(self,section,key):
        # read in config file
        config = configparser.ConfigParser()
        config.read('ReefberryPi.ini')
        print(config.sections())
        return config[section][key]
    
    def select_controltype(self,control):
        print("you selected control type: " + control)
        try:
            self.frame_cfg.destroy()
            print("destroy")
        except:
            pass
        ###########################################################################
        # frame for outlet configuration
        ###########################################################################
        self.frame_cfg = LabelFrame(self, text="Configuration", relief= RAISED)
        self.frame_cfg.pack(fill=X, side=TOP)

        # dropdown list for fallback
        self.fallbackframe = LabelFrame(self.frame_cfg, relief= FLAT)
        self.fallbackframe.pack(fill=X, side=TOP)
        fallbackchoice = StringVar()
        fallbacklist = ["ON", "OFF"]
        fallbackchoice.set("ON") # default value
        self.lbl_fallback = Label(self.fallbackframe,text="Fallback:")
        self.lbl_fallback.pack(side=LEFT, anchor=W)    
        self.fallbackmenu = OptionMenu(self.fallbackframe,fallbackchoice,*fallbacklist)
        self.fallbackmenu.configure(indicatoron=True, relief=GROOVE)
        self.fallbackmenu.pack(side=LEFT, anchor=W)

        ##
        if control=="Heater":
            #drop down list for probes
            self.probeframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.probeframe.pack(fill=X, side=TOP)
            probechoice = StringVar()
            probelist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
            probechoice.set("ds18b20_1") # default value
            self.lbl_probe = Label(self.probeframe,text="Probe Name:")
            self.lbl_probe.pack(side=LEFT, anchor=W)    
            self.probemenu = OptionMenu(self.probeframe,probechoice,*probelist)
            self.probemenu.configure(indicatoron=True, relief=GROOVE)
            self.probemenu.pack(side=LEFT, anchor=W)
            # spinbox for on temperature
            self.ontempframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.ontempframe.pack(fill=X, side=TOP)
            self.lbl_ontemp = Label(self.ontempframe,text="On Temperature:")
            self.lbl_ontemp.pack(side=LEFT, anchor=W)
            self.spn_ontemp = Spinbox(self.ontempframe, from_=32,to=212, increment=.1)
            self.spn_ontemp.pack(side=LEFT, anchor=W)
            # spinbox for off temperature
            self.offtempframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.offtempframe.pack(fill=X, side=TOP)
            self.lbl_offtemp = Label(self.offtempframe,text="Off Temperature:")
            self.lbl_offtemp.pack(side=LEFT, anchor=W)
            self.spn_offtemp = Spinbox(self.offtempframe, from_=32,to=212, increment=.1)
            self.spn_offtemp.pack(side=LEFT, anchor=W)
        elif control=="Always":
            #drop dwn list for Always
            self.stateframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.stateframe.pack(fill=X, side=TOP)
            statechoice = StringVar()
            statelist = ["ON", "OFF"]
            statechoice.set("ON") # default value
            self.lbl_state = Label(self.stateframe,text="State:")
            self.lbl_state.pack(side=LEFT, anchor=W)    
            self.statemenu = OptionMenu(self.stateframe,statechoice,*statelist)
            self.statemenu.configure(indicatoron=True, relief=GROOVE)
            self.statemenu.pack(side=LEFT, anchor=W)
        elif control=="Light":
            # editbox for on time
            self.ontimeframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.ontimeframe.pack(fill=X, side=TOP)
            self.lbl_ontime = Label(self.ontimeframe,text="On Time:")
            self.lbl_ontime.pack(side=LEFT, anchor=W)
            self.edt_ontime = Entry(self.ontimeframe)
            self.edt_ontime.pack(side=LEFT, anchor=W)
            # editbox for off time
            self.offtimeframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.offtimeframe.pack(fill=X, side=TOP)
            self.lbl_offtime = Label(self.offtimeframe,text="Off Time:")
            self.lbl_offtime.pack(side=LEFT, anchor=W)
            self.edt_offtime = Entry(self.offtimeframe)
            self.edt_offtime.pack(side=LEFT, anchor=W)
            #drop dwn list for shutdown probe
            self.shutdownframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.shutdownframe.pack(fill=X, side=TOP)
            shutdownchoice = StringVar()
            shutdownlist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
            shutdownchoice.set("ds18b20_1") # default value
            self.lbl_shutdownprobe = Label(self.shutdownframe,text="Shutdown Probe:")
            self.lbl_shutdownprobe.pack(side=LEFT, anchor=W)    
            self.shutdownmenu = OptionMenu(self.shutdownframe,shutdownchoice,*shutdownlist)
            self.shutdownmenu.configure(indicatoron=True, relief=GROOVE)
            self.shutdownmenu.pack(side=LEFT, anchor=W)
            # spinbox for shutdown temperature
            self.shutdowntempframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.shutdowntempframe.pack(fill=X, side=TOP)
            self.lbl_shutdowntemp = Label(self.shutdowntempframe,text="Shutdown Temperature:")
            self.lbl_shutdowntemp.pack(side=LEFT, anchor=W)
            self.spn_shutdowntemp = Spinbox(self.shutdowntempframe, from_=32,to=212, increment=.1)
            self.spn_shutdowntemp.pack(side=LEFT, anchor=W)
            # editbox for hysteresis
            self.hysteresisframe = LabelFrame(self.frame_cfg, relief= FLAT)
            self.hysteresisframe.pack(fill=X, side=TOP)
            self.lbl_hysteresis = Label(self.hysteresisframe,text="Hysteresis:")
            self.lbl_hysteresis.pack(side=LEFT, anchor=W)
            self.edt_hysteresis = Entry(self.hysteresisframe)
            self.edt_hysteresis.pack(side=LEFT, anchor=W)

    def select_outlet(self, outlet):
        print ("you selected outlet: " + self.outletchoice.get())
        try:
            self.frame_outlet.destroy()
            self.frame_cfg.destroy()
            print("destroy")
        except:
            pass

        ###########################################################################
        # generic outlet info
        ###########################################################################

        # drop down list for control type
        self.controltypechoice = StringVar()
        self.controltypelist = ["Always", "Heater", "Light"]
        self.controltypechoice.set("Always") # default value

        # outlet frame
        self.frame_outlet = LabelFrame(self, text="Outlet", relief= RAISED)
        self.frame_outlet.pack(fill=X, side=TOP)

        # outlet name
        self.outletnameframe = LabelFrame(self.frame_outlet, relief= FLAT)
        self.outletnameframe.pack(fill=X, side=TOP)
        self.lbl_outletname = Label(self.outletnameframe,text="Name:")
        self.lbl_outletname.pack(side=LEFT, anchor=W)
        self.txt_outletname = Entry(self.outletnameframe)
        self.txt_outletname.pack(side=LEFT, anchor=W)

        # control type
        self.controltypeframe = LabelFrame(self.frame_outlet, relief= FLAT)
        self.controltypeframe.pack(fill=X, side=TOP)
        self.lbl_controltype = Label(self.controltypeframe, text="Control Type:")
        self.lbl_controltype.pack(side=LEFT, anchor=W)
        self.controltypemenu = OptionMenu(self.controltypeframe,self.controltypechoice,*self.controltypelist,
                                command=self.select_controltype)
        self.controltypemenu.configure(indicatoron=True, relief=GROOVE)
        self.controltypemenu.pack(side=LEFT, anchor=W)

        # logging
        self.logframe = LabelFrame(self.frame_outlet, relief= FLAT)
        self.logframe.pack(fill=X, side=TOP)
        self.lbl_log = Label(self.logframe,text="Log:")
        self.lbl_log.pack(side=LEFT, anchor=W)
        self.chk_log = Checkbutton(self.logframe, text="Enable")
        self.chk_log.pack(side=LEFT, anchor=W)
        
        ###########################################################################
        # frame for outlet configuration
        ###########################################################################
        self.frame_cfg = LabelFrame(self, text="Configuration", relief= RAISED)
        self.frame_cfg.pack(fill=X, side=TOP)

        # fallback
        #self.lbl_fallback = Label(self.frame_cfg,text="Fallback:")
        #self.lbl_fallback.pack(side=TOP, anchor=W)
        #self.txt_fallback = Entry(self.frame_cfg)
        #self.txt_fallback.pack(side=TOP, anchor=W)

        if outlet == "Outlet 1":
            self.txt_outletname.delete(0, END)
            self.txt_outletname.insert(0, self.readinifile("outlet_1","name"))
        elif outlet == "Outlet 2":
            self.txt_outletname.delete(0, END)
            self.txt_outletname.insert(0, self.readinifile("outlet_2","name"))
        elif outlet == "Outlet 3":
            self.txt_outletname.delete(0, END)
            self.txt_outletname.insert(0, self.readinifile("outlet_3","name"))
        elif outlet == "Outlet 4":
            self.txt_outletname.delete(0, END)
            self.txt_outletname.insert(0, self.readinifile("outlet_4","name"))
        
        

             


    
