import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import * 
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta, time
import pika
import uuid
import json

matplotlib.use("TkAgg")

class ProbeWidget():
    
    def __init__(self, master):

        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.rpc_response, no_ack=True,
                                   queue=self.callback_queue)
        
        self.probeid = StringVar()
        self.name = StringVar()
        self.probetype = StringVar()
        self.probeval = StringVar()
        
        self.figprobe = Figure(figsize=(1,1), dpi=100)
        self.aniprobe = self.figprobe.add_subplot(111, axisbg="gainsboro")
        self.probeframe = LabelFrame(master, text=self.name, relief = RAISED)
        self.probeframe.pack(fill=X, side=TOP)
        self.frame_probeval = LabelFrame(self.probeframe, relief = FLAT)
        self.frame_probeval.pack(side=LEFT)
        self.lbl_probeval = Label(self.frame_probeval, text="00.0", relief = FLAT, 
                                    font=("Helvetica",44), padx=10)
        self.lbl_probeval.pack(side=TOP)
        self.lbl_probeSN = Label(self.frame_probeval,textvariable=self.probeid, padx=10)
        self.lbl_probeSN.pack(side=TOP) # dont display this, but its used to match the probe values on update

        #set up mini plot
        #some definitions for the plots
        LARGE_FONT= ("Verdana", 12)
        style.use("ggplot")
        self.figprobe = Figure(figsize=(1,1), dpi=100)
        self.figprobe.set_facecolor("gainsboro")
        self.aniprobe = self.figprobe.add_subplot(111, axisbg="gainsboro")
        self.canvasprobe = FigureCanvasTkAgg(self.figprobe, self.probeframe)
        self.canvasprobe.show()
        self.canvasprobe.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)
        #canvasprobe.get_tk_widget().grid(padx=10, sticky=W, row=0, column=2, columnspan=2)
        
        ani = animation.FuncAnimation(self.figprobe, self.animate_probe, interval=300000)
        
    def rpc_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def rpc_call(self, n, queue):
        self.response = None
        self.corr_id = str(uuid.uuid4())
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

    def updateProbeFrameName(self):
        self.probeframe.config(text = self.name.get())
        
    # plot probe data
    def animate_probe(self, i):
        self.aniprobe.clear()
        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing " + self.name.get() + " mini graph")
        days_to_plot = 2

        # request new data from server
        request = {
                      "rpc": "get_probedata24h",
                      "probetype": self.probetype.get(),
                      "probeid": self.probeid.get()
                  }
        request = json.dumps(request)          
        print(request)
        chartData = self.rpc_call(request, "rpc_queue")
        
        try:
            chartData = chartData.decode()
            chartData = json.loads(chartData)
            # convert the string dates to datetime objects
            xList = [] # put them in this list
            for t in chartData["datetime"]:
                t = datetime.strptime(t,'%Y-%m-%d %H:%M:%S')
                xList.append(t)
            print(chartData["datetime"])
            self.aniprobe.plot(xList, chartData["probevalue"], "-", color='GREEN')
            myFmt = mdates.DateFormatter('%I:%M%p')
            self.aniprobe.xaxis.set_major_formatter(myFmt)

            self.figprobe.autofmt_xdate()
            self.aniprobe.axes.tick_params(axis='x', labelsize=1, pad=50)
            self.aniprobe.axes.tick_params(axis='y', labelsize=8) 
        except:
            self.figprobe.autofmt_xdate()
            self.aniprobe.axes.tick_params(axis='x', labelsize=1, pad=50)
            self.aniprobe.axes.tick_params(axis='y', labelsize=8) 
            print("Error plotting data")
            pass
        

        return
