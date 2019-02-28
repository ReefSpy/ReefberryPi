import tkinter as tk
from tkinter import *
from tkinter import ttk
#import glob
#import cfg_common
#import configparser
from datetime import datetime
import defs_common
import json

LARGE_FONT= ("Verdana", 12)

class PageTempProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        # create dictionary to hold assigned probes
        # these are probes that are already saved in config file
        self.probeDict = {}
        # and these are the new unsaved probes
        self.newprobeDict = {}

        label = tk.Label(self, text="Temperature Probes", font=LARGE_FONT)
        label.pack(side=TOP, anchor=W)

        # top frame for toolbar
        #self.frame_toolbar = LabelFrame(self, relief= FLAT)
        #self.frame_toolbar.pack(fill=X, side=TOP)
        # save button
        #self.saveimg=PhotoImage(file="images/save-blue-24.png")
        #self.btn_save = Button(self.frame_toolbar, text="Save", image=self.saveimg,
        #                       compound='left', relief=RAISED, command=self.saveChanges)
        #self.btn_save.pack(side=TOP, anchor=W, pady=5)

        #hold these icons for later use
        self.editimg=PhotoImage(file="images/edit-24.png")
        self.deleteimg=PhotoImage(file="images/trash-can-24.png")

        ###########################################################################
        # frame temperature probes
        ###########################################################################
        self.frame_DS18B20 = LabelFrame(self, text="DS18B20 Temperature Probes", relief= RAISED)
        self.frame_DS18B20.pack(fill=X, side=TOP)

        # probe
        self.unassignedprobeframe = LabelFrame(self.frame_DS18B20, relief=GROOVE, text="Unnassigned Probes:")
        self.unassignedprobeframe.pack(side=LEFT, anchor=N, padx=10)
        #self.lbl_probe = Label(self.unassignedprobeframe,text="Unassigned Probes:")
        #self.lbl_probe.pack(side=TOP, anchor=W, padx=10)
        self.assignedprobeframe = LabelFrame(self.frame_DS18B20, relief=GROOVE, text="Assigned Probes:")
        self.assignedprobeframe.pack(side=LEFT, anchor=N, padx=10)

        # listbox to display connected probes
        self.lst_probes = Listbox(self.unassignedprobeframe,  height=5)
        self.lst_probes.pack(side=TOP, anchor=W, padx=10)

        # button to assign probe
        #self.btn_assignprobe = Button(self.unassignedprobeframe,text="Assign Probe",
        #                           command=self.assignProbe)
        #self.btn_assignprobe.pack(side=TOP, anchor=W, padx=10, pady=10)

        # add probe button
        self.btn_assignprobe = Button(self.unassignedprobeframe,text="Add Probe",
                                   command=self.addProbe)
        self.btn_assignprobe.pack(side=TOP, anchor=W, fill=X, pady=10)
        
        self.getConnectedProbes()
        self.readExistingProbes()
        for i in self.probeDict:
            print("Probe dict id: " + str(self.probeDict[i].probeid))
            print("Probe dict name: " + str(self.probeDict[i].probeid))
            self.createProbeFrame(str(self.probeDict[i].probeid), str(self.probeDict[i].name))
        

    def addProbe(self):
        d = NewProbeDialog(self, self.lst_probes.get(ACTIVE), "Unnamed")
        

    def getConnectedProbes(self):

        self.readExistingProbes()
        #base_dir = '/sys/bus/w1/devices/' 
        #device_folder = glob.glob(base_dir + '28*')

        defs_common.logtoconsole("Request list of connected temperature probes...")
        # get setting value from server
        request = {
                  "rpc_req": "get_connectedtempprobes",
                  }
        request = json.dumps(request)          
        connectedtempprobes = self.controller.rpc_call(request, "rpc_queue")
        connectedtempprobes = connectedtempprobes.decode()
        connectedtempprobes = json.loads(connectedtempprobes)

        #print (connectedtempprobes)   

        # we need to clear widget so we can refresh with current list
        # first grab current selection to it is still highlited after refresh
        selection = self.lst_probes.curselection()
        self.lst_probes.delete(0, END)
        addtolist = True
        newprobeID = ""
        for d in connectedtempprobes['tempprobelist']:
            newprobeid = d.split("/")[-1]
            for p in self.probeDict:
                if str(d.split("/")[-1]) == str(self.probeDict[p].probeid):
                    addtolist = False
                    break
                else:
                    addtolist = True
            if addtolist == True:
                self.lst_probes.insert(END, newprobeid)

        # set back to what was slected
        try:
            self.lst_probes.activate(selection)
            self.lst_probes.selection_set(selection)
        except:
            #print("Error selecting listbox index")
            pass


        # diable the add probe button if nothing left in the list
        if self.lst_probes.size() == 0:
            self.btn_assignprobe["state"] = DISABLED
        else:
            self.btn_assignprobe["state"] = NORMAL
            
        #self.after(2000,self.getConnectedProbes)


    def createProbeFrame(self, probeid, name):
        # probe frame
        self.probeframe = LabelFrame(self.assignedprobeframe, relief= FLAT)
        self.probeframe.pack(fill=X, side=TOP, pady=10)
        lbl_probeSNl = Label(self.probeframe,text="Probe ID:")
        lbl_probeSNl.grid(sticky=W, row=0, column=0)
        lbl_probeSN = Label(self.probeframe,text=probeid)
        lbl_probeSN.grid(padx=10, sticky=W, row=0, column=1)
        lbl_probenamel = Label(self.probeframe,text="Name:")
        lbl_probenamel.grid(sticky=W, row=1, column=0)
        lbl_probename = Label(self.probeframe, text=name)
        lbl_probename.grid(padx=10, sticky=W, row=1, column=1)

        btn_edit = Button(self.probeframe, image=self.editimg,
                          compound='left', relief=FLAT,
                          command=lambda:self.editProbe(lbl_probeSN, lbl_probename))
        btn_edit.grid (row=0, column=2, rowspan=2, padx=5)
        
        btn_delete = Button(self.probeframe,image=self.deleteimg,
                            compound='left', relief=FLAT,
                            command=lambda:self.deleteProbe(lbl_probeSN, lbl_probename))
        btn_delete.grid (row=0, column=3, rowspan=2, padx=5)
        self.probeframe.grid_columnconfigure(1, minsize=200)

    def editProbe(self, ID, name):
        #print(ID['text'])
        #print(name["text"])
        self.readExistingProbes()
        d = NewProbeDialog(self, ID['text'], name["text"])
        # we need to refresh the page, clear out old probes and populate current data
        for widget in self.assignedprobeframe.winfo_children():
            widget.destroy()
        #self.readExistingProbes()
        for i in self.probeDict:
            #print("Probe dict id: " + str(self.probeDict[i].probeid))
            #print("Probe dict name: " + str(self.probeDict[i].probeid))
            self.createProbeFrame(str(self.probeDict[i].probeid), str(self.probeDict[i].name))
        
    def deleteProbe(self, ID, name):
        if messagebox.askokcancel("Delete Probe", "Are you sure want to delete probe?\n\nProbe ID: " + str(ID["text"]) +
                                  "\nName: " + str(name["text"])):
            cfg_common.removesectionfromINIfile(str("ds18b20_" + ID["text"]))
            # we need to refresh the page, clear out old probes and populate current data
            for widget in self.assignedprobeframe.winfo_children():
                widget.destroy()
            self.readExistingProbes()
            for i in self.probeDict:
                self.createProbeFrame(str(self.probeDict[i].probeid), str(self.probeDict[i].name))
            self.getConnectedProbes()
            
    def saveChanges(self):
        #print("Enter saveChanges")
        #print(self.newprobeDict)
        try:
            for probe in self.newprobeDict:
                self.controller.uploadsettings('ds18b20_' + self.newprobeDict[probe].probeid, "name", "1")
                del self.newprobeDict[probe]
