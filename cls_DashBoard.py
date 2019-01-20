##############################################################################
# cls_DashBoard.py
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
from datetime import datetime, timedelta, time
import configparser
import cls_GraphPage
import cls_ProbeWidget
import cls_OutletWidget
import cls_FeedWidget
import defs_common
import json
import uuid
import pika

class DashBoard(tk.Frame):

    def __init__(self, parent, controller):
        defs_common.logtoconsole("Initializing Dashboard...", fg = "YELLOW", bg = "MAGENTA", style = "BRIGHT")
        tk.Frame.__init__(self,parent)

        #initialize the messaging queues      
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
##########
##        self.statuschannel = self.connection.channel()
##        self.statuschannel.exchange_declare(exchange='rbp_probestatus',
##                                            exchange_type='fanout')
##
##        self.result = self.statuschannel.queue_declare(exclusive=True)
##        self.queue_name = self.result.method.queue
##
##        self.statuschannel.queue_bind(exchange='rbp_probestatus',
##                   queue=self.queue_name)
##
##                
##        def callback(ch, method, properties, body):
##            body = body.decode()
##            #print(" [x] %r" % body)
##
##        self.statuschannel.basic_consume(callback,
##                      queue=self.queue_name,
##                      no_ack=True)
##
##        #self.statuschannel.start_consuming()
##        method_frame, header_frame, body = self.statuschannel.basic_get(queue=self.queue_name,
##                              no_ack=True)
##        #print(self.queue_name)
##        if body != None:
##            body = body.decode()

###############
        
        
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.rpc_response, no_ack=True,
                                   queue=self.callback_queue)

        # create dictionary to hold assigned probes and outlets
        self.probeDict = {}
        self.outletDict = {}

        self.canvas = tk.Canvas(self, borderwidth=0)

        self.frame_master=Frame(self.canvas, relief=FLAT)
        self.frame_master.pack(side=LEFT, fill=BOTH)
        self.frame_left_column=LabelFrame(self.frame_master, relief = RAISED)
        self.frame_left_column.pack(side=LEFT, anchor=N, fill=Y)
        self.frame_mid_column=LabelFrame(self.frame_master, relief = RAISED)
        self.frame_mid_column.pack(side=LEFT, anchor=N, fill=Y)
        self.frame_right_column=LabelFrame(self.frame_master, relief = RAISED)
        self.frame_right_column.pack(side=LEFT, anchor=N)

        self.frameProbes = tk.Frame(self.frame_left_column, width=470)
        self.frameProbes.pack(side=TOP, anchor=N, fill=BOTH, expand=True)
        self.frameSpaceFrame = Frame(self.frame_left_column, width=470, height=1)
        self.frameSpaceFrame.pack(side=TOP)
        
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=BOTH, expand=True)

        self.canvas.create_window((4,4), window=self.frame_master, anchor="nw", 
                                  tags="self.frame_master")

        self.frameProbes.bind("<Configure>", self.onFrameConfigure)

##        logocanvas=Canvas(self.frame_right_column,width=250,height=250)
##        logocanvas.pack()
##
##        self.img=PhotoImage(file="images/reefberrypi_logo2.gif")
##        logocanvas.create_image(0,0,image=self.img, anchor=NW)

        #  add probe frames to show current data and mini graphs on the GUI
        self.readExistingProbes()
        # add the feed widget
        feedFrame = cls_FeedWidget.FeedWidget(self.frame_mid_column)
        # now add the outlets
        self.readOutlets()

        
        
        #self.checkProbeStatus()
        
