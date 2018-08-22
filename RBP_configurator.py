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
import cfg_analog
import cfg_feedtimers
import cfg_pwm
import cfg_common
import cfg_alerts

LARGE_FONT= ("Verdana", 12)

PAGE_GLOBAL     = 0
PAGE_TEMPPROBES = 1
PAGE_OUTLETS    = 2
PAGE_ENVIRO     = 3
PAGE_SWITCHES   = 4
PAGE_ANALOG     = 5
PAGE_FEEDTIMERS = 6
PAGE_PWM        = 7
PAGE_ALERTS     = 8


class RBP_configurator(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        #self.iconbitmap('@images/reefberrypi_logo.xbm')
        tk.Tk.wm_title(self, "Reefberry Pi Configurator")

        # check if config file exists, if not it will make one
        cfg_common.checkifconfigexists()
        
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
                  cfg_analog.PageAnalogProbes,
                  cfg_feedtimers.PageFeedTimers,
                  cfg_pwm.PagePWM,
                  cfg_alerts.PageAlerts):

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
        self.img_environmental = PhotoImage(file="images/heating-room-64.png")
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

        # button for analog probes
        self.img_analog = PhotoImage(file="images/sine-64.png")
        rdoph = Radiobutton(toolbarframe, text="Analog Probes", variable=self.ConfigSelection,
                            image=self.img_analog, value=5, indicatoron=0,
                            compound=TOP, width=90, command=self.change_tab)
        rdoph.pack(side=LEFT)

        # button for feed timers
        self.img_feed = PhotoImage(file="images/time-64.png")
        rdofeed = Radiobutton(toolbarframe, text="Feed Timers", variable=self.ConfigSelection,
                            image=self.img_feed, value=PAGE_FEEDTIMERS, indicatoron=0,
                            compound=TOP, width=90, command=self.change_tab)
        rdofeed.pack(side=LEFT)

        # button for pulse width modulation settings
        self.img_pwm = PhotoImage(file="images/integrated-circuit-64.png")
        rdopwm = Radiobutton(toolbarframe, text="PWM", variable=self.ConfigSelection,
                            image=self.img_pwm, value=PAGE_PWM, indicatoron=0,
                            compound=TOP, width=90, command=self.change_tab)
        rdopwm.pack(side=LEFT)

        # button for alerts settings
        self.img_alerts = PhotoImage(file="images/alarm-64.png")
        rdoalerts = Radiobutton(toolbarframe, text="Alerts", variable=self.ConfigSelection,
                            image=self.img_alerts, value=PAGE_ALERTS, indicatoron=0,
                            compound=TOP, width=90, command=self.change_tab)
        rdoalerts.pack(side=LEFT)

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
        elif tab == PAGE_ANALOG:
            selection.show_frame(cfg_analog.PageAnalogProbes)
        elif tab == PAGE_FEEDTIMERS:
            selection.show_frame(cfg_feedtimers.PageFeedTimers)
        elif tab == PAGE_PWM:
            selection.show_frame(cfg_pwm.PagePWM)
        elif tab == PAGE_ALERTS:
            selection.show_frame(cfg_alerts.PageAlerts)
        
    def show_frame(self, cont):
        #print("show_frame" + str(cont))
        frame = self.frames[cont]
        frame.tkraise()

root = RBP_configurator()

def on_closing():
    if messagebox.askokcancel("Quit", "Are you sure want to quit?\n\nAny unsaved changes will be lost."):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

##    outletwin = tk.Toplevel()
##    outletwin.transient()
##    outletwin.grab_set()


