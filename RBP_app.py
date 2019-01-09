#!/usr/bin/python3

# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import time
import matplotlib
matplotlib.use("TkAgg")
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
import configparser
from datetime import datetime, timedelta, time
from colorama import Fore, Back, Style
import pika
import os,sys
import cfg_common
#import RBP_outletcfg

LARGE_FONT= ("Verdana", 12)
OUTLET_OFF = 1
OUTLET_AUTO = 2
OUTLET_ON = 3

# change to current directory or else could have trouble when
# executing script from another location ie: a Desktop icon
os.chdir(os.path.dirname(sys.argv[0]))

class RBP_app(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        #self.iconbitmap('@images/reefberrypi_logo.xbm')
        tk.Tk.wm_title(self, "Reefberry Pi")
        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (DashBoard, PageOne, PageTwo, PageThree):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(DashBoard)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()



class ProbeClass():
    name = ""
    probeid = ""
    probetype = ""
    probeval = ""

class DashBoard(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        #initialize config file
        config = configparser.ConfigParser()
        config.read('ReefberryPi.ini')
        #Define some Tkinter variables
        strTemperature = StringVar()
        strDate = StringVar()
        probe_temperature = StringVar()
        probe_update_time = StringVar()
        probe_temperature_ext = StringVar()
        probe_humidity = StringVar()
        probe_ph = StringVar()
        #humidity_display = StringVar()
        graphTimeFrame = IntVar()
        int_outlet1_state = IntVar()
        int_outlet2_state = IntVar()
        int_outlet3_state = IntVar()
        int_outlet4_state = IntVar()
        #heater_freezeupdate = BooleanVar()
        #outlet1_state = IntVar()
        #outlet1_freezeupdate = BooleanVar()
        int_outlet1_freezeupdate = BooleanVar()
        int_outlet2_freezeupdate = BooleanVar()
        int_outlet3_freezeupdate = BooleanVar()
        int_outlet4_freezeupdate = BooleanVar()
        
        #initialize the default values
        probe_temperature.set("-1")
        probe_temperature_ext.set("-1")
        probe_humidity.set("-1")
        probe_ph.set("-1")
        #humidity_display.set("-1")
        #heater_freezeupdate.set(True)
        #outlet1_freezeupdate.set(True)
        int_outlet1_freezeupdate.set(True)
        int_outlet2_freezeupdate.set(True)
        int_outlet3_freezeupdate.set(True)
        int_outlet4_freezeupdate.set(True)

        # create dictionary to hold assigned probes
        # these are probes that are saved in config file
        self.probeDict = {}

        #populate the GUI
        #use two frames to set up two columns
        self.frame_left_column=LabelFrame(self, relief = RAISED)
        #self.frame_left_column=Canvas(self, relief=RAISED)
        #leftVScroll=Scrollbar(self.frame_left_column, orient=VERTICAL, command=self.frame_left_column.yview)
        #leftVScroll.pack(side=RIGHT, fill=Y)
        #self.frame_left_column.configure(yscrollcommand=leftVScroll.set)
        self.frame_left_column.pack(side=LEFT, anchor=N, fill=X, expand=True)
        
        frame_right_column=LabelFrame(self, relief = RAISED)
        frame_right_column.pack(side=RIGHT, anchor=N)

        logocanvas=Canvas(frame_right_column,width=250,height=250)
        logocanvas.pack()

        self.img=PhotoImage(file="images/reefberrypi_logo2.gif")
        logocanvas.create_image(0,0,image=self.img, anchor=NW)

        #initialize the messaging queues      
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        #queue for current probe values  
        channel.queue_declare(queue='current_state')
        #queue for posting outlet changes
        channel.queue_declare(queue='outlet_change')
        
        #print(' [*] Waiting for messages.')
        
        #create toolbar frame
        frame_toolbar = tk.LabelFrame(self.frame_left_column, relief = tk.FLAT)
        frame_toolbar.pack(side=tk.TOP, fill=tk.X)
        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
        btn_DashBoard = ttk.Button(frame_toolbar, text="Dashboard", image=self.img_dashboard, 
                            compound=TOP, command=lambda: controller.show_frame(DashBoard))
        btn_DashBoard.pack(side=LEFT)

        self.img_alarm = PhotoImage(file="images/notification-64.png")
        button = ttk.Button(frame_toolbar, text="Alarm Log", image=self.img_alarm,
                            compound=TOP, command=lambda: controller.show_frame(PageOne))
        button.pack(side=LEFT)

        self.img_testlog = PhotoImage(file="images/test-tube-64.png")
        button2 = ttk.Button(frame_toolbar, text="Test Log", image=self.img_testlog,
                            compound=TOP, command=lambda: controller.show_frame(PageTwo))
        button2.pack(side=LEFT)

        self.img_graph = PhotoImage(file="images/line-chart-64.png")
        button3 = ttk.Button(frame_toolbar, text="Graphs", image=self.img_graph,
                            compound=TOP, command=lambda: controller.show_frame(PageThree))
        button3.pack(side=LEFT)

        # read the existing probes saved in the config file, we will use these to create the
        # small charts on the GUI
        self.readExistingProbes()
        for i in self.probeDict:
            print("Probe dict id: " + str(self.probeDict[i].probeid))
            print("Probe dict name: " + str(self.probeDict[i].name))
            self.createProbeFrame(self.probeDict[i])

            
      

        def select_int_outlet1_state():
            if int_outlet1_state.get() == OUTLET_OFF:    
                lbl_int_outlet1_status.config(text="OFF", foreground="RED")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_1" + "," + "OFF"))
            elif int_outlet1_state.get() == OUTLET_AUTO:
                lbl_int_outlet1_status.config(text="AUTO", foreground="DARK ORANGE")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_1" + "," + "AUTO"))
            elif int_outlet1_state.get() == OUTLET_ON:
                lbl_int_outlet1_status.config(text="ON", foreground="GREEN")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_1" + "," + "ON"))
            else:
                lbl_int_outlet1_status.config(text="UNKNOWN", foreground="BLACK")
            selection = "Select int_outlet_1 option " + lbl_int_outlet1_status.cget("text")
            print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
              " " + selection + Style.RESET_ALL)
            int_outlet1_freezeupdate.set(True)

        def select_int_outlet2_state():
            if int_outlet2_state.get() == OUTLET_OFF:
                lbl_int_outlet2_status.config(text="OFF", foreground="RED")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_2" + "," + "OFF"))
            elif int_outlet2_state.get() == OUTLET_AUTO:
                lbl_int_outlet2_status.config(text="AUTO", foreground="DARK ORANGE")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_2" + "," + "AUTO"))
            elif int_outlet2_state.get() == OUTLET_ON:
                lbl_int_outlet2_status.config(text="ON", foreground="GREEN")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_2" + "," + "ON"))
            else:
                lbl_int_outlet2_status.config(text="UNKNOWN", foreground="BLACK")
                
            selection = "Select int_outlet_2 option " + lbl_int_outlet2_status.cget("text")
            print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
              " " + selection + Style.RESET_ALL)
            int_outlet2_freezeupdate.set(True)

        def select_int_outlet3_state():
            if int_outlet3_state.get() == OUTLET_OFF:
                lbl_int_outlet3_status.config(text="OFF", foreground="RED")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_3" + "," + "OFF"))
            elif int_outlet3_state.get() == OUTLET_AUTO:
                lbl_int_outlet3_status.config(text="AUTO", foreground="DARK ORANGE")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_3" + "," + "AUTO"))
            elif int_outlet3_state.get() == OUTLET_ON:
                lbl_int_outlet3_status.config(text="ON", foreground="GREEN")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_3" + "," + "ON"))
            else:
                lbl_int_outlet3_status.config(text="UNKNOWN", foreground="BLACK")
            selection = "Select int_outlet_3 option " + lbl_int_outlet3_status.cget("text")
            print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
              " " + selection + Style.RESET_ALL)
            int_outlet3_freezeupdate.set(True)
            
        def select_int_outlet4_state():
            if int_outlet4_state.get() == OUTLET_OFF:
                lbl_int_outlet4_status.config(text="OFF", foreground="RED")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_4" + "," + "OFF"))
            elif int_outlet4_state.get() == OUTLET_AUTO:
                lbl_int_outlet4_status.config(text="AUTO", foreground="DARK ORANGE")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_4" + "," + "AUTO"))
            elif int_outlet4_state.get() == OUTLET_ON:
                lbl_int_outlet4_status.config(text="ON", foreground="GREEN")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("int_outlet_4" + "," + "ON"))
            else:
                lbl_int_outlet4_status.config(text="UNKNOWN", foreground="BLACK")
            selection = "Select int_outlet_4 option " + lbl_int_outlet4_status.cget("text")
            print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
              " " + selection + Style.RESET_ALL)
            int_outlet4_freezeupdate.set(True)

        self.img_cfg16 = PhotoImage(file="images/settings-16.png")

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
            
        # frame for feed timers
        frame_feedtimers = LabelFrame(frame_right_column, text="Feed Cycle", relief= RAISED)
        frame_feedtimers.pack(fill=X, side=TOP)
        lbl_feedtimers_status = Label(frame_feedtimers, text = " ", relief = FLAT)
        lbl_feedtimers_status.pack(side=TOP, anchor=E)
        btn_feedA = Button(frame_feedtimers, text="A", width=2, command=lambda:select_feed_mode("A"))
        btn_feedA.pack(side=LEFT, padx=2)
        btn_feedB = Button(frame_feedtimers, text="B", width=2, command=lambda:select_feed_mode("B"))
        btn_feedB.pack(side=LEFT, padx=2)
        btn_feedC = Button(frame_feedtimers, text="C", width=2, command=lambda:select_feed_mode("C"))
        btn_feedC.pack(side=LEFT, padx=2)
        btn_feedD = Button(frame_feedtimers, text="D", width=2, command=lambda:select_feed_mode("D"))
        btn_feedD.pack(side=LEFT, padx=2)
        btn_feedCancel = Button(frame_feedtimers, text="Cancel", width=6, command=lambda:select_feed_mode("CANCEL"))
        btn_feedCancel.pack(side=RIGHT, anchor=E, padx=2)
        
        # frame for internal outlet 1 control
        frame_int_outlet1 = LabelFrame(frame_right_column, text="waiting...", relief= RAISED)
        frame_int_outlet1.pack(fill=X, side=TOP)
        frame_outlet1_spacer = tk.LabelFrame(frame_int_outlet1, relief = tk.FLAT)
        frame_outlet1_spacer.pack(fill=X, side=TOP)
        #btn_cfg_outlet1 = Button(frame_outlet1_spacer, text = "edit", image=self.img_cfg16,
        #                         relief = FLAT, command = RBP_outletcfg.init())
        #btn_cfg_outlet1.pack(side=LEFT, anchor=W)
        lbl_int_outlet1_status = Label(frame_outlet1_spacer, text = "waiting...", relief = FLAT)
        lbl_int_outlet1_status.pack(side=TOP, anchor=E)                          
        rdo_int_outlet1_off = Radiobutton(frame_int_outlet1, text="Off", variable=int_outlet1_state,
                                     value=1, command=select_int_outlet1_state,
                                     indicatoron=0)
        rdo_int_outlet1_off.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet1_auto = Radiobutton(frame_int_outlet1, text="Auto", variable=int_outlet1_state,
                              value=2, command=select_int_outlet1_state,
                              indicatoron=0)
        rdo_int_outlet1_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet1_on = Radiobutton(frame_int_outlet1, text="On", variable=int_outlet1_state,
                                    value=3, command=select_int_outlet1_state,
                                    indicatoron=0)
        rdo_int_outlet1_on.pack(side=LEFT, expand=1, fill=X)

        # frame for internal outlet 2 control
        frame_int_outlet2 = LabelFrame(frame_right_column, text="waiting...", relief= RAISED)
        frame_int_outlet2.pack(fill=X, side=TOP)
        lbl_int_outlet2_status = Label(frame_int_outlet2, text = "waiting...", relief = FLAT)
        lbl_int_outlet2_status.pack(side=TOP, anchor=E)                          
        rdo_int_outlet2_off = Radiobutton(frame_int_outlet2, text="Off", variable=int_outlet2_state, value=1,
                             command=select_int_outlet2_state, indicatoron=0)
        rdo_int_outlet2_off.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet2_auto = Radiobutton(frame_int_outlet2, text="Auto", variable=int_outlet2_state, value=2,
                             command=select_int_outlet2_state, indicatoron=0)
        rdo_int_outlet2_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet2_on = Radiobutton(frame_int_outlet2, text="On", variable=int_outlet2_state, value=3,
                             command=select_int_outlet2_state, indicatoron=0)
        rdo_int_outlet2_on.pack(side=LEFT, expand=1, fill=X)

        # frame for internal outlet 3 control
        frame_int_outlet3 = LabelFrame(frame_right_column, text="waiting...", relief= RAISED)
        frame_int_outlet3.pack(fill=X, side=TOP)
        lbl_int_outlet3_status = Label(frame_int_outlet3, text = "waiting...", relief = FLAT)
        lbl_int_outlet3_status.pack(side=TOP, anchor=E)                          
        rdo_int_outlet3_off = Radiobutton(frame_int_outlet3, text="Off", variable=int_outlet3_state, value=1,
                             command=select_int_outlet3_state, indicatoron=0)
        rdo_int_outlet3_off.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet3_auto = Radiobutton(frame_int_outlet3, text="Auto", variable=int_outlet3_state, value=2,
                             command=select_int_outlet3_state, indicatoron=0)
        rdo_int_outlet3_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet3_on = Radiobutton(frame_int_outlet3, text="On", variable=int_outlet3_state, value=3,
                             command=select_int_outlet3_state, indicatoron=0)
        rdo_int_outlet3_on.pack(side=LEFT, expand=1, fill=X)

        # frame for internal outlet 4 control
        frame_int_outlet4 = LabelFrame(frame_right_column, text="waiting...", relief= RAISED)
        frame_int_outlet4.pack(fill=X, side=TOP)
        lbl_int_outlet4_status = Label(frame_int_outlet4, text = "waiting...", relief = FLAT)
        lbl_int_outlet4_status.pack(side=TOP, anchor=E)                          
        rdo_int_outlet4_off = Radiobutton(frame_int_outlet4, text="Off", variable=int_outlet4_state, value=1,
                             command=select_int_outlet4_state, indicatoron=0)
        rdo_int_outlet4_off.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet4_auto = Radiobutton(frame_int_outlet4, text="Auto", variable=int_outlet4_state, value=2,
                             command=select_int_outlet4_state, indicatoron=0)
        rdo_int_outlet4_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_int_outlet4_on = Radiobutton(frame_int_outlet4, text="On", variable=int_outlet4_state, value=3,
                             command=select_int_outlet4_state, indicatoron=0)
        rdo_int_outlet4_on.pack(side=LEFT, expand=1, fill=X)


        #create temperature frame
        frame_temperature = LabelFrame(self.frame_left_column, text="Temperature", relief = RAISED)
        frame_temperature.pack(side=TOP, fill=X)
        lbl_Temperature = Label(frame_temperature, textvariable = probe_temperature, relief = FLAT,
                                font=("Helvetica",44), padx=10)
        lbl_Temperature.pack(side=LEFT)

        #create external temperature frame
        frame_temperature_ext = LabelFrame(self.frame_left_column, text="Temperature External", relief = RAISED)
        frame_temperature_ext.pack(side=TOP, fill=X)
        lbl_Temperature_ext = Label(frame_temperature_ext, textvariable = probe_temperature_ext, relief = FLAT,
                                    font=("Helvetica",44), padx=10)
        lbl_Temperature_ext.pack(side=LEFT)

        #create ph frame
        frame_ph = LabelFrame(self.frame_left_column, text="PH", relief = RAISED)
        frame_ph.pack(side=TOP, fill=X)
        lbl_ph = Label(frame_ph, textvariable = probe_ph, relief = FLAT,
                                    font=("Helvetica",44), padx=10)
        lbl_ph.pack(side=LEFT)

        #create humidity frame
        frame_humidity = LabelFrame(self.frame_left_column, text="Humidity", relief = RAISED)
        frame_humidity.pack(side=TOP, fill=X)
        lbl_humidity = Label(frame_humidity, textvariable = probe_humidity, relief = FLAT,
                                    font=("Helvetica",44), padx=10)
        lbl_humidity.pack(side=LEFT)
            
        
        # internal temperature graph  
        def animate_temp_mini(i):
            anitemp.clear()
            print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing temperature mini graph")
            days_to_plot = 2
            for x in range(0,days_to_plot):
                DateSeed = datetime.now() - timedelta(days=x)
                LogFileName = config['logs']['temp1_log_prefix'] + DateSeed.strftime("%Y-%m-%d") + ".txt"
                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
                try:
                    pullData = open("logs/" + LogFileName,"r").read()
                    dataList = pullData.split('\n')
                    xList = []
                    yList = []
                    #print (dataList)
                    for index, eachLine in enumerate(dataList):
                        if len(eachLine) > 1:
                            x, y = eachLine.split(',')
                            x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                            xList.append(x)
                            yList.append(y)
                            #print(index, y)      
                    anitemp.plot(xList, yList, "-", color='GREEN')
                    if graphTimeFrame.get() > 1:
                        myFmt = mdates.DateFormatter('%b-%d')
                        anitemp.xaxis.set_major_formatter(myFmt)
                    else:
                        myFmt = mdates.DateFormatter('%I:%M%p')
                        anitemp.xaxis.set_major_formatter(myFmt)
                    
                    figtemp.autofmt_xdate()
                    anitemp.axes.tick_params(axis='x', labelsize=1, pad=50)
                    anitemp.axes.tick_params(axis='y', labelsize=8) 
                except:
                    print("Error: %s not available. (mini graph)" % LogFileName)
                    figtemp.autofmt_xdate()
                    anitemp.axes.tick_params(axis='x', labelsize=1, pad=50)
                    anitemp.axes.tick_params(axis='y', labelsize=8) 
                    return

        # external temperature graph
        def animate_temp_ext_mini(i):
            anitempext.clear()
            print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing external temperature mini graph")
            days_to_plot = 2
            for x in range(0,days_to_plot):
                DateSeed = datetime.now() - timedelta(days=x)
                LogFileName = config['logs']['extemp1_log_prefix'] + DateSeed.strftime("%Y-%m-%d") + ".txt"
                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
                try:
                    pullData = open("logs/" + LogFileName,"r").read()    
                    dataList = pullData.split('\n')
                    xList = []
                    yList = []
                    for index, eachLine in enumerate(dataList):
                        if len(eachLine) > 1:
                            x, y = eachLine.split(',')
                            x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                            xList.append(x)
                            yList.append(y)
                            #print(index, y)      
                    anitempext.plot(xList, yList, "-", color='GREEN')
                    if graphTimeFrame.get() > 1:
                        myFmt = mdates.DateFormatter('%b-%d')
                        anitempext.xaxis.set_major_formatter(myFmt)
                    else:
                        myFmt = mdates.DateFormatter('%I:%M%p')
                        anitempext.xaxis.set_major_formatter(myFmt)
            
                    figtempext.autofmt_xdate()
                    anitempext.axes.tick_params(axis='x', labelsize=1, pad=50)
                    anitempext.axes.tick_params(axis='y', labelsize=8) 
                except:
                    figtempext.autofmt_xdate()
                    anitempext.axes.tick_params(axis='x', labelsize=1, pad=50)
                    anitempext.axes.tick_params(axis='y', labelsize=8) 
                    print("Error: %s not available." % LogFileName)
                    return
                
        # ph graph
        def animate_ph_mini(i):
            aniph.clear()
            print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing ph mini graph")
            days_to_plot = 2
            for x in range(0,days_to_plot):
                DateSeed = datetime.now() - timedelta(days=x)
                LogFileName = config['logs']['ph_log_prefix'] + DateSeed.strftime("%Y-%m-%d") + ".txt"
                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
                try:
                    pullData = open("logs/" + LogFileName,"r").read()    
                    dataList = pullData.split('\n')
                    xList = []
                    yList = []
                    for index, eachLine in enumerate(dataList):
                        if len(eachLine) > 1:
                            x, y = eachLine.split(',')
                            x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                            xList.append(x)
                            yList.append(y)
                            #print(index, y)      
                    aniph.plot(xList, yList, "-", color='GREEN')
                    if graphTimeFrame.get() > 1:
                        myFmt = mdates.DateFormatter('%b-%d')
                        aniph.xaxis.set_major_formatter(myFmt)
                    else:
                        myFmt = mdates.DateFormatter('%I:%M%p')
                        aniph.xaxis.set_major_formatter(myFmt)
            
                    figph.autofmt_xdate()
                    aniph.axes.tick_params(axis='x', labelsize=1, pad=50)
                    aniph.axes.tick_params(axis='y', labelsize=8) 
                except:
                    figph.autofmt_xdate()
                    aniph.axes.tick_params(axis='x', labelsize=1, pad=50)
                    aniph.axes.tick_params(axis='y', labelsize=8) 
                    print("Error: %s not available." % LogFileName)
                    return

        # humidity graph
        def animate_hum_mini(i):
            anihum.clear()
            print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing humidity mini graph")
            days_to_plot = 2
            for x in range(0,days_to_plot):
                DateSeed = datetime.now() - timedelta(days=x)
                LogFileName = config['logs']['humidity_log_prefix'] + DateSeed.strftime("%Y-%m-%d") + ".txt"
                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
                try:
                    pullData = open("logs/" + LogFileName,"r").read()    
                    dataList = pullData.split('\n')
                    xList = []
                    yList = []
                    for index, eachLine in enumerate(dataList):
                        if len(eachLine) > 1:
                            x, y = eachLine.split(',')
                            x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                            xList.append(x)
                            yList.append(y)    
                    anihum.plot(xList, yList, "-", color='GREEN')
                    if graphTimeFrame.get() > 1:
                        myFmt = mdates.DateFormatter('%b-%d')
                        anihum.xaxis.set_major_formatter(myFmt)
                    else:
                        myFmt = mdates.DateFormatter('%I:%M%p')
                        anihum.xaxis.set_major_formatter(myFmt)
                    fighum.autofmt_xdate()
                    anihum.axes.tick_params(axis='x', labelsize=1, pad=50)
                    anihum.axes.tick_params(axis='y', labelsize=8) 
                except:
                    fighum.autofmt_xdate()
                    anihum.axes.tick_params(axis='x', labelsize=1, pad=50)
                    anihum.axes.tick_params(axis='y', labelsize=8) 
                    print("Error: %s not available." % LogFileName)
                    return