##                if cfg_common.writeINIfile('ds18b20_' + self.newprobeDict[probe].probeid, "name", "1"):
##                    messagebox.showinfo("Global Settings",
##                                    "New configuration saved succesfully.")
##                    # remove this key from unsaved probe list
##                    del self.newprobeDict[probe]
##                else:
##                    messagebox.showerror("Global Settings",
##                                     "Error: Could not save changes! \nNew configuration not saved.")
            

        except:
            print("saveChanges Error")
            #pass

           

    def readExistingProbes(self):
        # create dictionary to hold assigned temperature probes
        # these are probes that are already saved in config file
        self.probeDict = {}
        self.probeDict.clear()

        # send the command back up to the controller to handle the request
        defs_common.logtoconsole("Request probe list for outlet control")
        # get setting value from server
        request = {
                  "rpc_req": "get_probelist",
              }
        request = json.dumps(request)          
        probelist = self.controller.rpc_call(request, "rpc_queue")
        probelist = probelist.decode()
        probelist = json.loads(probelist)

        
        for tempprobe in probelist['probelist']:
            if tempprobe.split("_")[0] == "ds18b20":
                probe = ProbeClass()
                probe.probeid = probelist['probelist'][tempprobe]['probeid'].split("_")[1]
                probe.name = probelist['probelist'][tempprobe]['probename']
                self.probeDict [probe.probeid] = probe




        

