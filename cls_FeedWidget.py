import tkinter as tk
from tkinter import * 
from tkinter import ttk
from colorama import Fore, Back, Style
from datetime import datetime, timedelta, time
import pika

class FeedWidget():
    
    def __init__(self, master):

        #initialize the messaging queues      
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        #queue for posting outlet changes
        channel.queue_declare(queue='outlet_change')

        # frame for feed timers
        self.frame_feedtimers = LabelFrame(master, text="Feed Cycle", relief= RAISED)
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

            if mode == "A":
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("feed_mode" + "," + "A"))
            if mode == "B":
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("feed_mode" + "," + "B"))
            if mode == "C":
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("feed_mode" + "," + "C"))
            if mode == "D":
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("feed_mode"+ "," + "D"))
            if mode == "CANCEL":
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("feed_mode"+ "," + "CANCEL"))

            print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
              " Press Feed Mode: " + mode + Style.RESET_ALL)
