import tkinter as tk
from tkinter import * 
from tkinter import ttk
from colorama import Fore, Back, Style
from datetime import datetime, timedelta, time
import pika
import defs_common

class OutletWidget():
    
    def __init__(self, master):
        defs_common.logtoconsole("Initializing OutletWidget...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")

        self.outletid = StringVar()       # id of this outlet ex: int_outlet_1
        self.outletname = StringVar()     # user defined name of outlet
        self.outletbus = StringVar()      # int or ext bus
        self.control_type = StringVar()   # control scheme of outlet ex: skimmer, lights, always... 
        self.button_state = IntVar()      # button state ON (3), OFF (1), or AUTO (2)
        self.outletstate = StringVar()    # is the outlet currently on or off
        self.statusmsg = StringVar()      # short status message to display above buttons
        
        self.outlet_freezeupdate = BooleanVar()
        

        # set initial value...
        self.statusmsg.set("waiting...")
        self.outlet_freezeupdate.set(True)


        #initialize the messaging queues      
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        #queue for posting outlet changes
        channel.queue_declare(queue='outlet_change')

        # frame for internal outlet 1 control
        self.frame_outlet = LabelFrame(master, text="waiting...", relief= RAISED)
        self.frame_outlet.pack(fill=X, side=TOP)
        self.frame_outlet_spacer = tk.LabelFrame(self.frame_outlet, relief = tk.FLAT)
        self.frame_outlet_spacer.pack(fill=X, side=TOP)
        
##        self.img_cfg16 = PhotoImage(file="images/settings-16.png")
##        self.btn_cfg_outlet = Button(self.frame_outlet_spacer, text = "edit", image=self.img_cfg16,
##                                 relief = FLAT, command = self.RBP_outletcfg.init())
##        self.btn_cfg_outlet.pack(side=LEFT, anchor=W)
        
        self.lbl_outlet_status = Label(self.frame_outlet_spacer, text = "waiting...", relief = FLAT, textvariable=self.statusmsg)
        self.lbl_outlet_status.pack(side=TOP, anchor=E)                          
        self.rdo_outlet_off = Radiobutton(self.frame_outlet, text="Off", variable=self.button_state,
                                     value=1, command=self.select_outlet_state,
                                     indicatoron=0)
        self.rdo_outlet_off.pack(side=LEFT, expand=1, fill=X)

        self.rdo_outlet_auto = Radiobutton(self.frame_outlet, text="Auto", variable=self.button_state,
                              value=2, command=self.select_outlet_state,
                              indicatoron=0)
        self.rdo_outlet_auto.pack(side=LEFT, expand=1, fill=X)

        self.rdo_outlet_on = Radiobutton(self.frame_outlet, text="On", variable=self.button_state,
                                    value=3, command=self.select_outlet_state,
                                    indicatoron=0)
        self.rdo_outlet_on.pack(side=LEFT, expand=1, fill=X)

#    def select_int_outlet1_state():
#        print("Hello World")
        
    def updateOutletFrameName(self):
        self.frame_outlet.config(text = self.outletname.get())
        
##if value == "OFF":
##    value = OUTLET_OFF
##elif value == "ON":
##    value = OUTLET_ON
##elif value == "AUTO":
##    value = OUTLET_AUTO
                    
    def select_outlet_state(self):
        defs_common.logtoconsole("select_outlet_state: " + str(self.button_state.get()))
        if self.button_state.get() == defs_common.OUTLET_OFF:
            defs_common.logtoconsole("set text to off", bg="RED", style = "BRIGHT")
            self.statusmsg.set("OFF")
            self.lbl_outlet_status.config(foreground="RED")
##            channel.basic_publish(exchange='',
##                                  routing_key='outlet_change',
##                                  properties=pika.BasicProperties(expiration='30000'),
##                                  body=str("int_outlet_1" + "," + "OFF"))
        elif self.button_state.get() == defs_common.OUTLET_AUTO:
            defs_common.logtoconsole("set text to AUTO", bg="RED", style = "BRIGHT")
            self.statusmsg.set("AUTO")
            self.lbl_outlet_status.config(foreground="DARK ORANGE")            
##            channel.basic_publish(exchange='',
##                                  routing_key='outlet_change',
##                                  properties=pika.BasicProperties(expiration='30000'),
##                                  body=str("int_outlet_1" + "," + "AUTO"))
        elif self.button_state.get() == defs_common.OUTLET_ON:
            defs_common.logtoconsole("set text to ON", bg="RED", style = "BRIGHT")
            self.statusmsg.set("ON")
            self.lbl_outlet_status.config(foreground="GREEN")
##            channel.basic_publish(exchange='',
##                                  routing_key='outlet_change',
##                                  properties=pika.BasicProperties(expiration='30000'),
##                                  body=str("int_outlet_1" + "," + "ON"))
        else:
            self.lbl_outlet_status.config(text="UNKNOWN", foreground="BLACK")
##        selection = "Select outlet option " + self.lbl_outlet_status.cget("text")
##        print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
##          " " + selection + Style.RESET_ALL)
        self.outlet_freezeupdate.set(True)