#############
        

##        def updateCurrentState():
##            try:
##                currentStateFile = 'RBP_currentstate.ini'
##                curstate = configparser.ConfigParser()
##                curstate.read(currentStateFile)
##                probe_temperature.set(curstate['probes']['temp1'])
##                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " current temperature = " + str(probe_temperature.get()))
##
##                probe_temperature_ext.set(curstate['probes']['ext_temp'])
##                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " current external temperature = " + str(probe_temperature_ext.get()))
##
##                probe_humidity.set(curstate['probes']['humidity'] + "%")
##                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " current humidity = " + str(probe_humidity.get()))
##
##                probe_ph.set(curstate['probes']['ph'])
##                print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " current ph = " + str(probe_ph.get()))
##                
##                #repeat the loop
##                self.after(5000,updateCurrentState)
##            except:
##                print(Back.RED + Fore.WHITE +str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
##                      " Error setting current state." + Style.RESET_ALL)
##                self.after(5000,updateCurrentState)

        ##update the display with current probe values        
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        #channel = connection.channel()
        
        #channel.queue_declare(queue='current_state')

        #print(' [*] Waiting for messages.')
        def updateCurrentState():
            method_frame, header_frame, body = channel.basic_get(queue='current_state',
                              no_ack=True)
            if body != None:
                body = body.decode()
                probe = body.split(",")[0]
                value = body.split(",")[2]
                try:
                    name = body.split(",")[4]
                except:
                    pass
                
                
                if probe == "ds18b20_1":
                    probe_temperature.set(value)
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: temperature = " + str(value) + "F")
                if probe == "dht11_t":
                    probe_temperature_ext.set(value)
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: external temperature = " + str(value) + "F")
                if probe == "dht11_h":
                    probe_humidity.set(value + "%")
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: humidity = " + str(value) + "%")
                if probe == "mcp3008_0":
                    probe_ph.set(value)
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: ph = " + str(value))
                if probe.split("_")[0] == "ds18b20":
                    # the label for the probe val is nested within a few labelframes,
                    # so need to loop down to find it
                    for widget in self.frame_left_column.winfo_children():
                        for childwidget in widget.winfo_children():
                            if childwidget.winfo_class() == "Labelframe":
                                for targetwidget in childwidget.winfo_children():     
                                    try:
                                        if targetwidget.cget("text")==probe.split("_")[1]:
                                            for w in childwidget.winfo_children():
                                                #print (probe.split("_")[1])
                                                #print (w.cget("text"))
                                                if w.cget("text") != probe.split("_")[1]:
                                                    w.config(text = str(value))
                                                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                                                        " received: " + probe.split("_")[1] + " [" + widget.cget("text") + "] = " + str(value))
                                                    break
                                    except:
                                        pass


                if value == "OFF":
                    value = OUTLET_OFF
                elif value == "ON":
                    value = OUTLET_ON
                elif value == "AUTO":
                    value = OUTLET_AUTO

                if probe == "outlet_1":
                    status = body.split(",")[3]
                    #print(body)
                    frame_int_outlet1.config(text=name)
                    if int_outlet1_freezeupdate.get() != True:
                        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: outlet_1 = " + str(value) + " Status: " + status)
                        #print (value, heater_state.get(), str(heater_freezeupdate.get()))
                        #heater_state.set(int(value))
                        if "ON" in status:
                            lbl_int_outlet1_status.config(text=status, foreground="GREEN")
                        elif "OFF" in status:
                            lbl_int_outlet1_status.config(text=status, foreground="RED")

                        # if the value is same as current state dont do anythiing
                        if int(value) != int(int_outlet1_state.get()):      
                            print ("enter if")
                            if int(value) == int(OUTLET_OFF):
                                rdo_int_outlet1_off.invoke()
                                lbl_int_outlet1_status.config(text="OFF", foreground="RED")
                            elif int(value) == int(OUTLET_AUTO):
                                rdo_int_outlet1_auto.invoke()
                                #if "ON" in status:
                                #    lbl_heater_status.config(text=status, foreground="GREEN")
                                #    print("green")
                                #elif "OFF" in status:
                                #    lbl_heater_status.config(text=status, foreground="RED")
                                #    print("red")
                            elif int(value) == int(OUTLET_ON):
                                rdo_int_outlet1_on.invoke()
                                lbl_int_outlet1_status.config(text="ON", foreground="GREEN")
                    else:
                        #print ("set it to false")
                        int_outlet1_freezeupdate.set(False)

                if probe == "int_outlet_1":
                    status = body.split(",")[3]
                    #print(body)
                    frame_int_outlet1.config(text=name)
                    if int_outlet2_freezeupdate.get() != True:
                        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: int_outlet_1 = " + str(value) + " Status: " + status)
                        #print (value, heater_state.get(), str(heater_freezeupdate.get()))
                        #heater_state.set(int(value))
                        if "ON" in status:
                            lbl_int_outlet1_status.config(text=status, foreground="GREEN")
                        elif "OFF" in status:
                            lbl_int_outlet1_status.config(text=status, foreground="RED")

                        # if the value is same as current state dont do anything
                        #print("value = " + str(value))
                        if int(value) != int(int_outlet1_state.get()):      
                            #print ("enter if " + str(value) + " " + str(return_state.get()))
                            if int(value) == int(OUTLET_OFF):
                                rdo_int_outlet1_off.invoke()
                                lbl_int_outlet1_status.config(text="OFF", foreground="RED")
                            elif int(value) == int(OUTLET_AUTO):
                                rdo_int_outlet1_auto.invoke()
                                #if "ON" in status:
                                #    lbl_heater_status.config(text=status, foreground="GREEN")
                                #    print("green")
                                #elif "OFF" in status:
                                #    lbl_heater_status.config(text=status, foreground="RED")
                                #    print("red")
                            elif int(value) == int(OUTLET_ON):
                                rdo_int_outlet1_on.invoke()
                                lbl_int_outlet1_status.config(text="ON", foreground="GREEN")
                    else:
                        #print ("set it to false")
                        int_outlet1_freezeupdate.set(False)

                if probe == "int_outlet_2":
                    status = body.split(",")[3]
                    #print(body)
                    frame_int_outlet2.config(text=name)
                    if int_outlet2_freezeupdate.get() != True:
                        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: int_outlet_2 = " + str(value) + " Status: " + status)
                        #print (value, heater_state.get(), str(heater_freezeupdate.get()))
                        #heater_state.set(int(value))
                        if "ON" in status:
                            lbl_int_outlet2_status.config(text=status, foreground="GREEN")
                        elif "OFF" in status:
                            lbl_int_outlet2_status.config(text=status, foreground="RED")

                        # if the value is same as current state dont do anything
                        #print("value = " + str(value))
                        if int(value) != int(int_outlet2_state.get()):      
                            #print ("enter if " + str(value) + " " + str(return_state.get()))
                            if int(value) == int(OUTLET_OFF):
                                rdo_int_outlet2_off.invoke()
                                lbl_int_outlet2_status.config(text="OFF", foreground="RED")
                            elif int(value) == int(OUTLET_AUTO):
                                rdo_int_outlet2_auto.invoke()
                                #if "ON" in status:
                                #    lbl_heater_status.config(text=status, foreground="GREEN")
                                #    print("green")
                                #elif "OFF" in status:
                                #    lbl_heater_status.config(text=status, foreground="RED")
                                #    print("red")
                            elif int(value) == int(OUTLET_ON):
                                rdo_int_outlet2_on.invoke()
                                lbl_int_outlet2_status.config(text="ON", foreground="GREEN")
                    else:
                        #print ("set it to false")
                        int_outlet2_freezeupdate.set(False)

                if probe == "int_outlet_3":
                    status = body.split(",")[3]
                    #print(body)
                    frame_int_outlet3.config(text=name)
                    if int_outlet3_freezeupdate.get() != True:
                        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: int_outlet_3 = " + str(value) + " Status: " + status)
                        #print (value, heater_state.get(), str(heater_freezeupdate.get()))
                        #heater_state.set(int(value))
                        if "ON" in status:
                            lbl_int_outlet3_status.config(text=status, foreground="GREEN")
                        elif "OFF" in status:
                            lbl_int_outlet3_status.config(text=status, foreground="RED")

                        # if the value is same as current state dont do anything
                        #print("value = " + str(value))
                        if int(value) != int(int_outlet3_state.get()):      
                            #print ("enter if " + str(value) + " " + str(lights_state.get()))
                            if int(value) == int(OUTLET_OFF):
                                rdo_int_outlet3_off.invoke()
                                lbl_int_outlet3_status.config(text="OFF", foreground="RED")
                            elif int(value) == int(OUTLET_AUTO):
                                rdo_int_outlet3_auto.invoke()
                                #if "ON" in status:
                                #    lbl_heater_status.config(text=status, foreground="GREEN")
                                #    print("green")
                                #elif "OFF" in status:
                                #    lbl_heater_status.config(text=status, foreground="RED")
                                #    print("red")
                            elif int(value) == int(OUTLET_ON):
                                rdo_int_outlet3_on.invoke()
                                lbl_int_outlet3_status.config(text="ON", foreground="GREEN")
                    else:
                        #print ("set it to false")
                        int_outlet3_freezeupdate.set(False)

                if probe == "int_outlet_4":
                    status = body.split(",")[3]
                    #print(body)
                    frame_int_outlet4.config(text=name)
                    if int_outlet4_freezeupdate.get() != True:
                        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: int_outlet_4 = " + str(value) + " Status: " + status)
                        #print (value, heater_state.get(), str(heater_freezeupdate.get()))
                        #heater_state.set(int(value))
                        if "ON" in status:
                            lbl_int_outlet4_status.config(text=status, foreground="GREEN")
                        elif "OFF" in status:
                            lbl_int_outlet4_status.config(text=status, foreground="RED")

                        # if the value is same as current state dont do anything
                        #print("value = " + str(value))
                        if int(value) != int(int_outlet4_state.get()):      
                            #print ("enter if " + str(value) + " " + str(skimmer_state.get()))
                            if int(value) == int(OUTLET_OFF):
                                rdo_int_outlet4_off.invoke()
                                lbl_int_outlet4_status.config(text="OFF", foreground="RED")
                            elif int(value) == int(OUTLET_AUTO):
                                rdo_int_outlet4_auto.invoke()
                                #if "ON" in status:
                                #    lbl_heater_status.config(text=status, foreground="GREEN")
                                #    print("green")
                                #elif "OFF" in status:
                                #    lbl_heater_status.config(text=status, foreground="RED")
                                #    print("red")
                            elif int(value) == int(OUTLET_ON):
                                rdo_int_outlet4_on.invoke()
                                lbl_int_outlet4_status.config(text="ON", foreground="GREEN")
                    else:
                        #print ("set it to false")
                        int_outlet4_freezeupdate.set(False)

                if probe == "feed_timer":
                    #print (body)
                    status = body.split(",")[3]
                    DefClr = btn_feedCancel.cget("bg")
                    lbl_feedtimers_status.config(text=str(timedelta(seconds=int(status))))
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: feed_timer: " + str(value) + ", Time Remaining: " + status + "s")
                    if value == "A":
                        #print ("A")
                        btn_feedA.config(background="red")
                        btn_feedB.config(background=DefClr)
                        btn_feedC.config(background=DefClr)
                        btn_feedD.config(background=DefClr)
                    elif value == "B":
                        #print("B")
                        btn_feedA.config(background=DefClr)
                        btn_feedB.config(background="red")
                        btn_feedC.config(background=DefClr)
                        btn_feedD.config(background=DefClr)
                    elif value == "C":
                        #print("C")
                        btn_feedA.config(background=DefClr)
                        btn_feedB.config(background=DefClr)
                        btn_feedC.config(background="red")
                        btn_feedD.config(background=DefClr)
                    elif value == "D":
                        #print("D")
                        btn_feedA.config(background=DefClr)
                        btn_feedB.config(background=DefClr)
                        btn_feedC.config(background=DefClr)
                        btn_feedD.config(background="red")
                    else:
                        #print ("retun default")
                        btn_feedA.config(background=DefClr)
                        btn_feedB.config(background=DefClr)
                        btn_feedC.config(background=DefClr)
                        btn_feedD.config(background=DefClr)
                        lbl_feedtimers_status.config(text="")
                    
                    
            #repeat the loop
            self.after(100,updateCurrentState)

              
        #some definitions for the plots
        LARGE_FONT= ("Verdana", 12)
        style.use("ggplot")

        #set up main temperature mini plot
        figtemp = Figure(figsize=(1,1), dpi=100)
        figtemp.set_facecolor("gainsboro")
        anitemp = figtemp.add_subplot(111, axisbg="gainsboro")
        canvastemp = FigureCanvasTkAgg(figtemp, frame_temperature)
        canvastemp.show()
        canvastemp.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

        #set up external temperature mini plot
        figtempext = Figure(figsize=(1,1), dpi=100)
        figtempext.set_facecolor("gainsboro")
        anitempext = figtempext.add_subplot(111, axisbg="gainsboro")
        canvastempext = FigureCanvasTkAgg(figtempext, frame_temperature_ext)
        canvastempext.show()
        canvastempext.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

        #set up ph mini plot
        figph = Figure(figsize=(1,1), dpi=100)
        figph.set_facecolor("gainsboro")
        aniph = figph.add_subplot(111, axisbg="gainsboro")
        canvasph = FigureCanvasTkAgg(figph, frame_ph)
        canvasph.show()
        canvasph.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

        #set up humidity mini plot
        fighum = Figure(figsize=(1,1), dpi=100)
        fighum.set_facecolor("gainsboro")
        anihum = fighum.add_subplot(111, axisbg="gainsboro")
        canvashum = FigureCanvasTkAgg(fighum, frame_humidity)
        canvashum.show()
        canvashum.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)
        
        ani2 = animation.FuncAnimation(figtemp, animate_temp_mini, interval=300000)    
        ani3 = animation.FuncAnimation(figtempext, animate_temp_ext_mini, interval=300000) 
        ani4 = animation.FuncAnimation(fighum, animate_hum_mini, interval=300000)
        ani5 = animation.FuncAnimation(figph, animate_ph_mini, interval=300000)
        
        #update the display with current probe values
        updateCurrentState()
