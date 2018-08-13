import tkinter as tk
from tkinter import *
from tkinter import ttk
import configparser
import cfg_common

LARGE_FONT = ("Verdana", 12)
BUS_INTERNAL = 0
BUS_EXTERNAL = 1

class PageOutlets(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Outlet Configuration", font=LARGE_FONT)
        #label.pack(side=TOP, pady=10, anchor=W)
        label.grid(row=0, column=0, pady=10, sticky=W)
        
        # top frame for toolbar
        self.frame_toolbar = LabelFrame(self, relief= FLAT)
        #self.frame_toolbar.pack(fill=X, side=TOP)
        self.frame_toolbar.grid(row=1, column=0, sticky=W)
                
##        # drop down list for outlets
##        self.outletchoice = StringVar()
##        self.outletlist = ["Outlet 1","Outlet 2","Outlet 3","Outlet 4"]
##        self.outletchoice.set("Outlet 1") # default value
##
##        self.outletmenu = OptionMenu(self.frame_toolbar,self.outletchoice,*self.outletlist,
##                                           command=self.select_outlet)
##        self.outletimg=PhotoImage(file="images/socket-24.png")
##        self.outletmenu.configure(indicatoron=True, compound='left', image=self.outletimg, relief=FLAT)
##
##        #self.outletmenu.pack(side=LEFT, anchor=W)
##        self.outletmenu.grid(row=0, column=0)
##        
##        self.select_outlet("Outlet 1")
##
##        self.saveimg=PhotoImage(file="images/upload-to-cloud-24.png")
##        self.btn_save = Button(self.frame_toolbar, text="Save", image=self.saveimg, compound='left', relief=FLAT)
##        #self.btn_save.pack(side=LEFT, anchor=W)
##        self.btn_save.grid(row=0, column=1)

        self.BusSelection = IntVar()
        self.intbusimg=PhotoImage(file="images/motherboard-48.png")
        self.rdoIntBus = Radiobutton(self.frame_toolbar, text="Internal Bus", variable=self.BusSelection,
                                    image=self.intbusimg, value=0, indicatoron=0, command=lambda:self.show_frame(InternalBus),
                                    compound=TOP)
        self.rdoIntBus.grid(row=0, column=0)

        self.extbusimg=PhotoImage(file="images/usb-48.png")
        self.rdoExtBus = Radiobutton(self.frame_toolbar, text="External Bus", variable=self.BusSelection,
                                    image=self.extbusimg, value=1, indicatoron=0, command=lambda:self.show_frame(ExternalBus),
                                    compound=TOP)
        self.rdoExtBus.grid(row=0, column=1)

        self.container = tk.Frame(self)
        self.container.grid(row=2, column=0, sticky=W)
        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_columnconfigure(0, weight=0)

        self.frames = {}

        for F in (InternalBus,
                  ExternalBus):

            self.frame = F(self.container, self)

            self.frames[F] = self.frame

            self.frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(InternalBus)


    def show_frame(self, cont):
        #print("show_frame" + str(cont))
        frame = self.frames[cont]
        frame.tkraise()


class InternalBus(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.outletnum = IntVar()
        # Outlet Buttons
        self.frame_intbus = LabelFrame(self, text="Internal Bus", relief= GROOVE)
        self.frame_intbus.grid(row=2, column=0, pady=10, sticky=W)

        self.IntOutletSelection = IntVar()
        self.IntOutletSelection.set(1)
        self.outletimg=PhotoImage(file="images/socket-24.png")
        self.rdoOutlet1 = Radiobutton(self.frame_intbus, text="Outlet 1", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=1, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 1))
        self.rdoOutlet1.grid(row=0, column=0)

        self.rdoOutlet2 = Radiobutton(self.frame_intbus, text="Outlet 2", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=2, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 2))
        self.rdoOutlet2.grid(row=1, column=0)

        self.rdoOutlet3 = Radiobutton(self.frame_intbus, text="Outlet 3", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=3, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 3))
        self.rdoOutlet3.grid(row=2, column=0)

        self.rdoOutlet4 = Radiobutton(self.frame_intbus, text="Outlet 4", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=4, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 4))
        self.rdoOutlet4.grid(row=3, column=0)

        # Outlet Config
        self.outlet = Outlet(self.frame_intbus, self, BUS_INTERNAL)
        self.outlet.grid(row=0, column=1, sticky=N, padx=15, rowspan=30)

        # press Outlet 1 button
        self.rdoOutlet1.invoke()

    def selectOutlet(self, parent, outletNum):
        print("Selected Internal Outlet Num: " + str(outletNum))
        #print(parent.winfo_children()[0].winfo_children()[4].winfo_children()[0].winfo_children()[0].winfo_children())
        self.outlet.setOutletNum(outletNum, BUS_INTERNAL)
        parent.outletnum.set(outletNum)

