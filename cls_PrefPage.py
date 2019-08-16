##############################################################################
# cls_PrefPage.py
#
# this is the GUI for Reefberry Pi.  This implementation is written 
# using tKinter and is a native application to run on the
# Raspberry Pi
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################

import tkinter as tk
from tkinter import * 
from tkinter import ttk
from tkinter import messagebox
import pika
import json
import uuid
import threading

#import cfg_tempprobes
import cls_TempPrefs
import cls_GlobalPrefs
#import cfg_outlets
import cls_EnviroPrefs
import cls_SwitchPrefs
import cls_AnalogPrefs
#import cfg_feedtimers
import cls_PWMPrefs
#import cfg_common
import cls_AlertPrefs
import defs_common

PAGE_GLOBAL     = 0
PAGE_TEMPPROBES = 1
PAGE_OUTLETS    = 2
PAGE_ENVIRO     = 3
PAGE_SWITCHES   = 4
PAGE_ANALOG     = 5
PAGE_FEEDTIMERS = 6
PAGE_PWM        = 7
PAGE_ALERTS     = 8

LARGE_FONT= ("Verdana", 12)

class PrefPage(tk.Frame):
        
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        
        result = self.channel.queue_declare(queue='',exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(on_message_callback=self.rpc_response, auto_ack=True,
                                   queue=self.callback_queue)
        
        

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame_master=LabelFrame(self.canvas, text='Settings', relief=GROOVE)
        self.frame_master.pack(side=LEFT, fill=BOTH)

        # create a toolbar
        self.ConfigSelection = IntVar() 
        toolbarframe = tk.Frame(self.frame_master, relief=tk.FLAT)
        toolbarframe.pack(side=LEFT, fill=tk.Y)

        container = tk.Frame(self.frame_master)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
##
        
        
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=BOTH, expand=True, pady=10)

        self.canvas.create_window((4,4), window=self.frame_master, anchor="nw", 
                                  tags="self.frame_master")

        self.frame_master.bind("<Configure>", self.onFrameConfigure)
##
        for F in (cls_GlobalPrefs.PageGlobal,
                  cls_TempPrefs.PageTempProbes,
                  cls_EnviroPrefs.PageEnvironmental,
                  cls_SwitchPrefs.PageSwitches,
                  cls_AnalogPrefs.PageAnalogProbes,
                  cls_PWMPrefs.PagePWM,
                  cls_AlertPrefs.PageAlerts):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew", padx=20)

        self.show_frame(cls_GlobalPrefs.PageGlobal)

        # button for global settings
        self.img_global = PhotoImage(file="images/globe-48.png")
        rdoGlobal = Radiobutton(toolbarframe, text="Global", variable=self.ConfigSelection,
                                    image=self.img_global, value=0, indicatoron=0,
                                    compound=LEFT, width=200, command=self.change_tab, anchor=W)
        rdoGlobal.pack(side=TOP)

        # button for temperature probes
        self.img_temperature = PhotoImage(file="images/temperature-48.png")
        rdoTempProbes = Radiobutton(toolbarframe, text="Temp Probes", variable=self.ConfigSelection,
                                    image=self.img_temperature, value=1, indicatoron=0,
                                    compound=LEFT, width=200, command=self.change_tab, anchor=W)
        rdoTempProbes.pack(side=TOP)

##        # button for outlets
##        self.img_outlets = PhotoImage(file="images/socket-24.png")
##        rdoOutlets = Radiobutton(toolbarframe, text="Outlets", variable=self.ConfigSelection,
##                                 image=self.img_outlets, value=2, indicatoron=0,
##                                 compound=LEFT, width=200, command=self.change_tab, anchor=W)
##        rdoOutlets.pack(side=TOP)

        # button for environmental probes
        self.img_environmental = PhotoImage(file="images/heating-room-48.png")
        rdoEnvironmental = Radiobutton(toolbarframe, text="Environmental", variable=self.ConfigSelection,
                                       image=self.img_environmental, value=3, indicatoron=0,
                                       compound=LEFT, width=200, command=self.change_tab, anchor=W)
        rdoEnvironmental.pack(side=TOP)

        # button for switches
        self.img_switches = PhotoImage(file="images/switch-on-48.png")
        rdoSwitches = Radiobutton(toolbarframe, text="Switches", variable=self.ConfigSelection,
                                  image=self.img_switches, value=4, indicatoron=0,
                                  compound=LEFT, width=200, command=self.change_tab, anchor=W)
        rdoSwitches.pack(side=TOP)

        # button for analog probes
        self.img_analog = PhotoImage(file="images/sine-48.png")
        rdoph = Radiobutton(toolbarframe, text="Analog Probes", variable=self.ConfigSelection,
                            image=self.img_analog, value=5, indicatoron=0,
                            compound=LEFT, width=200, command=self.change_tab, anchor=W)
        rdoph.pack(side=TOP)

