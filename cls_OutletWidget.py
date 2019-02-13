import tkinter as tk
from tkinter import * 
from tkinter import ttk
import os
from colorama import Fore, Back, Style
from datetime import datetime, timedelta, time
import pika
import defs_common
import uuid
import json
#import cfg_outlets
import cls_OutletConfig
import time
import threading

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


        self.initializeConnection()
##        #initialize the messaging queues      
##        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat_interval=5))
##        self.channel = self.connection.channel()
##
##        result = self.channel.queue_declare(exclusive=True)
##        self.callback_queue = result.method.queue
##
##        self.channel.basic_consume(self.rpc_response, no_ack=True,
##                                   queue=self.callback_queue)

        

        # frame for internal outlet 1 control
        self.frame_outlet = LabelFrame(master, text="waiting...", relief= RAISED)
        self.frame_outlet.pack(fill=X, side=TOP)
        self.frame_outlet_spacer = tk.LabelFrame(self.frame_outlet, relief = tk.FLAT)
        self.frame_outlet_spacer.pack(fill=X, side=TOP)
        
        self.img_cfg16 = PhotoImage(file="images/settings-16.png")
        self.btn_cfg_outlet = Button(self.frame_outlet_spacer, text = "edit", image=self.img_cfg16,
                                 relief = FLAT, command=lambda:self.configureOutlet(master))
        self.btn_cfg_outlet.pack(side=LEFT, anchor=W)
        
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

        self.sendKeepAlive()

    def rpc_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def rpc_call(self, n, queue):
        self.response = None
        self.corr_id = str(uuid.uuid4())

##        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " RPC call: " + n
##              + " UID: " + self.corr_id)

        defs_common.logtoconsole(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " RPC call: " + n
              + " UID: " + self.corr_id, fg="GREEN", style="BRIGHT")
            

        if self.connection.is_open:
            defs_common.logtoconsole("Pika connection is OPEN")
        else:
            defs_common.logtoconsole("Pika connection is CLOSED")
            defs_common.logtoconsole("Reopen Pika connection")
            self.initializeConnection()
            
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         expiration="300000"),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response
    
    def initializeConnection(self):
        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.rpc_response, no_ack=True,
                                   queue=self.callback_queue)

    def updateOutletFrameName(self, name):
        self.frame_outlet.config(text = name)
        #print(name)

    def sendKeepAlive(self):
        # periodically (like every 1 or 2 minutes) send a message to the exchange so it
        # knows this channel is still active and not closed due to inactivity
        defs_common.logtoconsole("send keep alive request: " + str(self.outletid.get()), fg="YELLOW", style="BRIGHT")
        request = {
                  "rpc_req": "set_keepalive",
                  "module": str(self.outletid.get()),
              }
        request = json.dumps(request)          
        self.rpc_call(request, "rpc_queue")

        # every 2 minutes, send out a message on this channel so the exchange server knows
        # we are still alive and doesn't close our connection
        heartbeatThread = threading.Timer(120, self.sendKeepAlive)
        heartbeatThread.daemon = True
        heartbeatThread.start()
        #threading.Timer(120, self.sendKeepAlive).start()
        
                                
    def select_outlet_state(self):
        defs_common.logtoconsole("outlet state change: " + str(self.outletid.get()) + " to " + str(self.button_state.get()), fg="YELLOW", style="BRIGHT")
        if self.button_state.get() == defs_common.OUTLET_OFF:
            self.statusmsg.set("OFF")
            self.lbl_outlet_status.config(foreground="RED")
##            self.channel.basic_publish(exchange='',
##                                  routing_key='outlet_change',
##                                  properties=pika.BasicProperties(expiration='30000'),
##                                  body=str(str(self.outletid.get()) + "," + "OFF"))
##                                  #body=str("int_outlet_1" + "," + "OFF"))

            # request outlet change on server
            request = {
                      "rpc_req": "set_outletoperationmode",
                      "bus": str(self.outletbus.get()),
                      "outletnum": str(self.outletid.get().split("_")[2]),
                      "opmode": "off"
                  }
            request = json.dumps(request)          
            self.rpc_call(request, "rpc_queue")
                                  
        elif self.button_state.get() == defs_common.OUTLET_AUTO:
            self.statusmsg.set("AUTO")
            self.lbl_outlet_status.config(foreground="DARK ORANGE")            
##            self.channel.basic_publish(exchange='',
##                                  routing_key='outlet_change',
##                                  properties=pika.BasicProperties(expiration='30000'),
##                                  body=str(str(self.outletid.get()) + "," + "AUTO"))
##                                  #body=str("int_outlet_1" + "," + "AUTO"))
            request = {
                      "rpc_req": "set_outletoperationmode",
                      "bus": str(self.outletbus.get()),
                      "outletnum": str(self.outletid.get().split("_")[2]),
                      "opmode": "auto"
                  }
            request = json.dumps(request)          
            self.rpc_call(request, "rpc_queue")
            
        elif self.button_state.get() == defs_common.OUTLET_ON:
            self.statusmsg.set("ON")
            self.lbl_outlet_status.config(foreground="GREEN")
##            self.channel.basic_publish(exchange='',
##                                  routing_key='outlet_change',
##                                  properties=pika.BasicProperties(expiration='30000'),
##                                  body=str(str(self.outletid.get()) + "," + "ON"))
##                                  #body=str("int_outlet_1" + "," + "ON"))
            request = {
                      "rpc_req": "set_outletoperationmode",
                      "bus": str(self.outletbus.get()),
                      "outletnum": str(self.outletid.get().split("_")[2]),
                      "opmode": "on"
                  }
            request = json.dumps(request)          
            self.rpc_call(request, "rpc_queue")
        else:
            self.lbl_outlet_status.config(text="UNKNOWN", foreground="BLACK")
##        selection = "Select outlet option " + self.lbl_outlet_status.cget("text")
##        print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
##          " " + selection + Style.RESET_ALL)
        self.outlet_freezeupdate.set(True)
        defs_common.logtoconsole("Freeze Update: " + str(self.outletid.get() + " " + str(self.outlet_freezeupdate.get())), fg="CYAN")

    def configureOutlet(self, master):
        print("dialog " + self.outletid.get().split("_")[2])
        outnum = self.outletid.get().split("_")[2]
        
        d = Dialog(master, self, outnum)

    def uploadsettings(self, section, key, value):
        defs_common.logtoconsole("Request settings change: [" + str(section) + "] [" + str(key) + "] = " + str(value))
        # request settings change on server
        request = {
                  "rpc_req": "set_writeinifile",
                  "section": str(section),
                  "key": str(key),
                  "value": str(value)
              }
        request = json.dumps(request)          
        self.rpc_call(request, "rpc_queue")

    def downloadsettings(self, section, key, defaultval):
        defs_common.logtoconsole("Request settings vaue: [" + str(section) + "] [" + str(key) + "]")
        # get setting value from server
        request = {
                  "rpc_req": "get_readinifile",
                  "section": str(section),
                  "key": str(key),
                  "defaultval": str(defaultval)
              }
        request = json.dumps(request)          
        val = self.rpc_call(request, "rpc_queue")
        val = val.decode()
        val = json.loads(val)
        val = val.get("readinifile")

        print (val)
        
        return val

        
class Dialog(Toplevel):

    def __init__(self, parent, controller, outletnum, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.controller = controller

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        self.outletnum = outletnum

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)



    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        #outlet = cfg_outlets.PageOutlets(master, self)
        outlet = cls_OutletConfig.Outlet(master, self, cls_OutletConfig.BUS_INTERNAL, self.outletnum)

        outlet.pack()
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override