class ProbeClass():
    name = ""
    probeid = ""
       
class NewProbeDialog():

    def __init__(self, parent, sn, name):
        self.dlg = self.top = Toplevel(parent)
        self.dlg.focus_set()
        self.dlg.wm_title("Add Probe")
        self.dlg.resizable(0,0) # remove max button from dialog window and make unsizable
        
        # probe id
        self.lbl_id = Label(self.dlg, text="Probe ID:")
        self.lbl_id.grid(sticky=E, row=0, column=0)
        #self.lbl_probeid = Label(self.dlg, text=parent.lst_probes.get(ACTIVE))
        self.lbl_probeid = Label(self.dlg, text=sn)
        self.lbl_probeid.grid(sticky=W, row=0, column=1)

        # text entry for Probe Name
        self.lbl_name = Label(self.dlg, text="Name:")
        self.lbl_name.grid(sticky=E, row=1, column=0)
        self.txt_probename = Entry(self.dlg)
        self.txt_probename.grid(sticky=W, row=1, column=1, columnspan=2)
        self.txt_probename.delete(0,END)
        self.txt_probename.insert(0,name)

        # buttons
        btn_cancel = Button(self.dlg, text="Cancel", command=self.cancel)
        btn_cancel.grid(sticky=E, row=3, column=1)
        btn_save = Button(self.dlg, text="Save", command=lambda:self.save(parent))
        btn_save.grid(sticky=E, row=3, column=2)

        # make this a modal dialog
        self.dlg.grab_set()
        self.dlg.transient(parent)
        self.dlg.wait_window(self.dlg)
        parent.getConnectedProbes()
        parent.readExistingProbes()

    def save(self, parent):
        parent.controller.uploadsettings('ds18b20_' + self.lbl_probeid["text"],
                                   "name", self.txt_probename.get())
        parent.createProbeFrame(str(self.lbl_probeid["text"]), str(self.txt_probename.get()))
        try:
            parent.lst_probes.delete(parent.lst_probes.curselection())

            # diable the add probe button if nothing left in the list
            if parent.lst_probes.size() == 0:
                parent.btn_assignprobe["state"] = DISABLED
            else:
                parent.btn_assignprobe["state"] = NORMAL
        except:
            pass
        
        self.dlg.destroy()

    def cancel(self):
        self.dlg.destroy()