class ExternalBus(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.outletnum = IntVar()

        self.frame_extbus = LabelFrame(self, text="External Bus", relief= GROOVE)
        self.frame_extbus.grid(row=2, column=0, pady=10, sticky=W)

        self.ExtOutletSelection = IntVar()
        self.ExtOutletSelection.set(1)
        self.outletimg=PhotoImage(file="images/socket-24.png")
        self.rdoOutlet1 = Radiobutton(self.frame_extbus, text="Outlet 1", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=1, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 1))
        self.rdoOutlet1.grid(row=0, column=0)

        self.rdoOutlet2 = Radiobutton(self.frame_extbus, text="Outlet 2", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=2, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 2))
        self.rdoOutlet2.grid(row=1, column=0)

        self.rdoOutlet3 = Radiobutton(self.frame_extbus, text="Outlet 3", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=3, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 3))
        self.rdoOutlet3.grid(row=2, column=0)

        self.rdoOutlet4 = Radiobutton(self.frame_extbus, text="Outlet 4", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=4, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 4))
        self.rdoOutlet4.grid(row=3, column=0)

        self.rdoOutlet5 = Radiobutton(self.frame_extbus, text="Outlet 5", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=5, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 5))
        self.rdoOutlet5.grid(row=4, column=0)

        self.rdoOutlet6 = Radiobutton(self.frame_extbus, text="Outlet 6", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=6, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 6))
        self.rdoOutlet6.grid(row=5, column=0)

        self.rdoOutlet7 = Radiobutton(self.frame_extbus, text="Outlet 7", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=7, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 7))
        self.rdoOutlet7.grid(row=6, column=0)

        self.rdoOutlet8 = Radiobutton(self.frame_extbus, text="Outlet 8", variable=self.ExtOutletSelection,
                                    image=self.outletimg, value=8, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 8))
        self.rdoOutlet8.grid(row=7, column=0)

        # Outlet Config
        self.outlet = Outlet(self.frame_extbus, self, BUS_EXTERNAL)
        self.outlet.grid(row=0, column=1, sticky=N, padx=15, rowspan=30)

        # press Outlet 1 button
        self.rdoOutlet1.invoke()

    def selectOutlet(self, parent, outletNum):
        print("Selected External Outlet Num: " + str(outletNum))
        self.outlet.setOutletNum(outletNum, BUS_EXTERNAL)

class Outlet(tk.Frame):

    def __init__(self, parent, controller, BusType):

        tk.Frame.__init__(self, parent)

        self.BusType = BusType
        self.outletnum = IntVar()

