import tkinter as tk
from tkinter import * 
from tkinter import ttk
from colorama import Fore, Back, Style
from datetime import datetime, timedelta, time
import pika
import defs_common
import uuid
import json
import time
import threading
import cls_FeedConfig

class FeedWidget():
    
    def __init__(self, master):

        defs_common.logtoconsole("Initializing FeedWidget...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")

##        #initialize the messaging queues      
##        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
##        channel = connection.channel()

        #initialize the messaging queues      

        self.initializeConnection()
##        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
##        self.channel = self.connection.channel()
##
##        result = self.channel.queue_declare(exclusive=True)
##        self.callback_queue = result.method.queue
##
##        self.channel.basic_consume(self.rpc_response, no_ack=True,
##                                   queue=self.callback_queue)

        #queue for posting outlet changes
        #channel.queue_declare(queue='outlet_change')

        # frame for feed timers
        self.frame_feedtimers = LabelFrame(master, text="Feed Mode", relief= RAISED)
        self.frame_feedtimers.pack(fill=X, side=TOP)
        self.frame_feed_spacer = tk.LabelFrame(self.frame_feedtimers, relief = tk.FLAT)
        self.frame_feed_spacer.pack(fill=X, side=TOP)

        self.img_cfg16 = PhotoImage(file="images/settings-16.png")
        self.btn_cfg_feed = Button(self.frame_feed_spacer, text = "edit", image=self.img_cfg16,
                                 relief = FLAT, command=lambda:self.configureFeedmode(master))
        self.btn_cfg_feed.pack(side=LEFT, anchor=W)
        
        self.lbl_feedtimers_status = Label(self.frame_feed_spacer, text = " ", relief = FLAT)
        self.lbl_feedtimers_status.pack(side=TOP, anchor=E)
        self.btn_feedA = Button(self.frame_feedtimers, text="A", width=2, command=lambda:select_feed_mode("A"))
        self.btn_feedA.pack(side=LEFT, padx=2)
        self.btn_feedB = Button(self.frame_feedtimers, text="B", width=2, command=lambda:select_feed_mode("B"))
        self.btn_feedB.pack(side=LEFT, padx=2)
        self.btn_feedC = Button(self.frame_feedtimers, text="C", width=2, command=lambda:select_feed_mode("C"))
        self.btn_feedC.pack(side=LEFT, padx=2)
        self.btn_feedD = Button(self.frame_feedtimers, text="D", width=2, command=lambda:select_feed_mode("D"))
        self.btn_feedD.pack(side=LEFT, padx=2)
        self.btn_feedCancel = Button(self.frame_feedtimers, text="Cancel", width=6, command=lambda:select_feed_mode("CANCEL"))
        self.btn_feedCancel.pack(side=RIGHT, anchor=E, padx=2)

        self.sendKeepAlive()

        def select_feed_mode(mode):
            #DefClr = app.cget("bg")
            #btn_feedA.configure(bg=DefClr)
            #btn_feedB.configure(bg=DefClr)
            #btn_feedC.configure(bg=DefClr)
            #btn_feedD.configure(bg=DefClr)
            #btn_feedCancel.configure(bg=DefClr)

            defs_common.logtoconsole("Feed mode request: " + str(mode), fg="YELLOW", style="BRIGHT")

            # request outlet change on server
            request = {
                      "rpc_req": "set_feedmode",
                      "feedmode": str(mode),
                  }
            request = json.dumps(request)          
            self.rpc_call(request, "rpc_queue")
            

##            if mode == "A":
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("feed_mode" + "," + "A"))
##            if mode == "B":
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("feed_mode" + "," + "B"))
##            if mode == "C":
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("feed_mode" + "," + "C"))
##            if mode == "D":
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("feed_mode"+ "," + "D"))
##            if mode == "CANCEL":
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("feed_mode"+ "," + "CANCEL"))

##            print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
##              " Press Feed Mode: " + mode + Style.RESET_ALL)

    def sendKeepAlive(self):
        # periodically (like every 1 or 2 minutes) send a message to the exchange so it
        # knows this channel is still active and not closed due to inactivity
        defs_common.logtoconsole("send keep alive request: " + "FeedWidget", fg="YELLOW", style="BRIGHT")
        request = {
                  "rpc_req": "set_keepalive",
                  "module": "FeedWidget",
              }
        request = json.dumps(request)          
        self.rpc_call(request, "rpc_queue")

        # every 2 minutes or so, send out a message on this channel so the exchange server knows
        # we are still alive and doesn't close our connection
        heartbeatThread = threading.Timer(120, self.sendKeepAlive)
        heartbeatThread.daemon = True
        heartbeatThread.start()

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

    def initializeConnection(self):
        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.rpc_response, no_ack=True,
                                   queue=self.callback_queue)

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

    def updatefeedstatus(self, feedmode, timeremaining):
        DefClr = self.btn_feedCancel.cget("bg")
        self.lbl_feedtimers_status.config(text=str(timedelta(seconds=int(timeremaining))))
        
        if feedmode == "A":
            #print ("A")
            self.btn_feedA.config(background="red")
            self.btn_feedB.config(background=DefClr)
            self.btn_feedC.config(background=DefClr)
            self.btn_feedD.config(background=DefClr)
        elif feedmode == "B":
            #print("B")
            self.btn_feedA.config(background=DefClr)
            self.btn_feedB.config(background="red")
            self.btn_feedC.config(background=DefClr)
            self.btn_feedD.config(background=DefClr)
        elif feedmode == "C":
            #print("C")
            self.btn_feedA.config(background=DefClr)
            self.btn_feedB.config(background=DefClr)
            self.btn_feedC.config(background="red")
            self.btn_feedD.config(background=DefClr)
        elif feedmode == "D":
            #print("D")
            self.btn_feedA.config(background=DefClr)
            self.btn_feedB.config(background=DefClr)
            self.btn_feedC.config(background=DefClr)
            self.btn_feedD.config(background="red")
        else:
            #print ("retun default")
            self.btn_feedA.config(background=DefClr)
            self.btn_feedB.config(background=DefClr)
            self.btn_feedC.config(background=DefClr)
            self.btn_feedD.config(background=DefClr)
            self.lbl_feedtimers_status.config(text="")

    def configureFeedmode(self, master):
        #print("dialog " + self.outletid.get().split("_")[2])
        #outnum = self.outletid.get().split("_")[2]
        
        d = Dialog(master, self)

class Dialog(Toplevel):

    def __init__(self, parent, controller, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.controller = controller

        if title:
            self.title(title)

        self.parent = parent

        self.result = None


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
        self.feedtimers = cls_FeedConfig.FeedTimers(master, self)
        self.feedtimers.pack()
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

        self.feedtimers.saveChanges()

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
