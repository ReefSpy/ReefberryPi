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
#import RBP_outletcfg

LARGE_FONT= ("Verdana", 12)
OUTLET_OFF = 1
OUTLET_AUTO = 2
OUTLET_ON = 3

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
        heater_state = IntVar()
        return_state = IntVar()
        lights_state = IntVar()
        skimmer_state = IntVar()
        heater_freezeupdate = BooleanVar()
        outlet1_state = IntVar()
        outlet1_freezeupdate = BooleanVar()
        
        #initialize the default values
        probe_temperature.set("-1")
        probe_temperature_ext.set("-1")
        probe_humidity.set("-1")
        probe_ph.set("-1")
        #humidity_display.set("-1")
        heater_freezeupdate.set(True)
        outlet1_freezeupdate.set(True)

        #populate the GUI
        #use two frames to set up two columns
        frame_left_column=LabelFrame(self, relief = RAISED)
        frame_left_column.pack(side=LEFT, anchor=N, fill=X, expand=True)
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

        def writeCurrentState(section, key, value):
            currentStateFile = 'RBP_currentstate.ini'
            curstate = configparser.ConfigParser()
            curstate.read(currentStateFile)
            curstate[section][key] = str(value)
            with open(currentStateFile,'w') as configfile:
                curstate.write(configfile)

##        def select_outlet1_state():
##            if heater_state.get() == OUTLET_OFF:
##                lbl_heater_status.config(text="OFF", foreground="RED")
##                #GPIO.output(relay_switch1, True)
##                #writeCurrentState('relays','relay_heater', "OFF")
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("outlet_1" + "," + str(OUTLET_OFF)))
##            elif heater_state.get() == OUTLET_AUTO:
##                lbl_heater_status.config(text="AUTO", foreground="DARK ORANGE")
##                #writeCurrentState('relays','relay_heater', "AUTO")
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("outlet_1" + "," + str(OUTLET_AUTO)))
##            elif heater_state.get() == OUTLET_ON:
##                lbl_heater_status.config(text="ON", foreground="GREEN")
##                #GPIO.output(relay_switch1, False)
##                #writeCurrentState('relays','relay_heater', "ON")
##                channel.basic_publish(exchange='',
##                                      routing_key='outlet_change',
##                                      properties=pika.BasicProperties(expiration='30000'),
##                                      body=str("outlet_1" + "," + str(OUTLET_ON)))
##            else:
##                lbl_heater_status.config(text="UNKNOWN", foreground="BLACK")
##                #writeCurrentState('relays','relay_heater', "OFF")
##            selection = "You selected heater option " + lbl_heater_status.cget("text")
##            print(selection)
##            heater_freezeupdate.set(True) 

        def select_heater_state():
            if heater_state.get() == OUTLET_OFF:
                lbl_heater_status.config(text="OFF", foreground="RED")
                #GPIO.output(relay_switch1, True)
                #writeCurrentState('relays','relay_heater', "OFF")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("outlet_1" + "," + str(OUTLET_OFF)))
            elif heater_state.get() == OUTLET_AUTO:
                lbl_heater_status.config(text="AUTO", foreground="DARK ORANGE")
                #writeCurrentState('relays','relay_heater', "AUTO")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("outlet_1" + "," + str(OUTLET_AUTO)))
            elif heater_state.get() == OUTLET_ON:
                lbl_heater_status.config(text="ON", foreground="GREEN")
                #GPIO.output(relay_switch1, False)
                #writeCurrentState('relays','relay_heater', "ON")
                channel.basic_publish(exchange='',
                                      routing_key='outlet_change',
                                      properties=pika.BasicProperties(expiration='30000'),
                                      body=str("outlet_1" + "," + str(OUTLET_ON)))
            else:
                lbl_heater_status.config(text="UNKNOWN", foreground="BLACK")
                #writeCurrentState('relays','relay_heater', "OFF")
            selection = "You selected heater option " + lbl_heater_status.cget("text")
            print(selection)
            heater_freezeupdate.set(True) 

        def select_return_state():
            if return_state.get() == OUTLET_OFF:
                lbl_return_status.config(text="OFF", foreground="RED")
                #GPIO.output(relay_switch2, True)
                #writeCurrentState('relays','relay_return', "OFF")
            elif return_state.get() == OUTLET_AUTO:
                lbl_return_status.config(text="AUTO", foreground="DARK ORANGE")
                #writeCurrentState('relays','relay_return', "AUTO")
            elif return_state.get() == OUTLET_ON:
                lbl_return_status.config(text="ON", foreground="GREEN")
                #GPIO.output(relay_switch2, False)
                #writeCurrentState('relays','relay_return', "ON")
            else:
                lbl_return_status.config(text="UNKNOWN", foreground="BLACK")
                #writeCurrentState('relays','relay_return', "OFF")
            selection = "You selected return pump option " + lbl_return_status.cget("text")
            print(selection) 

        def select_lights_state():
            if lights_state.get() == OUTLET_OFF:
                lbl_lights_status.config(text="OFF", foreground="RED")
                #GPIO.output(relay_switch3, True)
                writeCurrentState('relays','relay_lights', "OFF")
            elif lights_state.get() == OUTLET_AUTO:
                lbl_lights_status.config(text="AUTO", foreground="DARK ORANGE")
                writeCurrentState('relays','relay_lights', "AUTO")
            elif lights_state.get() == OUTLET_ON:
                lbl_lights_status.config(text="ON", foreground="GREEN")
                writeCurrentState('relays','relay_lights', "ON")
                #GPIO.output(relay_switch3, False)
            else:
                lbl_lights_status.config(text="UNKNOWN", foreground="BLACK")
                writeCurrentState('relays','relay_lights', "OFF")
            selection = "You selected lights option " + lbl_lights_status.cget("text")
            print(selection) 
            
        def select_skimmer_state():
            if skimmer_state.get() == OUTLET_OFF:
                lbl_skimmer_status.config(text="OFF", foreground="RED")
                writeCurrentState('relays','relay_skimmer', "OFF")
                #GPIO.output(relay_switch4, True)
            elif skimmer_state.get() == OUTLET_AUTO:
                lbl_skimmer_status.config(text="AUTO", foreground="DARK ORANGE")
                writeCurrentState('relays','relay_skimmer', "AUTO")
            elif skimmer_state.get() == OUTLET_ON:
                lbl_skimmer_status.config(text="ON", foreground="GREEN")
                writeCurrentState('relays','relay_skimmer', "ON")
                #GPIO.output(relay_switch4, False)
            else:
                lbl_skimmer_status.config(text="UNKNOWN", foreground="BLACK")
                writeCurrentState('relays','relay_skimmer', "OFF")
            selection = "You selected skimmer option " + lbl_skimmer_status.cget("text")
            print(selection)

        self.img_cfg16 = PhotoImage(file="images/settings-16.png")

        