##        if self.BusType == BUS_INTERNAL:
##            self.section = "int_outlet_" + str(self.outletnum.get())
##            
##        elif self.BusType == BUS_EXTERNAL:
##            self.section = "ext_outlet_" + str(self.outletnum.get())
            
        ###########################################################################
        # generic outlet info
        ###########################################################################

        # drop down list for control type
        self.controltypechoice = StringVar()
        self.controltypelist = ["Always", "Heater", "Light", "Return Pump", "Skimmer"]
        self.controltypechoice.set("Always") # default value

        # outlet frame
        self.frame_outlet = LabelFrame(self, text="Outlet", relief= GROOVE)
        self.frame_outlet.grid(row=0, column=1, sticky=N)

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

        # Save button
        self.saveImg=PhotoImage(file="images/save-blue-24.png")
        self.btn_Save = Button(self, text="Save", image=self.saveImg, compound=LEFT, command=self.saveOutlet)
        self.btn_Save.grid(row=2, column=2, pady=10, padx=10, sticky=E)

    def setOutletNum(self, outletnum, bustype):
        self.outletnum.set(outletnum)
        print("Outlet::setOutletNum: " + str(outletnum) + " Bus: " + str(self.BusType))
        

        if bustype == BUS_INTERNAL:
            section = "int_outlet_" + str(self.outletnum.get())
            
        elif bustype == BUS_EXTERNAL:
            section = "ext_outlet_" + str(self.outletnum.get())

        # outlet name
        val = cfg_common.readINIfile(section, "name", "Unnamed")
        self.txt_outletname.delete(0, 'end')
        self.txt_outletname.insert(0, val)
        # control type
        val = cfg_common.readINIfile(section, "control_type", "Always")
        self.controltypechoice.set(val)
        self.select_controltype(val)
        # enable logging     
        val = cfg_common.readINIfile(section, "enable_log", str(False))
        if str(val) == "True":
            self.chk_log.select()
        else:
            self.chk_log.deselect()
       
              
    def setOutletName(self):
        self.txt_outletname.delete(0, 'end')
        self.txt_outletname.insert(0, "test123")
        
    def saveOutlet(self):
        print("Save: BusType = " + str(self.BusType))
        self.setOutletName()
        print("Save: Outlet = " + str(self.outletnum.get()))

    def select_controltype(self, control):
        OutletNumber = self.outletnum.get()
        if self.BusType == BUS_INTERNAL:
            section = "int_outlet_" + str(OutletNumber)    
        elif self.BusType == BUS_EXTERNAL:
            section = "ext_outlet_" + str(OutletNumber)

        #print(self.outletnum.get())
        print("you selected control type: " + control + " in section " + str(section))
        try:
            self.frame_cfg.destroy()
            print("destroy")
        except:
            pass    

        # registering validation command
        vldt_ifnum_cmd = (self.register(self.ValidateIfNum),'%s', '%S')

        ###########################################################################
        # frame for outlet configuration
        ###########################################################################
        self.frame_cfg = LabelFrame(self, text="Configuration", relief= GROOVE)
        self.frame_cfg.grid(row=0, column=2, padx=10, sticky=N)

        # dropdown list for fallback
        #fallbackchoice = StringVar()
        #fallbacklist = ["ON", "OFF"]
        #fallbackchoice.set("ON") # default value
        #self.lbl_fallback = Label(self.frame_cfg,text="Fallback:")
        #self.lbl_fallback.grid(row=0, column=0, sticky=E, padx=5)
        #self.fallbackmenu = OptionMenu(self.frame_cfg,fallbackchoice,*fallbacklist)
        #self.fallbackmenu.configure(indicatoron=True, relief=GROOVE)
        #self.fallbackmenu.grid(row=0, column=1, sticky=W, padx=5)

        ##
        if control=="Heater":
            #drop down list for probes
            probechoice = StringVar()
            probelist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
            probechoice.set("ds18b20_1") # default value
            self.lbl_probe = Label(self.frame_cfg,text="Probe Name:")
            self.lbl_probe.grid(row=1, column=0, sticky=E, padx=5)
            self.probemenu = OptionMenu(self.frame_cfg,probechoice,*probelist)
            self.probemenu.configure(indicatoron=True, relief=GROOVE)
            self.probemenu.grid(row=1, column=1, sticky=W, padx=5)
            # spinbox for on temperature
            self.lbl_ontemp = Label(self.frame_cfg,text="On Temperature:")
            self.lbl_ontemp.grid(row=2, column=0, sticky=E, padx=5, pady=5)
            self.spn_ontemp = Spinbox(self.frame_cfg, from_=32,to=212, increment=.1,
                                      validate='all', validatecommand=vldt_ifnum_cmd,
                                      width=6)
            self.spn_ontemp.grid(row=2, column=1, sticky=W, padx=5, pady=5)
            # spinbox for off temperature
            self.lbl_offtemp = Label(self.frame_cfg,text="Off Temperature:")
            self.lbl_offtemp.grid(row=3, column=0, sticky=E, padx=5, pady=5)
            self.spn_offtemp = Spinbox(self.frame_cfg, from_=32,to=212, increment=.1,
                                       validate='all', validatecommand=vldt_ifnum_cmd,
                                       width=6)
            self.spn_offtemp.grid(row=3, column=1, sticky=W, padx=5, pady=5)
        elif control=="Always":
            #drop dwn list for Always
            statechoice = StringVar()
            statelist = ["ON", "OFF"]
            statechoice.set("ON") # default value
            self.lbl_state = Label(self.frame_cfg,text="State:")
            self.lbl_state.grid(row=1, column=0, padx=5, sticky=E)
            self.statemenu = OptionMenu(self.frame_cfg,statechoice,*statelist)
            self.statemenu.configure(indicatoron=True, relief=GROOVE)
            self.statemenu.grid(row=1, column=1, padx=5, sticky=W)
            # read saved state
            val = cfg_common.readINIfile(section, "always_state", "ON")
            statechoice.set(val)
            print("select_controltype Always: " + val)
        elif control=="Light":
            # spinbox for on time
            self.lbl_ontime = Label(self.frame_cfg,text="On Time:")
            self.lbl_ontime.grid(row=1, column=0, padx=5, pady=5, sticky=E)
            self.frame_onFrame = LabelFrame(self.frame_cfg, relief=FLAT)
            self.frame_onFrame.grid(row=1, column=1, padx=5, pady=5, sticky=W)
            self.spn_ontimeHH = Spinbox(self.frame_onFrame, from_=00, to=23, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        format="%02.0f", wrap=True, width=3)
            self.spn_ontimeHH.pack(side=LEFT)
            self.lbl_onSep = Label(self.frame_onFrame, text=":")
            self.lbl_onSep.pack(side=LEFT)
            self.spn_ontimeMM = Spinbox(self.frame_onFrame, from_=00, to=59, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        format="%02.0f", wrap=True, width=3)
            self.spn_ontimeMM.pack(side=LEFT)
            self.lbl_onHHMM = Label(self.frame_onFrame, text="(HH:MM)")
            self.lbl_onHHMM.pack(side=LEFT)
            
            # spinbox for off time
            self.lbl_offtime = Label(self.frame_cfg,text="Off Time:")
            self.lbl_offtime.grid(row=2, column=0, padx=5, pady=5, sticky=E)
            self.frame_offFrame = LabelFrame(self.frame_cfg, relief=FLAT)
            self.frame_offFrame.grid(row=2, column=1, padx=5, pady=5, sticky=W)
            self.spn_offtimeHH = Spinbox(self.frame_offFrame, from_=00, to=23, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        format="%02.0f", wrap=True, width=3)
            self.spn_offtimeHH.pack(side=LEFT)
            self.lbl_offSep = Label(self.frame_offFrame, text=":")
            self.lbl_offSep.pack(side=LEFT)
            self.spn_offtimeMM = Spinbox(self.frame_offFrame, from_=00, to=59, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        format="%02.0f", wrap=True, width=3)
            self.spn_offtimeMM.pack(side=LEFT)
            self.lbl_offHHMM = Label(self.frame_offFrame, text="(HH:MM)")
            self.lbl_offHHMM.pack(side=LEFT)
        elif control=="Return Pump":
            self.lbl_returnFeedtime = Label(self.frame_cfg,text="Feed Timer:")
            self.lbl_returnFeedtime.grid(row=2, column=0, padx=5, pady=5, sticky=E)
            returnFeedchoice = StringVar()
            returnFeedlist = ["A", "B", "C", "D"]
            returnFeedchoice.set("A") # default value
            self.returnFeedmenu = OptionMenu(self.frame_cfg,returnFeedchoice,*returnFeedlist)
            self.returnFeedmenu.configure(indicatoron=True, relief=GROOVE)
            self.returnFeedmenu.grid(row=2, column=1, sticky=W, padx=5)
            self.lbl_returnFeeddelay = Label(self.frame_cfg,text="Feed Timer Delay:")
            self.lbl_returnFeeddelay.grid(row=3, column=0, padx=5, pady=5, sticky=E)
            self.spn_returnFeeddelay = Spinbox(self.frame_cfg, from_=00, to=120, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=4)
            self.spn_returnFeeddelay.grid(row=3, column=1, padx=5, pady=5)
            self.lbl_returnFeedmins = Label(self.frame_cfg,text="(minutes)")
            self.lbl_returnFeedmins.grid(row=3, column=2, padx=5, pady=5)
        elif control=="Skimmer":
            self.lbl_skimmerFeedtime = Label(self.frame_cfg,text="Feed Timer:")
            self.lbl_skimmerFeedtime.grid(row=2, column=0, padx=5, pady=5, sticky=E)
            skimmerFeedchoice = StringVar()
            skimmerFeedlist = ["A", "B", "C", "D"]
            skimmerFeedchoice.set("A") # default value
            self.skimmerFeedmenu = OptionMenu(self.frame_cfg,skimmerFeedchoice,*skimmerFeedlist)
            self.skimmerFeedmenu.configure(indicatoron=True, relief=GROOVE)
            self.skimmerFeedmenu.grid(row=2, column=1, sticky=W, padx=5)
            self.lbl_skimmerFeeddelay = Label(self.frame_cfg,text="Feed Timer Delay:")
            self.lbl_skimmerFeeddelay.grid(row=3, column=0, padx=5, pady=5, sticky=E)
            self.spn_skimmerFeeddelay = Spinbox(self.frame_cfg, from_=00, to=120, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=4)
            self.spn_skimmerFeeddelay.grid(row=3, column=1, padx=5, pady=5)
            self.lbl_skimmerFeedmins = Label(self.frame_cfg,text="(minutes)")
            self.lbl_skimmerFeedmins.grid(row=3, column=2, padx=5, pady=5)
            
