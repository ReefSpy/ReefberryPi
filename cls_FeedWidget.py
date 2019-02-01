import tkinter as tk
from tkinter import * 
from tkinter import ttk
from colorama import Fore, Back, Style
from datetime import datetime, timedelta, time
import pika
import defs_common
import uuid
import json

class FeedWidget():
    
    def __init__(self, master):

        defs_common.logtoconsole("Initializing FeedWidget...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")

##        #initialize the messaging queues      
##        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
##        channel = connection.channel()
        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.rpc_response, no_ack=True,
                                   queue=self.callback_queue)

        #queue for posting outlet changes
        #channel.queue_declare(queue='outlet_change')

        # frame for feed timers
        self.frame_feedtimers = LabelFrame(master, text="Feed Mode", relief= RAISED)
        self.frame_feedtimers.pack(fill=X, side=TOP)
        self.lbl_feedtimers_status = Label(self.frame_feedtimers, text = " ", relief = FLAT)
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

