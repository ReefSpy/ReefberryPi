import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common
from datetime import datetime

LARGE_FONT= ("Verdana", 12)

class FeedTimers(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        
        # registering validation command
        self.vldt_ifnum_cmd = (self.register(self.ValidateIfNum),'%s', '%S')
        
        label = tk.Label(self, text="Feed Timers", font=LARGE_FONT)
        label.grid(row=0, column=0, pady=10, sticky=W)

        # save button
        self.saveimg=PhotoImage(file="images/save-blue-24.png")
        self.btn_save = Button(self, text="Save", image=self.saveimg,
                               compound='left', relief=RAISED, command=self.saveChanges)
        self.btn_save.grid(row=1, column=0, sticky=W)

        ###########################################################################
        # frame for feed timers
        ###########################################################################
        self.frame_feed = LabelFrame(self, text="Feed Timers", relief= GROOVE)
        #self.frame_feed.pack(side=TOP, anchor=W)
        self.frame_feed.grid(row=2, column=0, pady=10, sticky=W)

        # timer A
        self.lbl_nameA = Label(self.frame_feed,text="Timer A:")
        self.lbl_nameA.grid(row=0, column=0, padx=10, pady=5)
        self.spn_A = Spinbox(self.frame_feed, from_=60,to=3600, increment=1,
                             validate='all', validatecommand=self.vldt_ifnum_cmd)
        self.spn_A.grid(row=0, column=1, padx=10, pady=5)
        
        # timer B
        self.lbl_nameB = Label(self.frame_feed,text="Timer B:")
        self.lbl_nameB.grid(row=1, column=0, padx=10, pady=5)
        self.spn_B = Spinbox(self.frame_feed, from_=60,to=3600, increment=1,
                             validate='all', validatecommand=self.vldt_ifnum_cmd)
        self.spn_B.grid(row=1, column=1, padx=10, pady=5)

        # timer C
        self.lbl_nameC = Label(self.frame_feed,text="Timer C:")
        self.lbl_nameC.grid(row=2, column=0, padx=10, pady=5)
        self.spn_C = Spinbox(self.frame_feed, from_=60,to=3600, increment=1,
                             validate='all', validatecommand=self.vldt_ifnum_cmd)
        self.spn_C.grid(row=2, column=1, padx=10, pady=5)

        # timer D
        self.lbl_nameD = Label(self.frame_feed,text="Timer D:")
        self.lbl_nameD.grid(row=3, column=0, padx=10, pady=5)
        self.spn_D = Spinbox(self.frame_feed, from_=60,to=3600, increment=1,
                             validate='all', validatecommand=self.vldt_ifnum_cmd)
        self.spn_D.grid(row=3, column=1, padx=10, pady=5)

        # read min and max values
        #self.minTime = cfg_common.readINIfile("feed_timers", "mintime", "60")
        #self.maxTime = cfg_common.readINIfile("feed_timers", "maxtime", "3600")
        self.minTime = self.downloadsettings("feed_timers", "mintime", "60")
        self.maxTime = self.downloadsettings("feed_timers", "maxtime", "3600")

        # description text
        self.lbl_desc = Label(self.frame_feed,text= "all time in seconds (" + self.minTime +
                              "-" + self.maxTime + ")")
        self.lbl_desc.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # read in saved settings
        self.spn_A.delete(0, END)
        #self.spn_A.insert(0, cfg_common.readINIfile("feed_timers", "feed_a", "60"))
        self.spn_A.insert(0, self.downloadsettings("feed_timers", "feed_a", "60"))
        self.spn_B.delete(0, END)
        #self.spn_B.insert(0, cfg_common.readINIfile("feed_timers", "feed_b", "60"))
        self.spn_B.insert(0, self.downloadsettings("feed_timers", "feed_b", "60"))
        self.spn_C.delete(0, END)
        #self.spn_C.insert(0, cfg_common.readINIfile("feed_timers", "feed_c", "60"))
        self.spn_C.insert(0, self.downloadsettings("feed_timers", "feed_c", "60"))
        self.spn_D.delete(0, END)
        #self.spn_D.insert(0, cfg_common.readINIfile("feed_timers", "feed_d", "60"))
        self.spn_D.insert(0, self.downloadsettings("feed_timers", "feed_d", "60"))

        
    def saveChanges(self):
        # Feed A
        val = self.ValidateMinMax(self.spn_A.get())
        self.spn_A.delete(0, END)
        self.spn_A.insert(0, val)
        #cfg_common.writeINIfile('feed_timers', 'feed_a', str(self.spn_A.get()))
        self.uploadsettings('feed_timers', 'feed_a', str(self.spn_A.get()))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + "Saved Feed A: " + val)

        # Feed B
        val = self.ValidateMinMax(self.spn_B.get())
        self.spn_B.delete(0, END)
        self.spn_B.insert(0, val)
        #cfg_common.writeINIfile('feed_timers', 'feed_b', str(self.spn_B.get()))
        self.uploadsettings('feed_timers', 'feed_b', str(self.spn_B.get()))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + "Saved Feed B: " + val)

        # Feed C
        val = self.ValidateMinMax(self.spn_C.get())
        self.spn_C.delete(0, END)
        self.spn_C.insert(0, val)
        #cfg_common.writeINIfile('feed_timers', 'feed_c', str(self.spn_C.get()))
        self.uploadsettings('feed_timers', 'feed_c', str(self.spn_C.get()))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + "Saved Feed C: " + val)

        # Feed D
        val = self.ValidateMinMax(self.spn_D.get())
        self.spn_D.delete(0, END)
        self.spn_D.insert(0, val)
        #cfg_common.writeINIfile('feed_timers', 'feed_d', str(self.spn_D.get()))
        self.uploadsettings('feed_timers', 'feed_d', str(self.spn_D.get()))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + "Saved Feed D: " + val)


    def ValidateIfNum(self, s, S):
        # disallow anything but numbers
        valid = S == '' or S.isdigit()
        if not valid:
            self.bell()
        return valid

    def ValidateMinMax(self, value):
        if value == "":
            return self.minTime
        elif int(value) < int(self.minTime):
            return self.minTime
        elif int(value) > int(self.maxTime):
            return self.maxTime
        else:
            return value

    def uploadsettings(self, section, key, value):
        # send the command back up to the controller to handle the request
        self.controller.controller.uploadsettings(section, key, value)

    def downloadsettings(self, section, key, defaultval):
        # send the command back up to the controller to handle the request
        val = self.controller.controller.downloadsettings(section, key, defaultval)
        return val
        


        