##            #drop dwn list for shutdown probe
##            shutdownchoice = StringVar()
##            shutdownlist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
##            shutdownchoice.set("ds18b20_1") # default value
##            self.lbl_shutdownprobe = Label(self.frame_cfg,text="Shutdown Probe:")
##            self.lbl_shutdownprobe.grid(row=3, column=0, padx=5, sticky=E)
##            self.shutdownmenu = OptionMenu(self.frame_cfg,shutdownchoice,*shutdownlist)
##            self.shutdownmenu.configure(indicatoron=True, relief=GROOVE)
##            self.shutdownmenu.grid(row=3, column=1, padx=5, sticky=W, columnspan=2)
##            # spinbox for shutdown temperature
##            self.lbl_shutdowntemp = Label(self.frame_cfg,text="Shutdown Temperature:")
##            self.lbl_shutdowntemp.grid(row=4, column=0, padx=5, pady=5, sticky=E)
##            self.spn_shutdowntemp = Spinbox(self.frame_cfg, from_=32,to=212, increment=.1,
##                                            validate='all', validatecommand=vldt_ifnum_cmd,
##                                            width=6)
##            self.spn_shutdowntemp.grid(row=4, column=1, padx=5, pady=5, sticky=W, columnspan=1)
##            # spin for hysteresis
##            self.lbl_hysteresis = Label(self.frame_cfg,text="Hysteresis:")
##            self.lbl_hysteresis.grid(row=5, column=0, padx=5, pady=5, sticky=E)
##            self.spn_hysteresis = Spinbox(self.frame_cfg, from_=0,to=120, increment=1,
##                                            validate='all', validatecommand=vldt_ifnum_cmd,
##                                            width=6)
##            self.spn_hysteresis.grid(row=5, column=1, padx=5, pady=5, sticky=W)
           

    def ValidateIfNum(self, s, S):
        # disallow anything but numbers
        print(s)
        valid = S == '' or S.isdigit()
        if not valid:
            self.bell()
        return valid