##        channel.basic_consume(updateCurrentState,
##                      queue='current_state',
##                      no_ack=True)
##        print(' [*] Waiting for messages.')
##        channel.start_consuming()


    def readExistingProbes(self):
        # clear out the old probe dictionary
        self.probeDict.clear()
        config = configparser.ConfigParser()
        config.read(cfg_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            if section.split("_")[0] == "ds18b20":
                #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                #      "Read existing temp probe: " + section.split("_")[1])
                #print (section.split("_")[1])
                probe = ProbeClass()
                probe.probeid = section.split("_")[1]
                probe.name = config[section]["name"]
                probe.type = section.split("_")[0]
                self.probeDict [section.split("_")[1]] = probe
                print("probe class id: " + probe.probeid)
                print("probe class name: " + probe.name)
                print("probe type: " + probe.type) 

    # animate probe graph
    def animate_probe(self,i, figprobe, aniprobe, probe):
        aniprobe.clear()
        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing probe mini graph")
        days_to_plot = 2
        for x in range(0,days_to_plot):
            DateSeed = datetime.now() - timedelta(days=x)
            #LogFileName = config['logs']['humidity_log_prefix'] + DateSeed.strftime("%Y-%m-%d") + ".txt"
            LogFileName = probe.type + "_" + probe.probeid + "_" + DateSeed.strftime("%Y-%m-%d") + ".txt"
            #LogFileName = "log_extemp1_2018-11-28.txt"
            print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
            try:
                pullData = open("logs/" + LogFileName,"r").read()    
                dataList = pullData.split('\n')
                xList = []
                yList = []
                for index, eachLine in enumerate(dataList):
                    if len(eachLine) > 1:
                        x, y, z = eachLine.split(',')
                        x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                        xList.append(x)
                        yList.append(y)    
                aniprobe.plot(xList, yList, "-", color='GREEN')
                #if self.graphTimeFrame.get() > 1:
                #    myFmt = mdates.DateFormatter('%b-%d')
                #    aniprobe.xaxis.set_major_formatter(myFmt)
                #else:
                myFmt = mdates.DateFormatter('%I:%M%p')
                aniprobe.xaxis.set_major_formatter(myFmt)

                figprobe.autofmt_xdate()
                aniprobe.axes.tick_params(axis='x', labelsize=1, pad=50)
                aniprobe.axes.tick_params(axis='y', labelsize=8) 
            except:
                figprobe.autofmt_xdate()
                aniprobe.axes.tick_params(axis='x', labelsize=1, pad=50)
                aniprobe.axes.tick_params(axis='y', labelsize=8) 
                print("Error: %s not available." % LogFileName)
                return


    # create probe frame dynamically
    def createProbeFrame(self, probe):
        self.probeframe = LabelFrame(self.frame_left_column, text=probe.name, relief = RAISED)
        self.probeframe.pack(fill=X, side=TOP)
        frame_probeval = LabelFrame(self.probeframe, relief = FLAT)
        frame_probeval.pack(side=LEFT)
        lbl_probeval = Label(frame_probeval, text="00.0", relief = FLAT, 
                                    font=("Helvetica",44), padx=10)
        lbl_probeval.pack(side=TOP)
        lbl_probeSN = Label(frame_probeval,text=probe.probeid, padx=10)
        lbl_probeSN.pack(side=TOP) # dont display this, but its used to math the probe values on update
        

        #set up mini plot
        #some definitions for the plots
        LARGE_FONT= ("Verdana", 12)
        style.use("ggplot")
        figprobe = Figure(figsize=(1,1), dpi=100)
        figprobe.set_facecolor("gainsboro")
        aniprobe = figprobe.add_subplot(111, axisbg="gainsboro")
        canvasprobe = FigureCanvasTkAgg(figprobe, self.probeframe)
        canvasprobe.show()
        canvasprobe.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)
        #canvasprobe.get_tk_widget().grid(padx=10, sticky=W, row=0, column=2, columnspan=2)

        try:
            aniprobe = animation.FuncAnimation(figprobe, self.animate_probe(self, figprobe, aniprobe, probe), interval=300000)
        except:
            print("error aniprobe")
        

                
