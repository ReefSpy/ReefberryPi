import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as tkst
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
import ph_sensor
from statistics import mean
import numpy
import math

matplotlib.use("TkAgg")

LARGE_FONT = ("Verdana", 18)
LARGE_FONT_BOLD = ("Verdana", 18, 'bold')

NUMCALPOINTS = 120      # num of points to use in calibration
ph_Sigma = 1            # how many standard deviations to include 
                        # (and throw out the outliers)
binsize = 2             # bin size for each bar in the histogram graph



class CalibPH(tk.Frame):

    def __init__(self, parent, controller, ChannelID, channelName):
        tk.Frame.__init__(self, parent)

        defs_common.logtoconsole("Initializing CalibPH...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")

        # Create the queue
        self.queue = queue.Queue(  )

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        #self.running = 1

        #self.threadCal = threading.Thread(target=self.workerThread_RBPstatusListener)
        #self.threadCal.daemon = True
        #self.threadCal.start()

        self.controller = controller
        self.parent = parent
        self.ChannelID = ChannelID
        self.ChannelName = channelName
        
        # registering validation command
        #self.vldt_ifnum_cmd = (self.register(self.ValidateIfNum),'%s', '%S')

        self.isCalRunning = False
        self.calType = "none"
        self.calPoints = []
        self.currentDVlistCounter = 0
        self.currentDVlist = []

        strHeadLabel = "Channel " + str(self.ChannelID) + " [" + str(self.ChannelName) + "]"
        headlabel = tk.Label(self, text=strHeadLabel, font=LARGE_FONT)
        headlabel.grid(row=0, column=0, pady=10, sticky=W, columnspan=3)

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
        self.lbl_low_val = tk.Label(self, text=val)
        self.lbl_low_val.grid(row=2, column=2)
        btn_LowCalStart = Button(self, text="Start Low Calibration", command=lambda:self.startCalLoop('low'))
        btn_LowCalStart.grid(row=2, column=3, sticky=EW)
        # Med Val
        lbl_pointMed = tk.Label(self, text="Mid")
        lbl_pointMed.grid(row=3, column=0)
        lbl_phrefMed = tk.Label(self, text="7.0")
        lbl_phrefMed.grid(row=3, column=1)
        strval = "ch" + str(ChannelID) + "_ph_med"
        val = self.controller.controller.controller.controller.downloadsettings("mcp3008", strval, "800")
        self.lbl_med_val= tk.Label(self, text=val)
        self.lbl_med_val.grid(row=3, column=2)
        btn_MedCalStart = Button(self, text="Start Mid Calibration", command=lambda:self.startCalLoop('med'))
        btn_MedCalStart.grid(row=3, column=3, sticky=EW)
        # High Val
        lbl_pointHigh = tk.Label(self, text="High")
        lbl_pointHigh.grid(row=4, column=0)
        lbl_phrefHigh = tk.Label(self, text="10.0")
        lbl_phrefHigh.grid(row=4, column=1)
        strval = "ch" + str(ChannelID) + "_ph_high"
        val = self.controller.controller.controller.controller.downloadsettings("mcp3008", strval, "700")
        self.lbl_high_val = tk.Label(self, text=val)
        self.lbl_high_val.grid(row=4, column=2)
        btn_HighCalStart = Button(self, text="Start High Calibration", command=lambda:self.startCalLoop('high'))
        btn_HighCalStart.grid(row=4, column=3, sticky=EW)

        # Show current PH and DV val
        frame_LiveData = LabelFrame(self, text="Live Data")
        frame_LiveData.grid(row=5, column=0, columnspan=4, sticky=EW)
        lbl_curPH = tk.Label(frame_LiveData, text="Current PH:")
        lbl_curPH.grid(row=5, column=0, sticky=E, columnspan=2)
        self.lbl_curPHval = tk.Label(frame_LiveData, text="waiting...")
        self.lbl_curPHval.grid(row=5, column=2, sticky=W, padx=20)
        lbl_curDV = tk.Label(frame_LiveData, text="Current Digital Value:")
        lbl_curDV.grid(row=6, column=0, sticky=E, columnspan=2)
        self.lbl_curDVval = tk.Label(frame_LiveData, text="waiting...")
        self.lbl_curDVval.grid(row=6, column=2, sticky=W, padx=20, pady=10)


        # calibration data
        frame_CalData = LabelFrame(self, text="Calibration Data")
        frame_CalData.grid(row=7, column = 0, columnspan=4, sticky=EW)

        # cal label
        self.calLabel = Label(frame_CalData, text = " ", font=LARGE_FONT_BOLD)
        self.calLabel.grid (row=0, column = 0, columnspan=4, padx=5, pady=4, sticky=W)

        # progress bar
        self.calprogress = ttk.Progressbar(frame_CalData, orient='horizontal', mode='determinate',
                                           maximum=NUMCALPOINTS, length=450)
        self.calprogress.grid(row=1, column=0, sticky=EW, pady=10, padx=5, columnspan=6)

        # data points plot
        style.use("ggplot")
        self.figprobe = Figure(figsize=(6,2.5), dpi=100)
        self.figprobe.set_facecolor("gainsboro")
        #self.aniprobe = self.figprobe.add_subplot(111, axisbg="gainsboro")
        self.aniprobe = self.figprobe.add_subplot(111)
        
        self.canvasprobe = FigureCanvasTkAgg(self.figprobe, frame_CalData)
        
        self.canvasprobe.show()
        self.canvasprobe.get_tk_widget().grid(sticky=EW, row=2, column=2, columnspan=4)

        # histogram plot
        self.fighist, self.axhist = plt.subplots()
        plt.title("Histogram")
        self.fighist.set_facecolor("gainsboro")
        self.fighist.set_size_inches(6,2.5)
        self.fighist.set_dpi(100)
        self.axhist.axes.tick_params(axis='x', labelsize=8)
        self.axhist.axes.tick_params(axis='y', labelsize=8)
        self.axhist.axes.set_xlim([0,1023])
       
        
        self.canvashist = FigureCanvasTkAgg(self.fighist, frame_CalData)
        self.canvashist.show()
        self.canvashist.get_tk_widget().grid(sticky=EW, row=3, column=2, columnspan=4)
        
        
        ani = animation.FuncAnimation(self.figprobe, self.animate_probe, interval=1000)

        # scrolled textbox for calibration values
        self.txt_calPoints = tkst.ScrolledText(frame_CalData, width=15, height=10, wrap='word')
        self.txt_calPoints.grid(row=2, column=0, sticky=NSEW, padx=5, columnspan=2 )

        # results area
        self.frame_Results = LabelFrame(frame_CalData, text="Results") 
        self.frame_Results.grid(row=3, column=0, sticky=NSEW, columnspan=2)

        self.lbl_num_Samples = Label(self.frame_Results, text="Num. Samples:")
        self.lbl_num_Samples.grid(row=0, column=0, sticky=E)
        self.lbl_num_SamplesVal = Label(self.frame_Results, text="", width=10)
        self.lbl_num_SamplesVal.grid(row=0, column=1, sticky=EW)    

        self.lbl_resultMin = Label(self.frame_Results, text="Min:")
        self.lbl_resultMin.grid(row=1, column=0, sticky=E)
        self.lbl_resultMinVal = Label(self.frame_Results, text="", width=10)
        self.lbl_resultMinVal.grid(row=1, column=1, sticky=EW)

        self.lbl_resultMax = Label(self.frame_Results, text="Max:")
        self.lbl_resultMax.grid(row=2, column=0, sticky=E)
        self.lbl_resultMaxVal = Label(self.frame_Results, text="", width=10)
        self.lbl_resultMaxVal.grid(row=2, column=1, sticky=EW)

        self.lbl_resultMean = Label(self.frame_Results, text="Mean:")
        self.lbl_resultMean.grid(row=3, column=0, sticky=E)
        self.lbl_resultMeanVal = Label(self.frame_Results, text="", width=10)
        self.lbl_resultMeanVal.grid(row=3, column=1, sticky=EW)

        self.lbl_resultStdDev = Label(self.frame_Results, text="Std. Deviation:")
        self.lbl_resultStdDev.grid(row=4, column=0, sticky=E)
        self.lbl_resultStdDevVal = Label(self.frame_Results, text="", width=10)
        self.lbl_resultStdDevVal.grid(row=4, column=1, sticky=EW)

        self.lbl_resultCalval = Label(self.frame_Results, text="Calibration Value:")
        self.lbl_resultCalval.grid(row=5, column=0, sticky=E)
        self.lbl_resultCalvalVal = Label(self.frame_Results, text="", width=10, font=LARGE_FONT_BOLD)
        self.lbl_resultCalvalVal.grid(row=5, column=1, sticky=EW, pady=20)

        self.btn_ApplyCal = Button(self.frame_Results, text="Apply Calibration Value", command=self.ApplyCal)
        self.btn_ApplyCal.grid(row=6, column=0, columnspan=2, sticky=EW)
        
        
        # Start the periodic call to check if the queue contains
        # anything
        #self.periodicCall()

        self.currentADCLoop(self.ChannelID)

    def startCalLoop(self, calPoint):

        self.isCalRunning = True

        #reset stats
        self.calprogress['value'] = 0
        self.txt_calPoints.delete(1.0, END)
        self.lbl_resultMeanVal.config(text="")
        self.lbl_num_SamplesVal.config(text="")
        self.lbl_resultStdDevVal.config(text="")
        self.lbl_resultMinVal.config(text="")
        self.lbl_resultMaxVal.config(text="")
        self.lbl_resultCalvalVal.config(text="")

        #clear old data plot
        self.aniprobe.cla()
        #remove old histogram if exists
        try:
            t = [b.remove() for b in self.patches]
            print(t)
            self.canvashist.show()
        except:
            print("no bars")

        self.calPoints.clear()
        
        if calPoint=='low':
            print("calLoop low")
            self.caltype = "low"           
            self.calLabel['text'] = "Low Calibration: In Progress..."
        if calPoint=='med':
            print("calLoop med")
            self.caltype = "med"
            self.calLabel['text'] = "Mid Calibration: In Progress..."
        if calPoint=='high':
            print("calLoop high")
            self.caltype = "high"
            self.calLabel['text'] = "High Calibration: In Progress..."
        

    def currentADCLoop(self, chnum):
        try:
            # get setting value from server
            request = {
                      "rpc_req": "get_ADCfromMCP3008",
                      "ch_num": str(chnum),
                  }
            request = json.dumps(request)          
            val = self.controller.controller.controller.controller.rpc_call(request, "rpc_queue")
            val = val.decode()
            val = json.loads(val)
            val = val.get("dv")

            print (val)
            #self.lbl_curDVval.configure(text=val)

            # buffer for current PH vals
            if self.currentDVlistCounter < 9:
                self.currentDVlistCounter = self.currentDVlistCounter +1
            else:
                self.currentDVlistCounter = 0
                

            if len(self.currentDVlist) < 10:
                self.currentDVlist.append(val)
                #print("in")
            else:
                self.currentDVlist[self.currentDVlistCounter] = val
                #print("out")
            print("counter = " + str(self.currentDVlistCounter))
            print("Current DV list: = " + str (self.currentDVlist))
            phVal = ph_sensor.dv2ph(int(mean(self.currentDVlist)), self.ChannelID, self.lbl_low_val.cget("text"),
                                                                   self.lbl_med_val.cget("text"),
                                                                   self.lbl_high_val.cget("text"))
            print('{0:.2f}'.format(float(phVal)))
            self.lbl_curPHval.configure(text='{0:.2f}'.format(float(phVal)), font=LARGE_FONT_BOLD)
            self.lbl_curDVval.configure(text=str(self.currentDVlist))

            if self.isCalRunning == True:
                print("cal in progress")
                self.calPoints.append(val)
                print(self.calPoints)
                self.calprogress['value'] = len(self.calPoints)

                strVal = str(len(self.calPoints)) + ":" + str(val)
                self.txt_calPoints.insert(END, str(strVal) + '\n')
                self.txt_calPoints.see('end')

                #plot new point
                #self.animate_probe(self.figprobe)

                calPtArray = numpy.array(self.calPoints)
                stdDev = numpy.std(calPtArray, axis=0)
                meanDV = mean(self.calPoints)
                minDV = min(self.calPoints)
                maxDV = max(self.calPoints)
                print("std dev = " + str(stdDev))
                print(meanDV+stdDev)
                self.lbl_resultMeanVal.config(text=str('{:.2f}'.format(meanDV)))
                self.lbl_num_SamplesVal.config(text=str(len(self.calPoints)))
                self.lbl_resultStdDevVal.config(text=str('{:.2f}'.format(stdDev)))                    
                self.lbl_resultMinVal.config(text=str(minDV))
                self.lbl_resultMaxVal.config(text=str(maxDV))

                if len(self.calPoints) >= NUMCALPOINTS:       
                    print("mean = " + str(mean(self.calPoints)))
                    
                    if self.caltype == 'low':
                        #self.lbl_low_val.config(text=int(mean(self.calPoints)))
                        self.calLabel['text'] = "Low Calibration: Aquisition Complete"
                    elif self.caltype == 'med':
                        #self.lbl_med_val.config(text=int(mean(self.calPoints)))
                        self.calLabel['text'] = "Mid Calibration: Aquisition Complete"
                    elif self.caltype == 'high':
                        #self.lbl_high_val.config(text=int(mean(self.calPoints)))
                        self.calLabel['text'] = "High Calibration: Aquisition Complete"

                    

                    FilteredCountList = [x for x in self.calPoints if
                                            (x >= meanDV - ph_Sigma * stdDev)]
                    FilteredCountList = [x for x in FilteredCountList if
                                            (x <= meanDV + ph_Sigma * stdDev)]

                    print("Cal point = " + str(int(mean(FilteredCountList))))
                    
                    self.lbl_resultCalvalVal.config(text=str(int(math.ceil(mean(FilteredCountList)))))

                    self.plot_hist()
                    self.isCalRunning = False
                   
                    

