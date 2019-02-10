##############################################################################
# cls_GraphPage.py
#
# this is the graphing page for the ReefBerry Pi gui app
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################

import tkinter as tk
from tkinter import * 
from tkinter import ttk
import cls_DashBoard
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
#import configparser
from datetime import datetime, timedelta, time
import time
#import logging
import defs_common
import pika
import json
import uuid
import threading

class GraphPage(tk.Frame):

    def __init__(self, parent, controller):
##        tk.Frame.__init__(self,parent)
##
##        label = tk.Label(self, text="Graph Page!")
##        label.pack(pady=10,padx=10)
##
##        button1 = ttk.Button(self, text="Back to Dashboard",
##                            command=lambda: controller.show_frame(cls_DashBoard.DashBoard))
##        button1.pack()
##
##        button2 = ttk.Button(self, text="Graphpage",
##                            command=lambda: controller.show_frame(GraphPage))
##        button2.pack()

        defs_common.logtoconsole("Initializing GraphPage...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")
        tk.Frame.__init__(self,parent)

        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.rpc_response, no_ack=True,
                                   queue=self.callback_queue)

        # initialize config file
        #config = configparser.ConfigParser()
        #config.read('ReefberryPi.ini')
        
        # populate the GUI
        # use two frames to set up two columns
        frame_left_column=LabelFrame(self, relief = RAISED)
        frame_left_column.pack(side=LEFT, anchor=N, fill=BOTH, expand=True)
        #frame_right_column=LabelFrame(self, relief = RAISED)
        #frame_right_column.pack(side=RIGHT, anchor=N)    

##        # create toolbar frame
##        frame_toolbar = tk.LabelFrame(frame_left_column, relief = tk.FLAT)
##        frame_toolbar.pack(side=tk.TOP, fill=tk.X)
##
##        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
##        btn_DashBoard = ttk.Button(frame_toolbar, text="Dashboard", image=self.img_dashboard, 
##                            compound=TOP, command=lambda: controller.show_frame(DashBoard))
##        btn_DashBoard.pack(side=LEFT)
##
##        self.img_alarm = PhotoImage(file="images/notification-64.png")
##        button = ttk.Button(frame_toolbar, text="Alarm Log", image=self.img_alarm,
##                            compound=TOP, command=lambda: controller.show_frame(PageOne))
##        button.pack(side=LEFT)
##
##        self.img_testlog = PhotoImage(file="images/test-tube-64.png")
##        button2 = ttk.Button(frame_toolbar, text="Test Log", image=self.img_testlog,
##                            compound=TOP, command=lambda: controller.show_frame(PageTwo))
##        button2.pack(side=LEFT)
##
##        self.img_graph = PhotoImage(file="images/line-chart-64.png")
##        button3 = ttk.Button(frame_toolbar, text="Graphs", image=self.img_graph,
##                            compound=TOP, command=lambda: controller.show_frame(PageThree))
##        button3.pack(side=LEFT)

        # create a spacer frame
        #frame_topspacer = tk.Frame(frame_left_column, height=5, relief = tk.FLAT)
        #frame_topspacer.pack(side=tk.TOP, fill=tk.X)
        
        # support different graph types
        graphType = StringVar()
        #graphType.set("Temperature") # default value
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
        #graphAltType.set("None") # default value
        def select_alt_graph_type(gtype):
            selection = "You selected alternate graph type " + gtype
            print(selection)
            graphAltType.set(str(gtype)) 
            plotGraph(str(graphType.get()), graphAltType.get(), int(graphTimeFrame.get()))
            canvas.show()
############################
        probelist = self.getProbeList()
        sortedprobelist = sorted(probelist['probelist'])

        sortedprobedict = {}
        for probeitem in probelist["probelist"]:
            print("Probe item = " + probeitem)
            sortedprobedict[probelist["probelist"][probeitem]["probename"]] = probeitem
            
            print("GraphProbe = " + probelist["probelist"][probeitem]["probename"])

        print(sortedprobedict)

        altsortedlist = sorted(sortedprobedict)
        altsortedlist.insert(0, "None")
###############################        
        # list of graph types
        altgraphchoice = StringVar()
        maingraphchoice = StringVar()
        altgraphlist = altsortedlist
        maingraphlist = sorted(sortedprobedict)
        maingraphchoice.set(maingraphlist[0]) #default value
        graphType.set(str(maingraphlist[0])) # default value
        altgraphchoice.set(altgraphlist[0]) #default value
        graphAltType.set(str(altgraphlist[0])) # default value

        # create graph type frame
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

            #Request main chart data from server first
            mainlogID = sortedprobedict[mainGraph]
            mainlogtype = mainlogID.split("_")[0]
            
            defs_common.logtoconsole("mainlogID: " + str(mainlogID))
            defs_common.logtoconsole("mainlogtype: " + str(mainlogtype))

            # create the request
