from tkinter import *


##    outletwin = tk.Toplevel()
##    outletwin.transient()
##    outletwin.grab_set()

#Create the Tkinter application GUI
root = Tk()
root.wm_title("Reefberry Pi - Outlet Configurator")

def select_controltype(control):
    print("you selected coltrol type: " + control)
    try:
        root.frame_cfg.destroy()
        print("destroy")
    except:
        pass
    ###########################################################################
    # frame for outlet configuration
    ###########################################################################
    root.frame_cfg = LabelFrame(root, text="Configuration", relief= RAISED)
    root.frame_cfg.pack(fill=X, side=TOP)

    # dropdown list for fallback
    # drop down list for control type
    fallbackchoice = StringVar()
    fallbacklist = ["ON", "OFF"]
    fallbackchoice.set("ON") # default value
    root.lbl_fallback = Label(root.frame_cfg,text="Fallback:")
    root.lbl_fallback.pack(side=TOP, anchor=W)    
    root.fallbackmenu = OptionMenu(root.frame_cfg,fallbackchoice,*fallbacklist)
    root.fallbackmenu.pack(side=TOP, anchor=W)

    if control=="Heater":
        pass
    elif control=="Always":
        pass
        
    
def select_outlet(outlet):
    print ("you selected outlet: " + outletchoice.get())
    try:
        root.frame_outlet.destroy()
        root.frame_cfg.destroy()
        print("destroy")
    except:
        pass

    ###########################################################################
    # generic outlet info
    ###########################################################################

    # drop down list for control type
    controltypechoice = StringVar()
    controltypelist = ["Always", "Heater", "Light"]
    controltypechoice.set("Heater") # default value

    # outlet frame
    root.frame_outlet = LabelFrame(root, text="Outlet", relief= RAISED)
    root.frame_outlet.pack(fill=X, side=TOP)

    # outlet name
    root.lbl_outletname = Label(root.frame_outlet,text="Name:")
    root.lbl_outletname.pack(side=TOP, anchor=W)
    root.txt_outletname = Entry(root.frame_outlet)
    root.txt_outletname.pack(side=TOP, anchor=W)

    # control type
    root.lbl_controltype = Label(root.frame_outlet, text="Control Type:")
    root.lbl_controltype.pack(side=TOP, anchor=W)
    root.controltypemenu = OptionMenu(root.frame_outlet,controltypechoice,*controltypelist,
                            command=select_controltype)
    root.controltypemenu.pack(side=TOP, anchor=W)

    # logging
    root.lbl_log = Label(root.frame_outlet,text="Log:")
    root.lbl_log.pack(side=TOP, anchor=W)
    root.chk_log = Checkbutton(root.frame_outlet, text="Enable")
    root.chk_log.pack(side=TOP, anchor=W)
    
    ###########################################################################
    # frame for outlet configuration
    ###########################################################################
    root.frame_cfg = LabelFrame(root, text="Configuration", relief= RAISED)
    root.frame_cfg.pack(fill=X, side=TOP)

    # fallback
    #root.lbl_fallback = Label(root.frame_cfg,text="Fallback:")
    #root.lbl_fallback.pack(side=TOP, anchor=W)
    #root.txt_fallback = Entry(root.frame_cfg)
    #root.txt_fallback.pack(side=TOP, anchor=W)
    
    
# drop down list for outlets
outletchoice = StringVar()
outletlist = ["Outlet 1","Outlet 2","Outlet 3","Outlet 4"]
outletchoice.set("Outlet 1") # default value

outletmenu = OptionMenu(root,outletchoice,*outletlist,
                                   command=select_outlet)
outletmenu.pack(side=TOP, anchor=W)

select_outlet("Outlet 1")






root.mainloop()