##    def checkProbeStatus(self):
##        print("checkProbeStatus")
##        
##        
##        self.after(100, self.checkProbeStatus)
##
##    def printProbeStatus(ch, method, properties, body):
##        body = body.decode()
##        print(" [x] %r" % body)
        
    def onFrameConfigure(self, event):
        # used for the scrollbar
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def updateProbeVal(self, probeid, probeval):
        # update an individual probe value on the UI
        # find the matching probeid in the dictionary then update
        for p in self.probeDict:
            if self.probeDict[p].probeid.get()==probeid:
                self.probeDict[p].probeval.set(probeval)

    def updateOutletStatus(self, outletid, outletname, outletbus, control_type, button_state, outletstate, statusmsg):
        # update an individual outlet on the UI
        # find the matching outletid in the dictionary then update
        for o in self.outletDict:
            if self.outletDict[o].outletid.get()==outletid:
                #defs_common.logtoconsole("Updating status of " + str(o) +
                #                         " (" + str(self.outletDict[o].outletname.get()) + ")", fg="YELLOW", style="BRIGHT")

                self.outletDict[o].outletname.set(outletname)
                self.outletDict[o].outletbus.set(outletbus)
                self.outletDict[o].control_type.set(control_type)
                
                
                self.outletDict[o].outletstate.set(outletstate)
                self.outletDict[o].updateOutletFrameName

                if button_state == "OFF":
                    button_state = defs_common.OUTLET_OFF
                elif button_state == "ON":
                    button_state = defs_common.OUTLET_ON
                elif button_state == "AUTO":
                    button_state = defs_common.OUTLET_AUTO

                defs_common.logtoconsole("Freeze Update: " + str(self.outletDict[o].outlet_freezeupdate.get())) 
                if self.outletDict[o].outlet_freezeupdate.get() != True:
                    self.outletDict[o].statusmsg.set(statusmsg)
                    if statusmsg.find("ON") != -1:
                        self.outletDict[o].lbl_outlet_status.config(text=statusmsg, foreground="GREEN")
                        #defs_common.logtoconsole("Set %s status text to GREEN" % str(self.outletDict[o].outletname.get()), fg = "GREEN", style = "BRIGHT")
                    elif statusmsg.find("OFF") != -1:
                        self.outletDict[o].lbl_outlet_status.config(text=statusmsg, foreground="RED")
                        #defs_common.logtoconsole("Set status text to RED", fg = "RED", style = "BRIGHT")
    
                    if int(button_state) != int(self.outletDict[o].button_state.get()):      
                            if int(button_state) == int(defs_common.OUTLET_OFF):
                                self.outletDict[o].rdo_outlet_off.invoke()
                                self.outletDict[o].lbl_outlet_status.config(text="OFF", foreground="RED")
                            elif int(button_state) == int(defs_common.OUTLET_AUTO):
                                self.outletDict[o].rdo_outlet_auto.invoke()
                            elif int(button_state) == int(defs_common.OUTLET_ON):
                                self.outletDict[o].rdo_outlet_on.invoke()
                                self.outletDict[o].lbl_outlet_status.config(text="ON", foreground="GREEN")
                                
                else:
                    self.outletDict[o].outlet_freezeupdate.set(False)
                    defs_common.logtoconsole("Freeze Update: " + str(self.outletDict[o].outlet_freezeupdate.get()), fg="CYAN")
                    
##
##                self.outletDict[o].button_state.set(button_state)
##                self.outletDict[o].rdo_outlet_auto.invoke()
                
                
                
    def readExistingProbes(self):
        # get list of all probes from the server
        # request new data from server
        request = {
                      "rpc_req": "get_probelist",
                  }
        request = json.dumps(request)          
        probelist = self.rpc_call(request, "rpc_queue")
        probelist = probelist.decode()
        #print (probelist)
        probelist = json.loads(probelist)

        for probeitem in probelist["probelist"]:
            #print(probeitem)
            #print(probelist["probelist"][probeitem]["probename"])
            
            probe = cls_ProbeWidget.ProbeWidget(self.frameProbes)
            probe.probeid.set(str(probelist["probelist"][probeitem]["probeid"]))
            probe.name.set(probelist["probelist"][probeitem]["probename"])
            probe.updateProbeFrameName()
            probe.probetype.set(probelist["probelist"][probeitem]["probetype"])
            probe.animate_probe(self)
            self.probeDict [probe.probeid.get()] = probe
            #print("probe class id: " + probe.probeid.get())
            #print("probe class name: " + probe.name.get())
            #print("probe class type: " + probe.probetype.get()) 

    def readOutlets(self):
        
        # request new data from server
        request = {
                      "rpc_req": "get_outletlist",
                  }
        request = json.dumps(request)          
        #print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " " + request)
        outletlist = self.rpc_call(request, "rpc_queue")
        outletlist = outletlist.decode()
        print (outletlist)
        outletlist = json.loads(outletlist)
        
        #print (outletlist)

        for outletitem in outletlist["outletlist"]:
            #outlet = cls_OutletWidget.OutletWidget(self.frame_mid_column)
            if outletlist["outletlist"][outletitem]["outletbus"] == "int":
                outlet = cls_OutletWidget.OutletWidget(self.frame_mid_column)
            elif outletlist["outletlist"][outletitem]["outletbus"]== "ext":
                outlet = cls_OutletWidget.OutletWidget(self.frame_right_column)

            outlet.outletname.set(outletlist["outletlist"][outletitem]["outletname"])
            outlet.outletbus.set(outletlist["outletlist"][outletitem]["outletbus"])
            outlet.outletid.set(outletlist["outletlist"][outletitem]["outletid"])
            outlet.control_type.set(outletlist["outletlist"][outletitem]["control_type"])
            outlet.updateOutletFrameName()
            self.outletDict [outlet.outletid.get()] = outlet
            
            
                    
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
            self.connection.process_data_events()
        return self.response        
        