##        # button for feed timers
##        self.img_feed = PhotoImage(file="images/time-24.png")
##        rdofeed = Radiobutton(toolbarframe, text="Feed Timers", variable=self.ConfigSelection,
##                            image=self.img_feed, value=PAGE_FEEDTIMERS, indicatoron=0,
##                            compound=LEFT, width=200, command=self.change_tab, anchor=W)
##        rdofeed.pack(side=TOP)

        # button for pulse width modulation settings
        self.img_pwm = PhotoImage(file="images/integrated-circuit-48.png")
        rdopwm = Radiobutton(toolbarframe, text="PWM", variable=self.ConfigSelection,
                            image=self.img_pwm, value=PAGE_PWM, indicatoron=0,
                            compound=LEFT, width=200, command=self.change_tab, anchor=W)
        rdopwm.pack(side=TOP)

##        # button for alerts settings
##        self.img_alerts = PhotoImage(file="images/alarm-48.png")
##        rdoalerts = Radiobutton(toolbarframe, text="Alerts", variable=self.ConfigSelection,
##                            image=self.img_alerts, value=PAGE_ALERTS, indicatoron=0,
##                            compound=LEFT, width=200, command=self.change_tab, anchor=W)
##        rdoalerts.pack(side=TOP)

        self.sendKeepAlive()
        
    def sendKeepAlive(self):
        # periodically (like every 1 or 2 minutes) send a message to the exchange so it
        # knows this channel is still active and not closed due to inactivity
        defs_common.logtoconsole("send keep alive request: " + "PrefPage", fg="YELLOW", style="BRIGHT")
        request = {
                  "rpc_req": "set_keepalive",
                  "module": "PrefPage",
              }
        request = json.dumps(request)          
        self.rpc_call(request, "rpc_queue")

        # every 2 minutes, send out a message on this channel so the exchange server knows
        # we are still alive and doesn't close our connection
        heartbeatThread = threading.Timer(120, self.sendKeepAlive)
        heartbeatThread.daemon = True
        heartbeatThread.start()
        #threading.Timer(120, self.sendKeepAlive).start()
        
    def rpc_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def rpc_call(self, n, queue):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        defs_common.logtoconsole("RPC call: " + n + " UID: " + self.corr_id, fg="GREEN", style="BRIGHT")
        
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         expiration="300000"),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events(time_limit=20)
            # if timelimit in seconds is reached, and we don't get a response, lets break out of the loop
            # but we must handle NONE return on the caller
            break
        return self.response        

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

        #print (val)
        
        return val

    def onFrameConfigure(self, event):
        # used for the scrollbar
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def change_tab(selection):
        tab = selection.ConfigSelection.get()
        if tab == PAGE_GLOBAL:
            selection.show_frame(cls_GlobalPrefs.PageGlobal)
        elif tab == PAGE_TEMPPROBES:
            selection.show_frame(cls_TempPrefs.PageTempProbes)
        elif tab == PAGE_OUTLETS:
            #selection.show_frame(cfg_outlets.PageOutlets)
            pass
        elif tab == PAGE_ENVIRO:
            selection.show_frame(cls_EnviroPrefs.PageEnvironmental)
        elif tab == PAGE_SWITCHES:
            selection.show_frame(cls_SwitchPrefs.PageSwitches)
        elif tab == PAGE_ANALOG:
            selection.show_frame(cls_AnalogPrefs.PageAnalogProbes)
        elif tab == PAGE_FEEDTIMERS:
            #selection.show_frame(cfg_feedtimers.PageFeedTimers)
            pass
        elif tab == PAGE_PWM:
            selection.show_frame(cls_PWMPrefs.PagePWM)
        elif tab == PAGE_ALERTS:
            selection.show_frame(cls_AlertPrefs.PageAlerts)
        
    def show_frame(self, cont):
        #print("show_frame" + str(cont))
        frame = self.frames[cont]
        frame.tkraise()

