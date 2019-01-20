#!/usr/bin/python3

##############################################################################
# RBP_app.py
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
from datetime import datetime, timedelta, time
import time
import cls_DashBoard 
import cls_GraphPage
#import cls_Toolbar
import defs_common
import os,sys
import queue
import threading
import pika
#import random
import json


# change to current directory or else could have trouble when
# executing script from another location ie: a Desktop icon
os.chdir(os.path.dirname(sys.argv[0]))

class RBP_app:
    
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        #tk.Tk.__init__(self, *args, **kwargs)

        defs_common.logtoconsole("Application startup...")
        
        #self.iconbitmap('@images/reefberrypi_logo.xbm')
        master.wm_title("Reefberry Pi")
        #set minimum size of the window
        master.minsize(400,400)
        master.geometry("1100x600")
        
        #self.toolbar = cls_Toolbar.Toolbar()

        ######################### 
        #create toolbar frame
        self.frame_toolbar = tk.LabelFrame(master, relief = tk.FLAT)
        self.frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
        self.btn_DashBoard = ttk.Button(self.frame_toolbar, text="Dashboard", image=self.img_dashboard, 
                            compound=TOP, command=lambda: self.show_frame(cls_DashBoard.DashBoard))
        self.btn_DashBoard.pack(side=LEFT)

        self.img_graph = PhotoImage(file="images/line-chart-64.png")
        self.btn_GraphPage = ttk.Button(self.frame_toolbar, text="Graphs", image=self.img_graph,
                            compound=TOP, command=lambda: self.show_frame(cls_GraphPage.GraphPage))
        self.btn_GraphPage.pack(side=LEFT)
        #########################
        container = tk.Frame(master)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (cls_DashBoard.DashBoard, cls_GraphPage.GraphPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame(cls_DashBoard.DashBoard)
        #self.show_frame(cls_GraphPage.GraphPage)

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                defs_common.logtoconsole("processIncoming " + str(msg))
                msg = json.loads(msg)
                 
                for key in msg:
                    if key == "status_currentprobeval":
                        curID = str(msg["status_currentprobeval"]["probeid"])
                        curVal = str(msg["status_currentprobeval"]["probeval"])

                        if curID == "dht_h": #if this is a humidity value, tack on the % sign
                            curVal = str(curVal) + "%"
                        self.frames[cls_DashBoard.DashBoard].updateProbeVal(curID, curVal)

                    if key == "status_currentoutletstate":    
                        #defs_common.logtoconsole(str(msg), fg="MAGENTA", bg="GREEN")
                        self.frames[cls_DashBoard.DashBoard].updateOutletStatus(str(msg["status_currentoutletstate"]["outletid"]),
                                                                                str(msg["status_currentoutletstate"]["outletname"]),
                                                                                str(msg["status_currentoutletstate"]["outletbus"]),
                                                                                str(msg["status_currentoutletstate"]["control_type"]),
                                                                                str(msg["status_currentoutletstate"]["button_state"]),
                                                                                str(msg["status_currentoutletstate"]["outletstate"]),
                                                                                str(msg["status_currentoutletstate"]["statusmsg"]))

            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

        
        
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()



####################
        
class ThreadedClient:
     # Launch the main part of the GUI and the worker thread. periodicCall and
     # endApplication could reside in the GUI part, but putting them here
     # means that you have all the thread controls in a single place.

    def __init__(self, master):

        # Start the GUI and the asynchronous threads. We are in the main
        # (original) thread of the application, which will later be used by
        # the GUI as well. We spawn a new thread for the worker (I/O).
        
        self.master = master

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = RBP_app(master, self.queue, self.endApplication)
       

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1

        self.thread1 = threading.Thread(target=self.workerThread_RBPstatusListener)
        self.thread1.daemon = True
        self.thread1.start()

        

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

        
    def periodicCall(self):
        
        # Check every 200 ms if there is something new in the queue.
        
        self.gui.processIncoming(  )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)


    def endApplication(self):
        defs_common.logtoconsole("Exiting application")
        self.running = 0
        

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
    
        

#####################
        
app = tk.Tk()

client = ThreadedClient(app)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.destroy()
        client.endApplication()

app.protocol("WM_DELETE_WINDOW", on_closing)


app.mainloop()