class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        
        #create toolbar frame
        frame_toolbar = tk.LabelFrame(self, relief = tk.FLAT)
        frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
        btn_DashBoard = ttk.Button(frame_toolbar, text="Dashboard", image=self.img_dashboard, 
                            compound=TOP, command=lambda: controller.show_frame(DashBoard))
        btn_DashBoard.pack(side=LEFT)

        self.img_alarm = PhotoImage(file="images/notification-64.png")
        button = ttk.Button(frame_toolbar, text="Alarm Log", image=self.img_alarm,
                            compound=TOP, command=lambda: controller.show_frame(PageOne))
        button.pack(side=LEFT)

        self.img_testlog = PhotoImage(file="images/test-tube-64.png")
        button2 = ttk.Button(frame_toolbar, text="Test Log", image=self.img_testlog,
                            compound=TOP, command=lambda: controller.show_frame(PageTwo))
        button2.pack(side=LEFT)

        self.img_graph = PhotoImage(file="images/line-chart-64.png")
        button3 = ttk.Button(frame_toolbar, text="Graphs", image=self.img_graph,
                            compound=TOP, command=lambda: controller.show_frame(PageThree))
        button3.pack(side=LEFT)
###
        label = tk.Label(self, text="Coming Soon!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(DashBoard))
        #button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        #button2.pack()
        

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
       #create toolbar frame
        frame_toolbar = tk.LabelFrame(self, relief = tk.FLAT)
        frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
        btn_DashBoard = ttk.Button(frame_toolbar, text="Dashboard", image=self.img_dashboard, 
                            compound=TOP, command=lambda: controller.show_frame(DashBoard))
        btn_DashBoard.pack(side=LEFT)

        self.img_alarm = PhotoImage(file="images/notification-64.png")
        button = ttk.Button(frame_toolbar, text="Alarm Log", image=self.img_alarm,
                            compound=TOP, command=lambda: controller.show_frame(PageOne))
        button.pack(side=LEFT)

        self.img_testlog = PhotoImage(file="images/test-tube-64.png")
        button2 = ttk.Button(frame_toolbar, text="Test Log", image=self.img_testlog,
                            compound=TOP, command=lambda: controller.show_frame(PageTwo))
        button2.pack(side=LEFT)

        self.img_graph = PhotoImage(file="images/line-chart-64.png")
        button3 = ttk.Button(frame_toolbar, text="Graphs", image=self.img_graph,
                            compound=TOP, command=lambda: controller.show_frame(PageThree))
        button3.pack(side=LEFT)
###

        label = tk.Label(self, text="Coming Soon!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(DashBoard))
        #button1.pack()

        button2 = ttk.Button(self, text="Page One",
                            command=lambda: controller.show_frame(PageOne))
        #button2.pack()


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # initialize config file
        config = configparser.ConfigParser()
        config.read('ReefberryPi.ini')
        
        # populate the GUI
        # use two frames to set up two columns
        frame_left_column=LabelFrame(self, relief = RAISED)
        frame_left_column.pack(side=LEFT, anchor=N, fill=BOTH, expand=True)
        frame_right_column=LabelFrame(self, relief = RAISED)
        frame_right_column.pack(side=RIGHT, anchor=N)    

        # create toolbar frame
        frame_toolbar = tk.LabelFrame(frame_left_column, relief = tk.FLAT)
        frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
        btn_DashBoard = ttk.Button(frame_toolbar, text="Dashboard", image=self.img_dashboard, 
                            compound=TOP, command=lambda: controller.show_frame(DashBoard))
        btn_DashBoard.pack(side=LEFT)

        self.img_alarm = PhotoImage(file="images/notification-64.png")
        button = ttk.Button(frame_toolbar, text="Alarm Log", image=self.img_alarm,
                            compound=TOP, command=lambda: controller.show_frame(PageOne))
        button.pack(side=LEFT)

        self.img_testlog = PhotoImage(file="images/test-tube-64.png")
        button2 = ttk.Button(frame_toolbar, text="Test Log", image=self.img_testlog,
                            compound=TOP, command=lambda: controller.show_frame(PageTwo))
        button2.pack(side=LEFT)

        self.img_graph = PhotoImage(file="images/line-chart-64.png")
        button3 = ttk.Button(frame_toolbar, text="Graphs", image=self.img_graph,
                            compound=TOP, command=lambda: controller.show_frame(PageThree))
        button3.pack(side=LEFT)

        # create a spacer frame
        frame_topspacer = tk.Frame(frame_left_column, height=5, relief = tk.FLAT)
        frame_topspacer.pack(side=tk.TOP, fill=tk.X)
        
        # support different graph types
        graphType = StringVar()
        graphType.set("Temperature") # default value
        def select_graph_type():
            selection = "You selected graph type " + str(graphType.get())
            print(selection)
            #animate("i")
            plotGraph(str(graphType.get()), str(graphAltType.get()), int(graphTimeFrame.get()))
            canvas.show()
        def select_main_graph_type(gtype):
            selection = "You selected main graph type " + gtype
            print(selection)
            graphType.set(str(gtype))
            plotGraph(str(graphType.get()), str(graphAltType.get()), int(graphTimeFrame.get()))
            canvas.show()
        graphAltType = StringVar()
        graphAltType.set("None") # default value
        def select_alt_graph_type(gtype):
            selection = "You selected alternate graph type " + gtype
            print(selection)
            graphAltType.set(str(gtype)) 
            plotGraph(str(graphType.get()), graphAltType.get(), int(graphTimeFrame.get()))
            canvas.show()

        # list of graph types
        altgraphchoice = StringVar()
        maingraphchoice = StringVar()
        altgraphlist = ["None","Temperature","External Temperature","PH","Humidity"]
        maingraphlist = ["Temperature","External Temperature","PH","Humidity"]
        altgraphchoice.set("None") #default value
        maingraphchoice.set("Temperature") #default value

##        # create graph type radio button frame
##        frame_graphtype = tk.LabelFrame(frame_left_column, relief = tk.FLAT)
##        frame_graphtype.pack(side=tk.TOP, fill=tk.X)
        frame_graphtype_alt = tk.LabelFrame(frame_left_column, relief = tk.FLAT)
        frame_graphtype_alt.pack(side=tk.TOP, fill=tk.X)

        # drop down list for main graph
        maingraphmenu = OptionMenu(frame_graphtype_alt,maingraphchoice,*maingraphlist,
                                   command=select_main_graph_type)
        maingraphmenu.pack(side=LEFT, fill=tk.X)

        # vs label
        lblVs = Label(frame_graphtype_alt,text="vs")
        lblVs.pack(side=LEFT, fill=tk.X)
        # drop down list for alt graph
        altgraphmenu = OptionMenu(frame_graphtype_alt,altgraphchoice,*altgraphlist,
                                   command=select_alt_graph_type)
        altgraphmenu.pack(side=LEFT, fill=tk.X)

        def select_temp_time_frame():
            selection = "You selected radio option " + str(graphTimeFrame.get()) + " days"
            print(selection)
            #animate("i")
            plotGraph(str(graphType.get()), str(graphAltType.get()), int(graphTimeFrame.get()))
            canvas.show()

                    
### START NEW GRAPH FUNC
        def plotGraph(mainGraph, altGraph, numdays):
            a.clear()
            a2.clear()
            
            # main graph
            if mainGraph == "Temperature":
                MainLogFilePrefix = config['logs']['temp1_log_prefix']
            elif mainGraph == "PH":
                MainLogFilePrefix = config['logs']['ph_log_prefix'] 
            elif mainGraph == "Humidity":
                MainLogFilePrefix = config['logs']['humidity_log_prefix']
            elif mainGraph =="External Temperature":
                MainLogFilePrefix = config['logs']['extemp1_log_prefix']
            else:
                MainLogFilePrefix = ""

            # alternate graph
            if altGraph == "Temperature":
                altLogFilePrefix = config['logs']['temp1_log_prefix']
            elif altGraph == "PH":
                altLogFilePrefix = config['logs']['ph_log_prefix'] 
            elif altGraph == "Humidity":
                altLogFilePrefix = config['logs']['humidity_log_prefix']
            elif altGraph =="External Temperature":
                altLogFilePrefix = config['logs']['extemp1_log_prefix']
            else:
                altLogFilePrefix = ""
            
            print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Refreshing large graph")
            # read graph data
            xList = []
            yList = []
            xListAlt = []
            yListAlt = []
            for x in reversed(range(0,numdays)):
                DateSeed = datetime.now() - timedelta(days=x)
                MainLogFileName = MainLogFilePrefix + DateSeed.strftime("%Y-%m-%d") + ".txt"
                AltLogFileName = altLogFilePrefix + DateSeed.strftime("%Y-%m-%d") + ".txt"
                #print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % TmpLogFileName)
                try:
                    # main graph data
                    pullData = open("logs/" + MainLogFileName,"r").read()    
                    dataList = pullData.split('\n')
                    
                    for index, eachLine in enumerate(dataList):
                        if len(eachLine) > 1:
                            x, y = eachLine.split(',')
                            x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                            xList.append(x)
                            yList.append(y)
                            #print(index, y)
                            #print(index, x, y)

                    # alt graph data
                    pullDataAlt = open("logs/" + AltLogFileName,"r").read()
                    dataListAlt = pullDataAlt.split('\n')
                    for index, eachLine in enumerate(dataListAlt):
                        if len(eachLine) > 1:
                            x, y = eachLine.split(',')
                            x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                            xListAlt.append(x)
                            yListAlt.append(y)
                    
                    
                    
                except:
                    print("Error: Log not available. (large graph) " + MainLogFileName)


            a2.plot(xListAlt, yListAlt, "-", picker=TRUE,label=altGraph, color='darkorange')
            a.plot(xList, yList, "-", picker=TRUE, label=mainGraph, color='cornflowerblue')
            a2.patch.set_visible(False) # some weird bug where first plot was hidden, but this fixes it
                                        # https://stackoverflow.com/questions/27216812/
                                        # matplotlib-cant-re-draw-first-axis-after-clearing-
                                        # second-using-twinx-and-cla
            if altGraph == "None":   
                a2.set_visible(False)
            else:
                a2.set_visible(True)
           
            if graphTimeFrame.get() > 2:
                myFmt = mdates.DateFormatter('%b-%d')
                a.xaxis.set_major_formatter(myFmt)
                a.set_xlabel('Date', weight='bold')
            else:
                myFmt = mdates.DateFormatter('%I:%M%p')
                a.xaxis.set_major_formatter(myFmt)
                a.set_xlabel('Time', weight='bold')
                    
            a.set_ylabel(graphType.get(), weight='bold')
            #a.set_xlabel('Time')
            a2.set_ylabel(altgraphchoice.get(), weight='bold')
            a.legend(loc='upper right', bbox_to_anchor=(1.00, 1.13),  shadow=True, ncol=2, fontsize = 'small')
            a2.legend(loc='upper left', bbox_to_anchor=(0.50, 1.13),  shadow=True, ncol=2, fontsize = 'small')

            f.autofmt_xdate()
### END NEW GRAPH FUNC
        #setup temperature plot
        f = Figure(figsize=(5,3), dpi=100)
        a = f.add_subplot(111)
        a2 = a.twinx()
        
        #f.set_facecolor("gainsboro")
        f.set_facecolor("lightgray")
        canvas = FigureCanvasTkAgg(f, frame_left_column)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

##        # add graph toolbar
##        frame_graphtoolbar = tk.Frame(frame_left_column, height=20, relief = tk.FLAT)
##        frame_graphtoolbar.pack(side=tk.TOP, fill=tk.X)        
##        graphtoolbar = NavigationToolbar2TkAgg(canvas, frame_graphtoolbar)
##        graphtoolbar.update()
##        canvas._tkcanvas.pack(side=TOP, fill=tk.BOTH, expand=True)
        
        graphTimeFrame = IntVar() 

        #ani = animation.FuncAnimation(f, animate, interval=3000)
        #ani = animation.FuncAnimation(f, animate, repeat=False)

        

        #radio buttons for graph time frame
        frame_timespan = tk.Frame(frame_left_column, relief = tk.FLAT)
        frame_timespan.pack(side=tk.TOP, fill=tk.X)
        
        rdo1Dy = Radiobutton(frame_timespan, text="1 Day", variable=graphTimeFrame, value=2,
                             command=select_temp_time_frame, indicatoron=0)
        rdo1Dy.pack(side=LEFT)

        rdo1Wk = Radiobutton(frame_timespan, text="1 Week", variable=graphTimeFrame, value=7,
                             command=select_temp_time_frame, indicatoron=0)
        rdo1Wk.pack(side=LEFT)

        rdo1M = Radiobutton(frame_timespan, text="1 Month", variable=graphTimeFrame, value=30,
                            command=select_temp_time_frame, indicatoron=0)
        rdo1M.pack(side=LEFT)

        # default to these
        rdo1Dy.invoke()
        #rdoTemp.invoke()
        
#################################
app = RBP_app()


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #turn off all relays when exiting
        #GPIO.output(relay_switch1, True)
        #GPIO.output(relay_switch2, True)
        #GPIO.output(relay_switch3, True)
        app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()
