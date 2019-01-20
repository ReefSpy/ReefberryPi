import tkinter as tk
from tkinter import *
from tkinter import ttk
import configparser
import cfg_common
from tkinter import font
import cfg_tempprobes

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

        self.rdoOutlet5 = Radiobutton(self.frame_intbus, text="Outlet 5", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=5, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 5))
        self.rdoOutlet5.grid(row=4, column=0)

        self.rdoOutlet6 = Radiobutton(self.frame_intbus, text="Outlet 6", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=6, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 6))
        self.rdoOutlet6.grid(row=5, column=0)

        self.rdoOutlet7 = Radiobutton(self.frame_intbus, text="Outlet 7", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=7, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 7))
        self.rdoOutlet7.grid(row=6, column=0)

        self.rdoOutlet8 = Radiobutton(self.frame_intbus, text="Outlet 8", variable=self.IntOutletSelection,
                                    image=self.outletimg, value=8, indicatoron=0,
                                    compound=RIGHT, command=lambda:self.selectOutlet(self, 8))
        self.rdoOutlet8.grid(row=7, column=0)
        

        # Outlet Config
        self.outlet = Outlet(self.frame_intbus, self, BUS_INTERNAL)
        self.outlet.grid(row=0, column=1, sticky=N, padx=15, rowspan=30)

        # press Outlet 1 button
        self.rdoOutlet1.invoke()

    def selectOutlet(self, parent, outletNum):
        #print("Selected Internal Outlet Num: " + str(outletNum))
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
        #print("Selected External Outlet Num: " + str(outletNum))
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
        self.logenabled = IntVar()
        self.logframe = LabelFrame(self.frame_outlet, relief= FLAT)
        self.logframe.pack(fill=X, side=TOP)
        self.lbl_log = Label(self.logframe,text="Log:")
        self.lbl_log.pack(side=LEFT, anchor=W)
        self.chk_log = Checkbutton(self.logframe, text="Enable", variable=self.logenabled)
        self.chk_log.pack(side=LEFT, anchor=W)

        # Save button
        self.saveImg=PhotoImage(file="images/save-blue-24.png")
        self.btn_Save = Button(self, text="Save", image=self.saveImg, compound=LEFT, command=self.saveOutlet)
        self.btn_Save.grid(row=2, column=2, pady=10, padx=10, sticky=E)

    def setOutletNum(self, outletnum, bustype):
        self.outletnum.set(outletnum)
        #print("Outlet::setOutletNum: " + str(outletnum) + " Bus: " + str(self.BusType))
        

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
        if self.BusType == BUS_INTERNAL:
            section = "int_outlet_" + str(self.outletnum.get())
        elif self.BusType == BUS_EXTERNAL:
            section = "ext_outlet_" + str(self.outletnum.get())

        # outlet name
        cfg_common.writeINIfile(section, "name", self.txt_outletname.get())
        # control type
        cfg_common.writeINIfile(section, "control_type", self.controltypechoice.get())
        # enable log
        if self.logenabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"    
        cfg_common.writeINIfile(section, "enable_log", str(chkstate))

        # configurations
        if self.controltypechoice.get() == "Always": # Always
            cfg_common.writeINIfile(section, "always_state", str(self.statechoice.get()))

        elif self.controltypechoice.get() == "Light": # Light
            # on time
            valH = self.spn_ontimeHH.get()
            if int(valH) > 23:
                valH = 23
            elif int(valH) < 0:
                valH = 0     
            self.spn_ontimeHH.delete(0, "end")
            self.spn_ontimeHH.insert(0, valH)

            valM = self.spn_ontimeMM.get()
            if int(valM) > 59:
                valM = 59
            elif int(valM) < 0:
                valM = 0
            self.spn_ontimeMM.delete(0, "end")
            self.spn_ontimeMM.insert(0, valM)
            
            val = str(valH) + ":" + str(valM)
            cfg_common.writeINIfile(section, "light_on", str(val))

            # off time
            valH = self.spn_offtimeHH.get()
            if int(valH) > 23:
                valH = 23
            elif int(valH) < 0:
                valH = 0     
            self.spn_offtimeHH.delete(0, "end")
            self.spn_offtimeHH.insert(0, valH)
            
            valM = self.spn_offtimeMM.get()
            if int(valM) > 59:
                valM = 59
            elif int(valM) < 0:
                valM = 0
            self.spn_offtimeMM.delete(0, "end")
            self.spn_offtimeMM.insert(0, valM)
            
            val = str(valH) + ":" + str(valM)
            cfg_common.writeINIfile(section, "light_off", str(val))

        elif self.controltypechoice.get() == "Return Pump": # Return Pump
            # feed a
            cfg_common.writeINIfile(section, "return_feed_delay_a", str(self.spn_returnFeeddelayA.get()))
            if self.rtnFeedenabledA.get() == True:
                cfg_common.writeINIfile(section, "return_enable_feed_a", "True")
            else:
                cfg_common.writeINIfile(section, "return_enable_feed_a", "False")
            # feed b
            cfg_common.writeINIfile(section, "return_feed_delay_b", str(self.spn_returnFeeddelayB.get()))
            if self.rtnFeedenabledB.get() == True:
                cfg_common.writeINIfile(section, "return_enable_feed_b", "True")
            else:
                cfg_common.writeINIfile(section, "return_enable_feed_b", "False")
            # feed c
            cfg_common.writeINIfile(section, "return_feed_delay_c", str(self.spn_returnFeeddelayC.get()))
            if self.rtnFeedenabledC.get() == True:
                cfg_common.writeINIfile(section, "return_enable_feed_c", "True")
            else:
                cfg_common.writeINIfile(section, "return_enable_feed_c", "False")
            # feed d
            cfg_common.writeINIfile(section, "return_feed_delay_d", str(self.spn_returnFeeddelayD.get()))
            if self.rtnFeedenabledD.get() == True:
                cfg_common.writeINIfile(section, "return_enable_feed_d", "True")
            else:
                cfg_common.writeINIfile(section, "return_enable_feed_d", "False")
            
        elif self.controltypechoice.get() == "Skimmer": # Skimmer
            # feed a
            cfg_common.writeINIfile(section, "skimmer_feed_delay_a", str(self.spn_skimmerFeeddelayA.get()))
            if self.skmFeedenabledA.get() == True:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_a", "True")
            else:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_a", "False")
            # feed b
            cfg_common.writeINIfile(section, "skimmer_feed_delay_b", str(self.spn_skimmerFeeddelayB.get()))
            if self.skmFeedenabledB.get() == True:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_b", "True")
            else:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_b", "False")
            # feed c
            cfg_common.writeINIfile(section, "skimmer_feed_delay_c", str(self.spn_skimmerFeeddelayC.get()))
            if self.skmFeedenabledC.get() == True:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_c", "True")
            else:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_c", "False")
            # feed d
            cfg_common.writeINIfile(section, "skimmer_feed_delay_d", str(self.spn_skimmerFeeddelayD.get()))
            if self.skmFeedenabledD.get() == True:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_d", "True")
            else:
                cfg_common.writeINIfile(section, "skimmer_enable_feed_d", "False")    

        elif self.controltypechoice.get() == "Heater": # Heater
            tempscale = cfg_common.readINIfile("global", "tempscale", cfg_common.SCALE_F)
            if int(tempscale) == int(cfg_common.SCALE_C):
                cfg_common.writeINIfile(section, "heater_on", self.spn_ontemp.get())
                cfg_common.writeINIfile(section, "heater_off", self.spn_offtemp.get())
            elif int(tempscale) == int(cfg_common.SCALE_F):
                val = cfg_common.convertFtoC(self.spn_ontemp.get())
                cfg_common.writeINIfile(section, "heater_on", val)
                val = cfg_common.convertFtoC(self.spn_offtemp.get())
                cfg_common.writeINIfile(section, "heater_off", val)

            val = self.tempprobechoice.get().rsplit("[")[1]
            val=val[:-1] # strip last character from string because it will be "]"
            cfg_common.writeINIfile(section, "heater_probe", val)

    def select_controltype(self, control):
        OutletNumber = self.outletnum.get()
        if self.BusType == BUS_INTERNAL:
            section = "int_outlet_" + str(OutletNumber)    
        elif self.BusType == BUS_EXTERNAL:
            section = "ext_outlet_" + str(OutletNumber)

        #print(self.outletnum.get())
        #print("you selected control type: " + control + " in section " + str(section))
        try:
            self.frame_cfg.destroy()
            #print("destroy")
        except:
            pass    

        # registering validation command
        vldt_ifnum_cmd = (self.register(self.ValidateIfNum),'%s', '%S')
        vldt_iffloat_cmd = (self.register(self.ValidateIfFloat),'%s', '%S')        

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
            
            probeDict = self.readExistingProbes()
            print(probeDict)
            probelist = []
            for k in probeDict.keys():
                #probelist.append(probeDict.get("28-0316479150ff").name + " (" +
                #                 probeDict.get("28-0316479150ff").probeid + ")")
                probelist.append(probeDict.get(k).name + " [" +
                                 probeDict.get(k).probeid + "]")
            if len(probeDict) == 0:
                probelist.append(" ") # no probes defined, just add an empty list entry so it wont error
            #drop down list for probes
            self.tempprobechoice = StringVar()
            #probelist = ["ds18b20_1", "ds18b20_2", "ds18b20_3"]
            #probechoice.set("ds18b20_1") # default value
            self.lbl_probe = Label(self.frame_cfg,text="Probe Name:")
            self.lbl_probe.grid(row=1, column=0, sticky=E, padx=5)
            self.probemenu = OptionMenu(self.frame_cfg,self.tempprobechoice,*probelist)
            self.probemenu.configure(indicatoron=True, relief=GROOVE)
            self.probemenu.grid(row=1, column=1, sticky=W, padx=5)
            # spinbox for on temperature
            self.lbl_ontemp = Label(self.frame_cfg,text="On Temperature:")
            self.lbl_ontemp.grid(row=2, column=0, sticky=E, padx=5, pady=5)
            self.spn_ontemp = Spinbox(self.frame_cfg, from_=0,to=212, increment=.1,
                                      validate='all', 
                                      width=6)
            self.spn_ontemp.grid(row=2, column=1, sticky=W, padx=5, pady=5)
            # spinbox for off temperature
            self.lbl_offtemp = Label(self.frame_cfg,text="Off Temperature:")
            self.lbl_offtemp.grid(row=3, column=0, sticky=E, padx=5, pady=5)
            self.spn_offtemp = Spinbox(self.frame_cfg, from_=0,to=212, increment=.1,
                                       validate='all',
                                       width=6)
            self.spn_offtemp.grid(row=3, column=1, sticky=W, padx=5, pady=5)

            # read saved values
            val = cfg_common.readINIfile(section, "heater_probe", "")
            if val != "":
                try:
                    self.tempprobechoice.set(probeDict[val].name + " [" +
                                             probeDict[val].probeid + "]")
                except:
                    self.tempprobechoice.set(val) # if a selection was made, but probe later deleted
                                                  # it won't find the name so just use the ID

            tempscale = cfg_common.readINIfile("global", "tempscale", cfg_common.SCALE_F)
            if int(tempscale) == int(cfg_common.SCALE_C):
                val = cfg_common.readINIfile(section, "heater_on", "25.0")
                self.spn_ontemp.delete(0, END)
                self.spn_ontemp.insert(0, '{0:.1f}'.format(float(val)))
                val = cfg_common.readINIfile(section, "heater_off", "25.5")
                self.spn_offtemp.delete(0, END)
                self.spn_offtemp.insert(0, '{0:.1f}'.format(float(val)))
            else:
                val = cfg_common.readINIfile(section, "heater_on", "25.0")
                val = cfg_common.convertCtoF(val)
                self.spn_ontemp.delete(0, END)
                self.spn_ontemp.insert(0, '{0:.1f}'.format(float(val)))
                val = cfg_common.readINIfile(section, "heater_off", "25.5")
                val = cfg_common.convertCtoF(val)
                self.spn_offtemp.delete(0, END)
                self.spn_offtemp.insert(0, '{0:.1f}'.format(float(val)))
                
            
        elif control=="Always":
            #drop dwn list for Always
            self.statechoice = StringVar()
            self.statelist = ["ON", "OFF"]
            self.statechoice.set("ON") # default value
            self.lbl_state = Label(self.frame_cfg,text="State:")
            self.lbl_state.grid(row=1, column=0, padx=5, sticky=E)
            self.statemenu = OptionMenu(self.frame_cfg,self.statechoice,*self.statelist)
            self.statemenu.configure(indicatoron=True, relief=GROOVE)
            self.statemenu.grid(row=1, column=1, padx=5, sticky=W)
            # read saved state
            val = cfg_common.readINIfile(section, "always_state", "ON")
            self.statechoice.set(val)
            #print("select_controltype Always: " + val)

            
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

            # read saved states
            # on time 
            val = cfg_common.readINIfile(section, "light_on", "08:00")
            val = val.split(":")
            self.spn_ontimeHH.delete(0, "end")
            self.spn_ontimeHH.insert(0, val[0])
            self.spn_ontimeMM.delete(0, "end")
            self.spn_ontimeMM.insert(0, val[1])
            # off time
            val = cfg_common.readINIfile(section, "light_off", "17:00")
            val = val.split(":")
            self.spn_offtimeHH.delete(0, "end")
            self.spn_offtimeHH.insert(0, val[0])
            self.spn_offtimeMM.delete(0, "end")
            self.spn_offtimeMM.insert(0, val[1])
            
            
        elif control=="Skimmer":
            self.lbl_skimmerFeedtimer = Label(self.frame_cfg,text="Feed Timer")
            self.lbl_skimmerFeedtimer.grid(row=2, column=0, padx=5, pady=5, sticky=E)
            self.lbl_enableSkmFeedtimer = Label(self.frame_cfg,text="Enable")
            self.lbl_enableSkmFeedtimer.grid(row=2, column=1, padx=5, pady=5, sticky=E)
            self.lbl_delaySkmFeedtimer = Label(self.frame_cfg,text="Additional Feed Timer Delay (seconds)",
                                            wraplength=150)
            self.lbl_delaySkmFeedtimer.grid(row=2, column=2, padx=5, pady=5, sticky=E)
            # we want to underline the header, so:
            # clone the font, set the underline attribute,
            # and assign it to our widget
            f = font.Font(self.lbl_skimmerFeedtimer, self.lbl_skimmerFeedtimer.cget("font"))
            f.configure(underline = True)
            self.lbl_skimmerFeedtimer.configure(font=f)
            self.lbl_enableSkmFeedtimer.configure(font=f)
            self.lbl_delaySkmFeedtimer.configure(font=f)

            # row for timer A
            self.lbl_skimmerFeedtimerA = Label(self.frame_cfg,text="A")
            self.lbl_skimmerFeedtimerA.grid(row=3, column=0, padx=5, pady=2)
            self.skmFeedenabledA = IntVar()
            self.chk_skmFeedenabledA = Checkbutton(self.frame_cfg, variable=self.skmFeedenabledA)
            self.chk_skmFeedenabledA.grid(row=3, column=1, padx=5, pady=2)
            self.spn_skimmerFeeddelayA = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_skimmerFeeddelayA.grid(row=3, column=2, padx=5, pady=2)    
            val = cfg_common.readINIfile(section, "skimmer_enable_feed_a", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_skmFeedenabledA.select()
            else:
                self.chk_skmFeedenabledA.deselect()
            val = cfg_common.readINIfile(section, "skimmer_feed_delay_a", "0") # feed delay timer
            self.spn_skimmerFeeddelayA.delete(0, "end")
            self.spn_skimmerFeeddelayA.insert(0, val)
           
            # row for timer B
            self.lbl_skimmerFeedtimerB = Label(self.frame_cfg,text="B")
            self.lbl_skimmerFeedtimerB.grid(row=4, column=0, padx=5, pady=2)
            self.skmFeedenabledB = IntVar()
            self.chk_skmFeedenabledB = Checkbutton(self.frame_cfg, variable=self.skmFeedenabledB)
            self.chk_skmFeedenabledB.grid(row=4, column=1, padx=5, pady=2)
            self.spn_skimmerFeeddelayB = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_skimmerFeeddelayB.grid(row=4, column=2, padx=5, pady=2)
            val = cfg_common.readINIfile(section, "skimmer_enable_feed_b", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_skmFeedenabledB.select()
            else:
                self.chk_skmFeedenabledB.deselect()
            val = cfg_common.readINIfile(section, "skimmer_feed_delay_b", "0") # feed delay timer
            self.spn_skimmerFeeddelayB.delete(0, "end")
            self.spn_skimmerFeeddelayB.insert(0, val)
            # row for timer C
            self.lbl_skimmerFeedtimerC = Label(self.frame_cfg,text="C")
            self.lbl_skimmerFeedtimerC.grid(row=5, column=0, padx=5, pady=2)
            self.skmFeedenabledC = IntVar()
            self.chk_skmFeedenabledC = Checkbutton(self.frame_cfg, variable=self.skmFeedenabledC)
            self.chk_skmFeedenabledC.grid(row=5, column=1, padx=5, pady=2)
            self.spn_skimmerFeeddelayC = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_skimmerFeeddelayC.grid(row=5, column=2, padx=5, pady=2)
            val = cfg_common.readINIfile(section, "skimmer_enable_feed_c", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_skmFeedenabledC.select()
            else:
                self.chk_skmFeedenabledC.deselect()
            val = cfg_common.readINIfile(section, "skimmer_feed_delay_c", "0") # feed delay timer
            self.spn_skimmerFeeddelayC.delete(0, "end")
            self.spn_skimmerFeeddelayC.insert(0, val)
            # row for timer D
            self.lbl_skimmerFeedtimerD = Label(self.frame_cfg,text="D")
            self.lbl_skimmerFeedtimerD.grid(row=6, column=0, padx=5, pady=2)
            self.skmFeedenabledD = IntVar()
            self.chk_skmFeedenabledD = Checkbutton(self.frame_cfg, variable=self.skmFeedenabledD)
            self.chk_skmFeedenabledD.grid(row=6, column=1, padx=5, pady=2)
            self.spn_skimmerFeeddelayD = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_skimmerFeeddelayD.grid(row=6, column=2, padx=5, pady=2)
            val = cfg_common.readINIfile(section, "skimmer_enable_feed_d", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_skmFeedenabledD.select()
            else:
                self.chk_skmFeedenabledD.deselect()
            val = cfg_common.readINIfile(section, "skimmer_feed_delay_d", "0") # feed delay timer
            self.spn_skimmerFeeddelayD.delete(0, "end")
            self.spn_skimmerFeeddelayD.insert(0, val)
            
        elif control=="Return Pump":
            self.lbl_returnFeedtimer = Label(self.frame_cfg,text="Feed Timer")
            self.lbl_returnFeedtimer.grid(row=2, column=0, padx=5, pady=5, sticky=E)
            self.lbl_enableRtnFeedtimer = Label(self.frame_cfg,text="Enable")
            self.lbl_enableRtnFeedtimer.grid(row=2, column=1, padx=5, pady=5, sticky=E)
            self.lbl_delayFeedtimer = Label(self.frame_cfg,text="Additional Feed Timer Delay (seconds)",
                                            wraplength=150)
            self.lbl_delayFeedtimer.grid(row=2, column=2, padx=5, pady=5, sticky=E)
            # we want to underline the header, so:
            # clone the font, set the underline attribute,
            # and assign it to our widget
            f = font.Font(self.lbl_returnFeedtimer, self.lbl_returnFeedtimer.cget("font"))
            f.configure(underline = True)
            self.lbl_returnFeedtimer.configure(font=f)
            self.lbl_enableRtnFeedtimer.configure(font=f)
            self.lbl_delayFeedtimer.configure(font=f)

            # row for timer A
            self.lbl_returnFeedtimerA = Label(self.frame_cfg,text="A")
            self.lbl_returnFeedtimerA.grid(row=3, column=0, padx=5, pady=2)
            self.rtnFeedenabledA = IntVar()
            self.chk_rtnFeedenabledA = Checkbutton(self.frame_cfg, variable=self.rtnFeedenabledA)
            self.chk_rtnFeedenabledA.grid(row=3, column=1, padx=5, pady=2)
            self.spn_returnFeeddelayA = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_returnFeeddelayA.grid(row=3, column=2, padx=5, pady=2)    
            val = cfg_common.readINIfile(section, "return_enable_feed_a", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_rtnFeedenabledA.select()
            else:
                self.chk_rtnFeedenabledA.deselect()
            val = cfg_common.readINIfile(section, "return_feed_delay_a", "0") # feed delay timer
            self.spn_returnFeeddelayA.delete(0, "end")
            self.spn_returnFeeddelayA.insert(0, val)
           
            # row for timer B
            self.lbl_returnFeedtimerB = Label(self.frame_cfg,text="B")
            self.lbl_returnFeedtimerB.grid(row=4, column=0, padx=5, pady=2)
            self.rtnFeedenabledB = IntVar()
            self.chk_rtnFeedenabledB = Checkbutton(self.frame_cfg, variable=self.rtnFeedenabledB)
            self.chk_rtnFeedenabledB.grid(row=4, column=1, padx=5, pady=2)
            self.spn_returnFeeddelayB = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_returnFeeddelayB.grid(row=4, column=2, padx=5, pady=2)
            val = cfg_common.readINIfile(section, "return_enable_feed_b", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_rtnFeedenabledB.select()
            else:
                self.chk_rtnFeedenabledB.deselect()
            val = cfg_common.readINIfile(section, "return_feed_delay_b", "0") # feed delay timer
            self.spn_returnFeeddelayB.delete(0, "end")
            self.spn_returnFeeddelayB.insert(0, val)
            # row for timer C
            self.lbl_returnFeedtimerC = Label(self.frame_cfg,text="C")
            self.lbl_returnFeedtimerC.grid(row=5, column=0, padx=5, pady=2)
            self.rtnFeedenabledC = IntVar()
            self.chk_rtnFeedenabledC = Checkbutton(self.frame_cfg, variable=self.rtnFeedenabledC)
            self.chk_rtnFeedenabledC.grid(row=5, column=1, padx=5, pady=2)
            self.spn_returnFeeddelayC = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_returnFeeddelayC.grid(row=5, column=2, padx=5, pady=2)
            val = cfg_common.readINIfile(section, "return_enable_feed_c", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_rtnFeedenabledC.select()
            else:
                self.chk_rtnFeedenabledC.deselect()
            val = cfg_common.readINIfile(section, "return_feed_delay_c", "0") # feed delay timer
            self.spn_returnFeeddelayC.delete(0, "end")
            self.spn_returnFeeddelayC.insert(0, val)
            # row for timer D
            self.lbl_returnFeedtimerD = Label(self.frame_cfg,text="D")
            self.lbl_returnFeedtimerD.grid(row=6, column=0, padx=5, pady=2)
            self.rtnFeedenabledD = IntVar()
            self.chk_rtnFeedenabledD = Checkbutton(self.frame_cfg, variable=self.rtnFeedenabledD)
            self.chk_rtnFeedenabledD.grid(row=6, column=1, padx=5, pady=2)
            self.spn_returnFeeddelayD = Spinbox(self.frame_cfg, from_=0, to=3600, increment=1,
                                        validate='all', validatecommand=vldt_ifnum_cmd,
                                        wrap=True, width=8)
            self.spn_returnFeeddelayD.grid(row=6, column=2, padx=5, pady=2)
            val = cfg_common.readINIfile(section, "return_enable_feed_d", str(False)) # enabled feed delay
            if str(val) == "True":
                self.chk_rtnFeedenabledD.select()
            else:
                self.chk_rtnFeedenabledD.deselect()
            val = cfg_common.readINIfile(section, "return_feed_delay_d", "0") # feed delay timer
            self.spn_returnFeeddelayD.delete(0, "end")
            self.spn_returnFeeddelayD.insert(0, val)
##            self.lbl_skimmerFeedtime = Label(self.frame_cfg,text="Feed Timer:")
##            self.lbl_skimmerFeedtime.grid(row=2, column=0, padx=5, pady=5, sticky=E)
##            skimmerFeedchoice = StringVar()
##            skimmerFeedlist = ["A", "B", "C", "D"]
##            skimmerFeedchoice.set("A") # default value
##            self.skimmerFeedmenu = OptionMenu(self.frame_cfg,skimmerFeedchoice,*skimmerFeedlist)
##            self.skimmerFeedmenu.configure(indicatoron=True, relief=GROOVE)
##            self.skimmerFeedmenu.grid(row=2, column=1, sticky=W, padx=5)
##            self.lbl_skimmerFeeddelay = Label(self.frame_cfg,text="Feed Timer Delay:")
##            self.lbl_skimmerFeeddelay.grid(row=3, column=0, padx=5, pady=5, sticky=E)
##            self.spn_skimmerFeeddelay = Spinbox(self.frame_cfg, from_=00, to=120, increment=1,
##                                        validate='all', validatecommand=vldt_ifnum_cmd,
##                                        wrap=True, width=6)
##            self.spn_skimmerFeeddelay.grid(row=3, column=1, padx=5, pady=5)
##            self.lbl_skimmerFeedsecs = Label(self.frame_cfg,text="(seconds)")
##            self.lbl_skimmerFeedsecs.grid(row=3, column=2, padx=5, pady=5)
##            # read saved states
##            # feed timer
##            val = cfg_common.readINIfile(section, "skimmer_feed_selection", "A")
##            skimmerFeedchoice.set(val)
##            if val == "A":
##                val = cfg_common.readINIfile(section, "skimmer_feed_delay_a", "0")
##                self.spn_skimmerFeeddelay.delete(0, "end")
##                self.spn_skimmerFeeddelay.insert(0, val)
##            elif val == "B":
##                val = cfg_common.readINIfile(section, "skimmer_feed_delay_b", "0")
##                self.spn_skimmerFeeddelay.delete(0, "end")
##                self.spn_skimmerFeeddelay.insert(0, val)
##            elif val == "C":
##                val = cfg_common.readINIfile(section, "skimmer_feed_delay_c", "0")
##                self.spn_skimmerFeeddelay.delete(0, "end")
##                self.spn_skimmerFeeddelay.insert(0, val)
##            elif val == "D":
##                val = cfg_common.readINIfile(section, "skimmer_feed_delay_d", "0")
##                self.spn_skimmerFeeddelay.delete(0, "end")
##                self.spn_skimmerFeeddelay.insert(0, val)
            

           

    def ValidateIfNum(self, s, S):
        # disallow anything but numbers
        #print(s)
        valid = S == '' or S.isdigit()
        if not valid:
            self.bell()
        return valid

    def ValidateIfFloat(self, s, S):
        # disallow anything but numbers
        #print(s)
        valid = S == '' or S.isdigit() or S == '.'
        if not valid:
            self.bell()
        return valid

    def readExistingProbes(self):
        # create dictionary to hold assigned temperature probes
        # these are probes that are already saved in config file
        probeDict = {}
        probeDict.clear()
        config = configparser.ConfigParser()
        config.read(cfg_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            if section.split("_")[0] == "ds18b20":
                probe = cfg_tempprobes.ProbeClass()
                probe.probeid = section.split("_")[1]
                probe.name = config[section]["name"]
                probeDict [section.split("_")[1]] = probe
        return probeDict
