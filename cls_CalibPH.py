import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common
from datetime import datetime
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pika
import uuid
import json
import defs_common
import queue
import threading
import random
import time

matplotlib.use("TkAgg")

LARGE_FONT= ("Verdana", 12)

class CalibPH(tk.Frame):

    def __init__(self, parent, controller, ChannelID):
        tk.Frame.__init__(self, parent)

        defs_common.logtoconsole("Initializing CalibPH...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")

        # Create the queue
        self.queue = queue.Queue(  )

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1


        self.thread1 = threading.Thread(target=self.workerThread_RBPstatusListener)
        self.thread1.daemon = True
        self.thread1.start()

        self.controller = controller
        self.parent = parent
        
        # registering validation command
        #self.vldt_ifnum_cmd = (self.register(self.ValidateIfNum),'%s', '%S')

        headlabel = tk.Label(self, text="3-Point Calibration", font=LARGE_FONT)
        headlabel.grid(row=0, column=0, pady=10, sticky=W, columnspan=2)

        lbl_calPoint = headlabel = tk.Label(self, text="Cal Point")
        lbl_calPoint.grid(row=1, column=0, padx=10)
        lbl_refVal = headlabel = tk.Label(self, text="PH Reference")
        lbl_refVal.grid(row=1, column=1, padx=10)
        lbl_digVal = headlabel = tk.Label(self, text="Digital Value")
        lbl_digVal.grid(row=1, column=2, padx=10)

        # we want to underline the header, so:
        # clone the font, set the underline attribute,
        # and assign it to our widget
        f = font.Font(lbl_calPoint, lbl_calPoint.cget("font"))
        f.configure(underline = True)
        lbl_calPoint.configure(font=f)
        lbl_refVal.configure(font=f)
        lbl_digVal.configure(font=f)

        # read values from config file
        # Low Val
        lbl_pointLow = tk.Label(self, text="Low")
        lbl_pointLow.grid(row=2, column=0)
        lbl_phrefLow = tk.Label(self, text="4.0")
        lbl_phrefLow.grid(row=2, column=1)
        strval = "ch" + str(ChannelID) + "_ph_low"
        val = self.controller.controller.controller.controller.downloadsettings("mcp3008", strval, "900")
        lbl_low_val = tk.Label(self, text=val)
        lbl_low_val.grid(row=2, column=2)
        # Med Val
        lbl_pointMed = tk.Label(self, text="Medium")
        lbl_pointMed.grid(row=3, column=0)
        lbl_phrefMed = tk.Label(self, text="7.0")
        lbl_phrefMed.grid(row=3, column=1)
        strval = "ch" + str(ChannelID) + "_ph_med"
        val = self.controller.controller.controller.controller.downloadsettings("mcp3008", strval, "800")
        lbl_low_med = tk.Label(self, text=val)
        lbl_low_med.grid(row=3, column=2)
        # High Val
        lbl_pointHigh = tk.Label(self, text="High")
        lbl_pointHigh.grid(row=4, column=0)
        lbl_phrefHigh = tk.Label(self, text="10.0")
        lbl_phrefHigh.grid(row=4, column=1)
        strval = "ch" + str(ChannelID) + "_ph_high"
        val = self.controller.controller.controller.controller.downloadsettings("mcp3008", strval, "700")
        lbl_low_high = tk.Label(self, text=val)
        lbl_low_high.grid(row=4, column=2)

        # Start the periodic call to check if the queue contains
        # anything
        self.periodicCall()



    def periodicCall(self):
        
        # Check every 100 ms if there is something new in the queue.
        
        self.processIncoming(  )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                print(msg)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                #defs_common.logtoconsole("processIncoming " + str(msg))
                msg = json.loads(msg)
                 
                for key in msg:
                    print(key)
##                    if key == "status_currentprobeval":
##                        curID = str(msg["status_currentprobeval"]["probeid"])
##                        curVal = str(msg["status_currentprobeval"]["probeval"])
##                        curName = str(msg["status_currentprobeval"]["probename"])
##
##                        if curID == "dht_h": #if this is a humidity value, tack on the % sign
##                            curVal = str(curVal) + "%"
##                        self.frames[cls_DashBoard.DashBoard].updateProbeVal(curID, curVal, curName)
##
##                    if key == "status_currentoutletstate":    
##                        #defs_common.logtoconsole(str(msg), fg="MAGENTA", bg="GREEN")
##                        self.frames[cls_DashBoard.DashBoard].updateOutletStatus(str(msg["status_currentoutletstate"]["outletid"]),
##                                                                                str(msg["status_currentoutletstate"]["outletname"]),
##                                                                                str(msg["status_currentoutletstate"]["outletbus"]),
##                                                                                str(msg["status_currentoutletstate"]["control_type"]),
##                                                                                str(msg["status_currentoutletstate"]["button_state"]),
##                                                                                str(msg["status_currentoutletstate"]["outletstate"]),
##                                                                                str(msg["status_currentoutletstate"]["statusmsg"]))
##                    if key == "status_feedmode":
##                        defs_common.logtoconsole(str(msg), fg="MAGENTA", bg="GREEN")
##                        feedmode = str(msg["status_feedmode"]["feedmode"])
##                        timeremaining = str(msg["status_feedmode"]["timeremaining"])
##                        self.frames[cls_DashBoard.DashBoard].feedFrame.updatefeedstatus(feedmode, timeremaining)
                        
                        
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass


    def workerThread_RBPstatusListener(self):
        # check for new messages in the messanging exchange
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange='rbp_currentstatus',
                                 exchange_type='fanout')

        target=self.handle_RBPstatus(channel)

    def handle_RBPstatus(self, channel):
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='rbp_currentstatus',
                           queue=queue_name)
        def callback(ch, method, properties, body):
            body = body.decode()
            #print(" [x] %r" % body)
            self.queue.put(body)


        channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)

        defs_common.logtoconsole("Listening for status updates on exchange: rbp_currentstatus")
        channel.start_consuming()