##            phVal = ph_sensor.dv2ph(val, self.ChannelID, self.lbl_low_val.cget("text"),
##                                                         self.lbl_med_val.cget("text"),
##                                                         self.lbl_high_val.cget("text"))
##            print('{0:.2f}'.format(float(phVal)))
##            self.lbl_curPHval.configure(text='{0:.2f}'.format(float(phVal)))

            self.after(1000, self.currentADCLoop, chnum)
            
            #return val
        except Exception as e:
            print(e)
            pass

    def getADCval(self, chnum):
        # get setting value from server
        request = {
                  "rpc_req": "get_ADCfromMCP3008",
                  "ch_num": str(chnum),
              }
        request = json.dumps(request)          
        val = self.controller.controller.controller.controller.rpc_call(request, "rpc_queue")
        val = val.decode()
        val = json.loads(val)
        val = val.get("dv")

        print (val)
        
        return val
        
##    def periodicCall(self):
##        
##        # Check every 100 ms if there is something new in the queue.
##        
##        self.processIncoming(  )
##        print("Running = " + str(self.running))
##        if not self.running:
##            # This is the brutal stop of the system. You may want to do
##            # some cleanup before actually shutting it down.
##            #import sys
##            print("I am trying to stop")
##            #sys.exit(1)
##            
##        self.master.after(100, self.periodicCall)

