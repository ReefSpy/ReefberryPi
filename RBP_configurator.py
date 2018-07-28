import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import configparser
import cfg_tempprobes
import cfg_global
import cfg_outlets
import cfg_environmental
import cfg_switches
import cfg_ph

LARGE_FONT= ("Verdana", 12)

PAGE_GLOBAL     = 0
PAGE_TEMPPROBES = 1
PAGE_OUTLETS    = 2
PAGE_ENVIRO     = 3
PAGE_SWITCHES   = 4
PAGE_PHPROBES   = 5


class RBP_configurator(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        #self.iconbitmap('@images/reefberrypi_logo.xbm')
        tk.Tk.wm_title(self, "Reefberry Pi Configurator")

##        #create a menubar
##        menubar = Menu(self)
##
##        # create a pulldown menu, and add it to the menu bar
##        filemenu = Menu(menubar, tearoff=0)
##        filemenu.add_command(label="Exit", command=self.quit)
##        menubar.add_cascade(label="File", menu=filemenu)
##        # display the menu
##        self.config(menu=menubar)

        # create a toolbar
        self.ConfigSelection = IntVar() 
        toolbarframe = tk.Frame(self, relief=tk.FLAT)
        toolbarframe.pack(side=TOP, fill=tk.X)

        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (cfg_global.PageGlobal,
                  cfg_tempprobes.PageTempProbes,
                  cfg_outlets.PageOutlets,
                  cfg_environmental.PageEnvironmental,
                  cfg_switches.PageSwitches,
                  cfg_ph.PagePHProbes):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(cfg_global.PageGlobal)

        # button for global settings
        self.img_global = PhotoImage(file="images/globe-64.png")
        rdoGlobal = Radiobutton(toolbarframe, text="Global", variable=self.ConfigSelection,
                                    image=self.img_global, value=0, indicatoron=0,
                                    compound=TOP, width=90, command=self.change_tab)
        rdoGlobal.pack(side=LEFT)

        # button for temperature probes
        self.img_temperature = PhotoImage(file="images/temperature-64.png")
        rdoTempProbes = Radiobutton(toolbarframe, text="Temp Probes", variable=self.ConfigSelection,
                                    image=self.img_temperature, value=1, indicatoron=0,
                                    compound=TOP, width=90, command=self.change_tab)
        rdoTempProbes.pack(side=LEFT)

        # button for outlets
        self.img_outlets = PhotoImage(file="images/socket-64.png")
        rdoOutlets = Radiobutton(toolbarframe, text="Outlets", variable=self.ConfigSelection,
                                 image=self.img_outlets, value=2, indicatoron=0,
                                 compound=TOP, width=90, command=self.change_tab)
        rdoOutlets.pack(side=LEFT)

        # button for environmental probes
        self.img_environmental = PhotoImage(file="images/cooling-room-64.png")
        rdoEnvironmental = Radiobutton(toolbarframe, text="Environmental", variable=self.ConfigSelection,
                                       image=self.img_environmental, value=3, indicatoron=0,
                                       compound=TOP, width=90, command=self.change_tab)
        rdoEnvironmental.pack(side=LEFT)

        # button for switches
        self.img_switches = PhotoImage(file="images/switch-on-64.png")
        rdoSwitches = Radiobutton(toolbarframe, text="Switches", variable=self.ConfigSelection,
                                  image=self.img_switches, value=4, indicatoron=0,
                                  compound=TOP, width=90, command=self.change_tab)
        rdoSwitches.pack(side=LEFT)

        # button for PH probes
        self.img_ph = PhotoImage(file="images/experiment-64.png")
        rdoph = Radiobutton(toolbarframe, text="pH Probes", variable=self.ConfigSelection,
                            image=self.img_ph, value=5, indicatoron=0,
                            compound=TOP, width=90, command=self.change_tab)
        rdoph.pack(side=LEFT)

    def change_tab(selection):
        tab = selection.ConfigSelection.get()
        if tab == PAGE_GLOBAL:
            selection.show_frame(cfg_global.PageGlobal)
        elif tab == PAGE_TEMPPROBES:
            selection.show_frame(cfg_tempprobes.PageTempProbes)
        elif tab == PAGE_OUTLETS:
            selection.show_frame(cfg_outlets.PageOutlets)
        elif tab == PAGE_ENVIRO:
            selection.show_frame(cfg_environmental.PageEnvironmental)
        elif tab == PAGE_SWITCHES:
            selection.show_frame(cfg_switches.PageSwitches)
        elif tab == PAGE_PHPROBES:
            selection.show_frame(cfg_ph.PagePHProbes)
        
    def show_frame(self, cont):
        print("show_frame" + str(cont))
        frame = self.frames[cont]
        frame.tkraise()

root = RBP_configurator()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

##    outletwin = tk.Toplevel()
##    outletwin.transient()
##    outletwin.grab_set()


##########################
##
###Create the Tkinter application GUI
##root = Tk()
##root.wm_title("Reefberry Pi - Configurator")
##
###read in config file
###config = configparser.ConfigParser()
###config.read('ReefberryPi.ini')
###print(config.sections())
##
##def readinifile(section,key):
##    #read in config file
##    config = configparser.ConfigParser()
##    config.read('ReefberryPi.ini')
##    print(config.sections())
##    return config[section][key]
##
##def select_controltype(control):
##    print("you selected control type: " + control)
##    try:
##        root.frame_cfg.destroy()
##        print("destroy")
##    except:
##        pass
##    ###########################################################################
##    # frame for outlet configuration
##    ###########################################################################
##    root.frame_cfg = LabelFrame(root, text="Configuration", relief= RAISED)
##    root.frame_cfg.pack(fill=X, side=TOP)
##
##    # dropdown list for fallback
##    root.fallbackframe = LabelFrame(root.frame_cfg, relief= FLAT)
##    root.fallbackframe.pack(fill=X, side=TOP)
##    fallbackchoice = StringVar()
##    fallbacklist = ["ON", "OFF"]
##    fallbackchoice.set("ON") # default value
##    root.lbl_fallback = Label(root.fallbackframe,text="Fallback:")
##    root.lbl_fallback.pack(side=LEFT, anchor=W)    
##    root.fallbackmenu = OptionMenu(root.fallbackframe,fallbackchoice,*fallbacklist)
##    root.fallbackmenu.configure(indicatoron=True, relief=GROOVE)
##    root.fallbackmenu.pack(side=LEFT, anchor=W)
##
##    if control=="Heater":
##        #drop down list for probes
##        root.probeframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.probeframe.pack(fill=X, side=TOP)
##        probechoice = StringVar()
##        probelist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
##        probechoice.set("ds18b20_1") # default value
##        root.lbl_probe = Label(root.probeframe,text="Probe Name:")
##        root.lbl_probe.pack(side=LEFT, anchor=W)    
##        root.probemenu = OptionMenu(root.probeframe,probechoice,*probelist)
##        root.probemenu.configure(indicatoron=True, relief=GROOVE)
##        root.probemenu.pack(side=LEFT, anchor=W)
##        # spinbox for on temperature
##        root.ontempframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.ontempframe.pack(fill=X, side=TOP)
##        root.lbl_ontemp = Label(root.ontempframe,text="On Temperature:")
##        root.lbl_ontemp.pack(side=LEFT, anchor=W)
##        root.spn_ontemp = Spinbox(root.ontempframe, from_=32,to=212, increment=.1)
##        root.spn_ontemp.pack(side=LEFT, anchor=W)
##        # spinbox for off temperature
##        root.offtempframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.offtempframe.pack(fill=X, side=TOP)
##        root.lbl_offtemp = Label(root.offtempframe,text="Off Temperature:")
##        root.lbl_offtemp.pack(side=LEFT, anchor=W)
##        root.spn_offtemp = Spinbox(root.offtempframe, from_=32,to=212, increment=.1)
##        root.spn_offtemp.pack(side=LEFT, anchor=W)
##    elif control=="Always":
##        #drop dwn list for Always
##        root.stateframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.stateframe.pack(fill=X, side=TOP)
##        statechoice = StringVar()
##        statelist = ["ON", "OFF"]
##        statechoice.set("ON") # default value
##        root.lbl_state = Label(root.stateframe,text="State:")
##        root.lbl_state.pack(side=LEFT, anchor=W)    
##        root.statemenu = OptionMenu(root.stateframe,statechoice,*statelist)
##        root.statemenu.configure(indicatoron=True, relief=GROOVE)
##        root.statemenu.pack(side=LEFT, anchor=W)
##    elif control=="Light":
##        # editbox for on time
##        root.ontimeframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.ontimeframe.pack(fill=X, side=TOP)
##        root.lbl_ontime = Label(root.ontimeframe,text="On Time:")
##        root.lbl_ontime.pack(side=LEFT, anchor=W)
##        root.edt_ontime = Entry(root.ontimeframe)
##        root.edt_ontime.pack(side=LEFT, anchor=W)
##        # editbox for off time
##        root.offtimeframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.offtimeframe.pack(fill=X, side=TOP)
##        root.lbl_offtime = Label(root.offtimeframe,text="Off Time:")
##        root.lbl_offtime.pack(side=LEFT, anchor=W)
##        root.edt_offtime = Entry(root.offtimeframe)
##        root.edt_offtime.pack(side=LEFT, anchor=W)
##        #drop dwn list for shutdown probe
##        root.shutdownframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.shutdownframe.pack(fill=X, side=TOP)
##        shutdownchoice = StringVar()
##        shutdownlist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
##        shutdownchoice.set("ds18b20_1") # default value
##        root.lbl_shutdownprobe = Label(root.shutdownframe,text="Shutdown Probe:")
##        root.lbl_shutdownprobe.pack(side=LEFT, anchor=W)    
##        root.shutdownmenu = OptionMenu(root.shutdownframe,shutdownchoice,*shutdownlist)
##        root.shutdownmenu.configure(indicatoron=True, relief=GROOVE)
##        root.shutdownmenu.pack(side=LEFT, anchor=W)
##        # spinbox for shutdown temperature
##        root.shutdowntempframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.shutdowntempframe.pack(fill=X, side=TOP)
##        root.lbl_shutdowntemp = Label(root.shutdowntempframe,text="Shutdown Temperature:")
##        root.lbl_shutdowntemp.pack(side=LEFT, anchor=W)
##        root.spn_shutdowntemp = Spinbox(root.shutdowntempframe, from_=32,to=212, increment=.1)
##        root.spn_shutdowntemp.pack(side=LEFT, anchor=W)
##        # editbox for hysteresis
##        root.hysteresisframe = LabelFrame(root.frame_cfg, relief= FLAT)
##        root.hysteresisframe.pack(fill=X, side=TOP)
##        root.lbl_hysteresis = Label(root.hysteresisframe,text="Hysteresis:")
##        root.lbl_hysteresis.pack(side=LEFT, anchor=W)
##        root.edt_hysteresis = Entry(root.hysteresisframe)
##        root.edt_hysteresis.pack(side=LEFT, anchor=W)
##        
##    
##def select_outlet(outlet):
##    print ("you selected outlet: " + outletchoice.get())
##    try:
##        root.frame_outlet.destroy()
##        root.frame_cfg.destroy()
##        print("destroy")
##    except:
##        pass
##
##    
##    ###########################################################################
##    # generic outlet info
##    ###########################################################################
##
##    # drop down list for control type
##    controltypechoice = StringVar()
##    controltypelist = ["Always", "Heater", "Light"]
##    controltypechoice.set("Always") # default value
##
##    # outlet frame
##    root.frame_outlet = LabelFrame(root, text="Outlet", relief= RAISED)
##    root.frame_outlet.pack(fill=X, side=TOP)
##
##    # outlet name
##    root.outletnameframe = LabelFrame(root.frame_outlet, relief= FLAT)
##    root.outletnameframe.pack(fill=X, side=TOP)
##    root.lbl_outletname = Label(root.outletnameframe,text="Name:")
##    root.lbl_outletname.pack(side=LEFT, anchor=W)
##    root.txt_outletname = Entry(root.outletnameframe)
##    root.txt_outletname.pack(side=LEFT, anchor=W)
##
##    # control type
##    root.controltypeframe = LabelFrame(root.frame_outlet, relief= FLAT)
##    root.controltypeframe.pack(fill=X, side=TOP)
##    root.lbl_controltype = Label(root.controltypeframe, text="Control Type:")
##    root.lbl_controltype.pack(side=LEFT, anchor=W)
##    root.controltypemenu = OptionMenu(root.controltypeframe,controltypechoice,*controltypelist,
##                            command=select_controltype)
##    root.controltypemenu.configure(indicatoron=True, relief=GROOVE)
##    root.controltypemenu.pack(side=LEFT, anchor=W)
##
##    # logging
##    root.logframe = LabelFrame(root.frame_outlet, relief= FLAT)
##    root.logframe.pack(fill=X, side=TOP)
##    root.lbl_log = Label(root.logframe,text="Log:")
##    root.lbl_log.pack(side=LEFT, anchor=W)
##    root.chk_log = Checkbutton(root.logframe, text="Enable")
##    root.chk_log.pack(side=LEFT, anchor=W)
##    
##    ###########################################################################
##    # frame for outlet configuration
##    ###########################################################################
##    root.frame_cfg = LabelFrame(root, text="Configuration", relief= RAISED)
##    root.frame_cfg.pack(fill=X, side=TOP)
##
##    # fallback
##    #root.lbl_fallback = Label(root.frame_cfg,text="Fallback:")
##    #root.lbl_fallback.pack(side=TOP, anchor=W)
##    #root.txt_fallback = Entry(root.frame_cfg)
##    #root.txt_fallback.pack(side=TOP, anchor=W)
##
##    if outlet == "Outlet 1":
##        root.txt_outletname.delete(0, END)
##        root.txt_outletname.insert(0, readinifile("outlet_1","name"))
##    elif outlet == "Outlet 2":
##        root.txt_outletname.delete(0, END)
##        root.txt_outletname.insert(0, readinifile("outlet_2","name"))
##    elif outlet == "Outlet 3":
##        root.txt_outletname.delete(0, END)
##        root.txt_outletname.insert(0, readinifile("outlet_3","name"))
##    elif outlet == "Outlet 4":
##        root.txt_outletname.delete(0, END)
##        root.txt_outletname.insert(0, readinifile("outlet_4","name"))
##    
##    
##
### top frame for toolbar
##root.frame_toolbar = LabelFrame(root, relief= FLAT)
##root.frame_toolbar.pack(fill=X, side=TOP)
##        
### drop down list for outlets
##outletchoice = StringVar()
##outletlist = ["Outlet 1","Outlet 2","Outlet 3","Outlet 4"]
##outletchoice.set("Outlet 1") # default value
##
##outletmenu = OptionMenu(root.frame_toolbar,outletchoice,*outletlist,
##                                   command=select_outlet)
##outletimg=PhotoImage(file="images/socket-24.png")
##outletmenu.configure(indicatoron=True, compound='left', image=outletimg, relief=FLAT)
##
##outletmenu.pack(side=LEFT, anchor=W)
##
##select_outlet("Outlet 1")
##
##saveimg=PhotoImage(file="images/save-24.png")
##btn_save = Button(root.frame_toolbar, text="Save", image=saveimg, compound='left', relief=FLAT)
##btn_save.pack(side=LEFT, anchor=W)
##
##root.mainloop()