##        def cfg_outlet():
##            outletwin = tk.Toplevel(master=app)
##            outletwin.transient(app)
##            outletwin.grab_set()
            
        
        # frame for heater control
        frame_heater = LabelFrame(frame_right_column, text="Heater", relief= RAISED)
        frame_heater.pack(fill=X, side=TOP)
        frame_outlet1_spacer = tk.LabelFrame(frame_heater, relief = tk.FLAT)
        frame_outlet1_spacer.pack(fill=X, side=TOP)
        #btn_cfg_outlet1 = Button(frame_outlet1_spacer, text = "edit", image=self.img_cfg16,
        #                         relief = FLAT, command = RBP_outletcfg.init())
        #btn_cfg_outlet1.pack(side=LEFT, anchor=W)
        lbl_heater_status = Label(frame_outlet1_spacer, text = "waiting...", relief = FLAT)
        lbl_heater_status.pack(side=TOP, anchor=E)                          
        rdo_heater_off = Radiobutton(frame_heater, text="Off", variable=heater_state,
                                     value=1, command=select_heater_state,
                                     indicatoron=0)
        rdo_heater_off.pack(side=LEFT, expand=1, fill=X)

        rdo_heater_auto = Radiobutton(frame_heater, text="Auto", variable=heater_state,
                              value=2, command=select_heater_state,
                              indicatoron=0)
        rdo_heater_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_heater_on = Radiobutton(frame_heater, text="On", variable=heater_state,
                                    value=3, command=select_heater_state,
                                    indicatoron=0)
        rdo_heater_on.pack(side=LEFT, expand=1, fill=X)

        # frame for return pump control
        frame_return = LabelFrame(frame_right_column, text="Return Pump", relief= RAISED)
        frame_return.pack(fill=X, side=TOP)
        lbl_return_status = Label(frame_return, text = "waiting...", relief = FLAT)
        lbl_return_status.pack(side=TOP, anchor=E)                          
        rdo_return_off = Radiobutton(frame_return, text="Off", variable=return_state, value=1,
                             command=select_return_state, indicatoron=0)
        rdo_return_off.pack(side=LEFT, expand=1, fill=X)

        rdo_return_auto = Radiobutton(frame_return, text="Auto", variable=return_state, value=2,
                             command=select_return_state, indicatoron=0)
        rdo_return_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_return_on = Radiobutton(frame_return, text="On", variable=return_state, value=3,
                             command=select_return_state, indicatoron=0)
        rdo_return_on.pack(side=LEFT, expand=1, fill=X)

        # frame for lights control
        frame_lights = LabelFrame(frame_right_column, text="Lights", relief= RAISED)
        frame_lights.pack(fill=X, side=TOP)
        lbl_lights_status = Label(frame_lights, text = "waiting...", relief = FLAT)
        lbl_lights_status.pack(side=TOP, anchor=E)                          
        rdo_lights_off = Radiobutton(frame_lights, text="Off", variable=lights_state, value=1,
                             command=select_lights_state, indicatoron=0)
        rdo_lights_off.pack(side=LEFT, expand=1, fill=X)

        rdo_lights_auto = Radiobutton(frame_lights, text="Auto", variable=lights_state, value=2,
                             command=select_lights_state, indicatoron=0)
        rdo_lights_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_lights_on = Radiobutton(frame_lights, text="On", variable=lights_state, value=3,
                             command=select_lights_state, indicatoron=0)
        rdo_lights_on.pack(side=LEFT, expand=1, fill=X)

        # frame for skimmer control
        frame_skimmer = LabelFrame(frame_right_column, text="Skimmer", relief= RAISED)
        frame_skimmer.pack(fill=X, side=TOP)
        lbl_skimmer_status = Label(frame_skimmer, text = "waiting...", relief = FLAT)
        lbl_skimmer_status.pack(side=TOP, anchor=E)                          
        rdo_skimmer_off = Radiobutton(frame_skimmer, text="Off", variable=skimmer_state, value=1,
                             command=select_skimmer_state, indicatoron=0)
        rdo_skimmer_off.pack(side=LEFT, expand=1, fill=X)

        rdo_skimmer_auto = Radiobutton(frame_skimmer, text="Auto", variable=skimmer_state, value=2,
                             command=select_skimmer_state, indicatoron=0)
        rdo_skimmer_auto.pack(side=LEFT, expand=1, fill=X)

        rdo_skimmer_on = Radiobutton(frame_skimmer, text="On", variable=skimmer_state, value=3,
                             command=select_skimmer_state, indicatoron=0)
        rdo_skimmer_on.pack(side=LEFT, expand=1, fill=X)


        #create temperature frame
        frame_temperature = LabelFrame(frame_left_column, text="Temperature", relief = RAISED)
        frame_temperature.pack(side=TOP, fill=X)
        lbl_Temperature = Label(frame_temperature, textvariable = probe_temperature, relief = FLAT,
                                font=("Helvetica",44), padx=10)
        lbl_Temperature.pack(side=LEFT)

        #create external temperature frame
        frame_temperature_ext = LabelFrame(frame_left_column, text="Temperature External", relief = RAISED)
        frame_temperature_ext.pack(side=TOP, fill=X)
        lbl_Temperature_ext = Label(frame_temperature_ext, textvariable = probe_temperature_ext, relief = FLAT,
                                    font=("Helvetica",44), padx=10)
        lbl_Temperature_ext.pack(side=LEFT)

        #create ph frame
        frame_ph = LabelFrame(frame_left_column, text="PH", relief = RAISED)
        frame_ph.pack(side=TOP, fill=X)
        lbl_ph = Label(frame_ph, textvariable = probe_ph, relief = FLAT,
                                    font=("Helvetica",44), padx=10)
        lbl_ph.pack(side=LEFT)

        #create humidity frame
        frame_humidity = LabelFrame(frame_left_column, text="Humidity", relief = RAISED)
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
                
                if probe == "ds18b20_1":
                    probe_temperature.set(value)
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: temperature = " + str(value) + "F")
                elif probe == "dht11_t":
                    probe_temperature_ext.set(value)
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: external temperature = " + str(value) + "F")
                elif probe == "dht11_h":
                    probe_humidity.set(value + "%")
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: humidity = " + str(value) + "%")
                elif probe == "mcp3008_0":
                    probe_ph.set(value)
                    print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                          " received: ph = " + str(value))
                elif probe == "outlet_1":
                    status = body.split(",")[3]
                    #print(body)
                    if heater_freezeupdate.get() != True:
                        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
                              " received: outlet_1 = " + str(value) + " Status: " + status)
                        #print (value, heater_state.get(), str(heater_freezeupdate.get()))
                        #heater_state.set(int(value))
                        if "ON" in status:
                            lbl_heater_status.config(text=status, foreground="GREEN")
                        elif "OFF" in status:
                            lbl_heater_status.config(text=status, foreground="RED")

                        # if the value is same as current state dont do anythiing
                        if int(value) != int(heater_state.get()):      
                            print ("enter if")
                            if int(value) == int(OUTLET_OFF):
                                rdo_heater_off.invoke()
                                lbl_heater_status.config(text="OFF", foreground="RED")
                            elif int(value) == int(OUTLET_AUTO):
                                rdo_heater_auto.invoke()
                                #if "ON" in status:
                                #    lbl_heater_status.config(text=status, foreground="GREEN")
                                #    print("green")
                                #elif "OFF" in status:
                                #    lbl_heater_status.config(text=status, foreground="RED")
                                #    print("red")
                            elif int(value) == int(OUTLET_ON):
                                rdo_heater_on.invoke()
                                lbl_heater_status.config(text="ON", foreground="GREEN")
                    else:
                        #print ("set it to false")
                        heater_freezeupdate.set(False) 
            #repeat the loop
            self.after(1000,updateCurrentState)

              
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
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(DashBoard))
        button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        

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

        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(DashBoard))
        button1.pack()

        button2 = ttk.Button(self, text="Page One",
                            command=lambda: controller.show_frame(PageOne))
        button2.pack()


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
