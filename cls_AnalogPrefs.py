import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common
import cls_CalibPH

LARGE_FONT= ("Verdana", 12)

class PageAnalogProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        label = tk.Label(self, text="Analog Probes", font=LARGE_FONT)
        label.grid(row=0, column=0, sticky=W)

        # save button
        #self.saveimg=PhotoImage(file="images/save-blue-24.png")
        self.saveimg=PhotoImage(file="images/upload-to-cloud-24.png")
        self.btn_save = Button(self, text="Save", image=self.saveimg,
                               compound='left', relief=RAISED, command=self.saveChanges)
        self.btn_save.grid(row=1, column=0, sticky=W)


        # mcp3008 analog to digital converter
        self.adcframe = LabelFrame(self, text="MCP3008 10-bit Analog to Digital Converter", relief=GROOVE)
        self.adcframe.grid(row=2, column=0, pady=10, sticky=W)

        # create the channel widgets
        self.channelDict = {}
        for i in range(0,8):
            self.channelDict[i] = ChannelWidget(self.adcframe, self, i)

   

    def saveChanges(self):

        for i in range(0,8):
            self.channelDict[i].saveChanges()
        

class ChannelWidget(tk.Frame):

    def __init__(self, parent, controller, channelID):
        tk.Frame.__init__(self, parent)
        self.channelID = channelID
        self.controller = controller
        self.parent = parent

        # channel frame
        channelText = "Channel " + str(channelID)
        self.adcframe = LabelFrame(parent, relief=GROOVE, text=channelText)
        if channelID == 0 or channelID == 1:
            if channelID == 0:
                self.adcframe.grid(row=0, column=0, padx=10, pady=10)
            else:
                self.adcframe.grid(row=0, column=1, padx=10, pady=10)
        elif channelID == 2 or channelID == 3:
            if channelID == 2:
                self.adcframe.grid(row=1, column=0, padx=10, pady=10)
            else:
                self.adcframe.grid(row=1, column=1, padx=10, pady=10)
        elif channelID == 4 or channelID == 5:
            if channelID == 4:
                self.adcframe.grid(row=2, column=0, padx=10, pady=10)
            else:
                self.adcframe.grid(row=2, column=1, padx=10, pady=10)
        elif channelID == 6 or channelID == 7:
            if channelID == 6:
                self.adcframe.grid(row=3, column=0, padx=10, pady=10)
            else:
                self.adcframe.grid(row=3, column=1, padx=10, pady=10)
            

        # channel name
        self.lbl_name = Label(self.adcframe,text="Name:")
        self.lbl_name.grid(row=0, column=0, sticky=E)
        self.txt_name = Entry(self.adcframe)
        self.txt_name.grid(row=0, column=1, columnspan=2)

        # channel sensor type drown down list
        self.sensortype = StringVar()
        self.sensortypelist = ["pH","salinity","raw"]
        self.sensortype.set("pH") # default value
        self.lbl_sensortype = Label(self.adcframe,text="Sensor Type:")
        self.lbl_sensortype.grid(row=1, column=0, sticky=E)
        self.sensortypemenu = OptionMenu(self.adcframe,self.sensortype,*self.sensortypelist)
        self.sensortypemenu.configure(indicatoron=True, relief=GROOVE)
        self.sensortypemenu.grid(row=1, column=1)

        # channel calibrate button
        self.btn_calibrate = Button(self.adcframe, text="Calibrate", relief=RAISED, command=self.calibrateSensor)
        self.btn_calibrate.grid(row=1, column=2)

        # channel enable checkbox
        self.Enabled = IntVar()
        self.chk_enable = Checkbutton(self.adcframe,text="Enable",
                                         variable=self.Enabled, command=self.enableControls)
        self.chk_enable.grid(row=2, column=0, sticky=E)

        # get configuration from server
        self.getConfig(controller.controller, self.channelID)

        # enable/disable controls
        self.enableControls()

    def enableControls(self):
        # channel
        if self.Enabled.get() == True:
            self.lbl_name.config(state='normal')
            self.txt_name.config(state='normal')
            self.lbl_sensortype.config(state='normal')
            self.sensortypemenu.config(state='normal')
            self.btn_calibrate.config(state='normal')
        else:
            self.lbl_name.config(state='disabled')
            self.txt_name.config(state='disabled')
            self.lbl_sensortype.config(state='disabled')
            self.sensortypemenu.config(state='disabled')
            self.btn_calibrate.config(state='disabled')

    def calibrateSensor(self):
        if str(self.sensortype.get()) == "raw":
            tk.messagebox.showwarning("Calibration", "Calibration unavailable for sensor type 'raw' on channel " + str(self.channelID) )

        if str(self.sensortype.get()) == "salinity":
            tk.messagebox.showwarning("Calibration", "Calibration unavailable for sensor type 'salinity' on channel " + str(self.channelID) )

        if str(self.sensortype.get()) == "pH":
            #tk.messagebox.showinfo("Calibration", "Let's calibrate pH")
            strtitle = "pH Calibration: Channel " + str(self.channelID) + " [" + str(self.txt_name.get()) + "]"
            d = Dialog(self.parent, self, self.channelID, title = strtitle)
            d.CalibPH.running = False

    def getConfig(self, controller, channelID):
        # read values from config file
        # Channel name
        strval = "ch" + str(channelID) + "_name"
        val = controller.downloadsettings("mcp3008", strval, "Unnamed")
        self.txt_name.delete(0,END)
        self.txt_name.insert(0,val)
        # Channel enabled
        strval = "ch" + str(channelID) + "_enabled"
        val = controller.downloadsettings("mcp3008", strval, "False")
        if str(val) == "True":
            self.chk_enable.select()
        else:
            self.chk_enable.deselect()
        # Channel type
        strval = "ch" + str(channelID) + "_type"
        val = controller.downloadsettings("mcp3008", strval, "raw")
        self.sensortype.set(val)

    def saveChanges(self):
        # Channel
        if self.Enabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"

        strval = "ch" + str(self.channelID) + "_name"
        self.controller.controller.uploadsettings('mcp3008', strval, str(self.txt_name.get()))
        strval = "ch" + str(self.channelID) + "_enabled"
        self.controller.controller.uploadsettings('mcp3008', strval, str(chkstate))
        strval = "ch" + str(self.channelID) + "_type"
        self.controller.controller.uploadsettings('mcp3008', strval, str(self.sensortype.get()))

class Dialog(Toplevel):

    def __init__(self, parent, controller, channelnum, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.controller = controller

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        self.channelnum = channelnum

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
        self.CalibPH = cls_CalibPH.CalibPH(master, self, self.channelnum)
        self.CalibPH.pack()
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="Close", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        #w = Button(box, text="Cancel", width=10, command=self.cancel)
        #w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        #self.outlet.saveOutlet()

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

        