##            mainrequest = {
##                          "rpc_req": "get_probedata24h",
##                          "probetype": mainlogtype,
##                          "probeid": mainlogID
##                      }
            mainrequest = {
                          "rpc_req": "get_probedatadays",
                          "probetype": mainlogtype,
                          "probeid": mainlogID,
                          "numdays": str(numdays)
                      }
            mainrequest = json.dumps(mainrequest)          
            mainChartData = self.rpc_call(mainrequest, "rpc_queue")

            mainChartData = mainChartData.decode()
            mainChartData = json.loads(mainChartData)

            defs_common.logtoconsole(str(mainrequest))
            defs_common.logtoconsole(str(mainChartData))


            if altGraph != "None":
                #Now lets get the data for the alt graph
                altlogID = sortedprobedict[altGraph]
                altlogtype = altlogID.split("_")[0]
                
                defs_common.logtoconsole("altlogID: " + str(altlogID))
                defs_common.logtoconsole("altlogtype: " + str(altlogtype))

                # create the request
##                altrequest = {
##                              "rpc_req": "get_probedata24h",
##                              "probetype": altlogtype,
##                              "probeid": altlogID
##                          }
                altrequest = {
                          "rpc_req": "get_probedatadays",
                          "probetype": altlogtype,
                          "probeid": altlogID,
                          "numdays": str(numdays)
                      }
                altrequest = json.dumps(altrequest)
                altChartData = self.rpc_call(altrequest, "rpc_queue")

                altChartData = altChartData.decode()
                altChartData = json.loads(altChartData)

                defs_common.logtoconsole(str(altrequest))
                defs_common.logtoconsole(str(altChartData))
            

            defs_common.logtoconsole("Refreshing large graph")

            
            # convert the string dates to datetime objects
            xList = []
            for t in mainChartData["datetime"]:
                t = datetime.strptime(t,'%Y-%m-%d %H:%M:%S')
                xList.append(t)
            yList = mainChartData["probevalue"]

            xListAlt = []
            yListAlt = []
            if altGraph != "None":
                for t in altChartData["datetime"]:
                    t = datetime.strptime(t,'%Y-%m-%d %H:%M:%S')
                    xListAlt.append(t)
                yListAlt = altChartData["probevalue"]

            a2.plot(xListAlt, yListAlt, "-", picker=TRUE,label=altGraph, color='darkorange', linewidth=2)
            a.plot(xList, yList, "-", picker=TRUE, label=mainGraph, color='cornflowerblue', linewidth=2)
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

        rdo3Dy = Radiobutton(frame_timespan, text="3 Days", variable=graphTimeFrame, value=3,
                             command=select_temp_time_frame, indicatoron=0)
        rdo3Dy.pack(side=LEFT)

        rdo1Wk = Radiobutton(frame_timespan, text="1 Week", variable=graphTimeFrame, value=7,
                             command=select_temp_time_frame, indicatoron=0)
        rdo1Wk.pack(side=LEFT)

        rdo2Wk = Radiobutton(frame_timespan, text="2 Weeks", variable=graphTimeFrame, value=14,
                             command=select_temp_time_frame, indicatoron=0)
        rdo2Wk.pack(side=LEFT)

        rdo1M = Radiobutton(frame_timespan, text="1 Month", variable=graphTimeFrame, value=30,
                            command=select_temp_time_frame, indicatoron=0)
        rdo1M.pack(side=LEFT)

        # default to these
        rdo1Dy.invoke()

        self.sendKeepAlive()
        
    def sendKeepAlive(self):
        # periodically (like every 1 or 2 minutes) send a message to the exchange so it
        # knows this channel is still active and not closed due to inactivity
        defs_common.logtoconsole("send keep alive request: " + "GraphPage", fg="YELLOW", style="BRIGHT")
        request = {
                  "rpc_req": "set_keepalive",
                  "module": "GraphPage",
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

##        print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " RPC call: " + n
##              + " UID: " + self.corr_id)
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

    def getProbeList(self):
        # get list of all probes from the server
        # request new data from server
        request = {
                      "rpc_req": "get_probelist",
                  }
        request = json.dumps(request)          
        probelist = self.rpc_call(request, "rpc_queue")
        probelist = probelist.decode()
        print (probelist)
        probelist = json.loads(probelist)

        return probelist
        