##    def processIncoming(self):
##        """Handle all messages currently in the queue, if any."""
##        while self.queue.qsize(  ):
##            try:
##                msg = self.queue.get(0)
##                #print(msg)
##                # Check contents of message and do whatever is needed. As a
##                # simple test, print it (in real life, you would
##                # suitably update the GUI's display in a richer fashion).
##                #defs_common.logtoconsole("processIncoming " + str(msg))
##                msg = json.loads(msg)
##                 
##                for key in msg:
##                    #print(key)
##                    if key == "status_currentprobeval":
##                        curID = str(msg["status_currentprobeval"]["probeid"])
##                        curVal = str(msg["status_currentprobeval"]["probeval"])
##                        curName = str(msg["status_currentprobeval"]["probename"])
##                        print(curID + " " + curVal + " " + curName)
##
##                        #if curID == "mcp3008_ch" + str(self.ChannelID):
##                        #    self.lbl_curPHval.configure(text='{0:.2f}'.format(float(curVal)))
##
####                        if curID == "dht_h": #if this is a humidity value, tack on the % sign
####                            curVal = str(curVal) + "%"
####                        self.frames[cls_DashBoard.DashBoard].updateProbeVal(curID, curVal, curName)
####
####                    if key == "status_currentoutletstate":    
####                        #defs_common.logtoconsole(str(msg), fg="MAGENTA", bg="GREEN")
####                        self.frames[cls_DashBoard.DashBoard].updateOutletStatus(str(msg["status_currentoutletstate"]["outletid"]),
####                                                                                str(msg["status_currentoutletstate"]["outletname"]),
####                                                                                str(msg["status_currentoutletstate"]["outletbus"]),
####                                                                                str(msg["status_currentoutletstate"]["control_type"]),
####                                                                                str(msg["status_currentoutletstate"]["button_state"]),
####                                                                                str(msg["status_currentoutletstate"]["outletstate"]),
####                                                                                str(msg["status_currentoutletstate"]["statusmsg"]))
####                    if key == "status_feedmode":
####                        defs_common.logtoconsole(str(msg), fg="MAGENTA", bg="GREEN")
####                        feedmode = str(msg["status_feedmode"]["feedmode"])
####                        timeremaining = str(msg["status_feedmode"]["timeremaining"])
####                        self.frames[cls_DashBoard.DashBoard].feedFrame.updatefeedstatus(feedmode, timeremaining)
##                        
##                        
##            except queue.Empty:
##                # just on general principles, although we don't
##                # expect this branch to be taken in this case
##                pass
##
##
##    def workerThread_RBPstatusListener(self):
##        # check for new messages in the messanging exchange
##        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
##        channel = connection.channel()
##
##        channel.exchange_declare(exchange='rbp_currentstatus',
##                                 exchange_type='fanout')
##
##        target=self.handle_RBPstatus(channel)
##
##    def handle_RBPstatus(self, channel):
##        result = channel.queue_declare(exclusive=True)
##        queue_name = result.method.queue
##
##        channel.queue_bind(exchange='rbp_currentstatus',
##                           queue=queue_name)
##        def callback(ch, method, properties, body):
##            body = body.decode()
##            #print(" [x] %r" % body)
##            self.queue.put(body)
##
##
##        channel.basic_consume(callback,
##                              queue=queue_name,
##                              no_ack=True)
##
##        defs_common.logtoconsole("Listening for status updates on exchange: rbp_currentstatus")
##        channel.start_consuming()

    # plot calibration data
    def animate_probe(self, i):
        if self.isCalRunning == True:
            self.aniprobe.clear()
            chartData = self.calPoints
            dim = numpy.arange(1, len(chartData)+1)
            #print(dim)
            #print(chartData)
            self.aniprobe.set_title("Data Points")
            try:
                self.aniprobe.plot(dim, chartData,  "-", color='GREEN')
                self.aniprobe.axes.tick_params(axis='x', labelsize=8)
                self.aniprobe.axes.tick_params(axis='y', labelsize=8)
                self.aniprobe.axes.set_xlim([1,None])
                 
            except:           
                print("Error plotting data")
                pass
            if len(chartData) > 1:
                meanDV = mean(self.calPoints)
                calPtArray = numpy.array(chartData)
                stdDev = numpy.std(calPtArray, axis=0)


                FilteredCountList = [x for x in self.calPoints if
                                            (x >= meanDV - ph_Sigma * stdDev)]
                FilteredCountList = [x for x in FilteredCountList if
                                            (x <= meanDV + ph_Sigma * stdDev)]
                targetMeanDV = mean(FilteredCountList)
                targetDV = int(math.ceil(targetMeanDV))
                self.aniprobe.axhline(y=(targetDV), color='red')
                #self.aniprobe.axhline(y=(meanDV), color='red')
                
                self.aniprobe.axhline(y=math.ceil(meanDV+stdDev), color='black', linestyle='-.')
                self.aniprobe.axhline(y=math.ceil(meanDV-stdDev), color='black', linestyle='-.')

                
                t = self.aniprobe.text(1, targetDV,str(targetDV) , fontsize=24)
                #t = self.aniprobe.text(1, meanDV, str("{:.2f}".format(meanDV)), fontsize=24)
                t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='black'))
            return

    # plot calibration histogram
    def plot_hist(self):
        
        try:
            # lets plot the histogram
            bins = range (0,1023,binsize) # set up bins for histogram
            #minbin = min(self.calPoints)
            #maxbin = max(self.calPoints)
            #bins = range (minbin,maxbin,binsize) # set up bins for histogram
            #self.axhist.axes.set_xlim([minbin,maxbin])
            n, dvbins, self.patches = self.axhist.hist(self.calPoints, bins, color = "royalblue", ec="royalblue")
            
            self.canvashist.show()
        except:           
            print("Error plotting histogram")
            pass
        
        return

    def ApplyCal(self):
        self.running = 0
        try:
            calVal = self.lbl_resultCalvalVal.cget("text")
            if self.caltype == 'low':
                self.lbl_low_val.config(text=int(calVal))         
            elif self.caltype == 'med':
                self.lbl_med_val.config(text=int(calVal))
            elif self.caltype == 'high':
                self.lbl_high_val.config(text=int(calVal))
        except Exception as e:
            print(e)
                        
