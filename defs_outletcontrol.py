from datetime import datetime, timedelta, time
from colorama import Fore, Back, Style
import defs_common
import RPi.GPIO as GPIO
import time




def handle_outlet_always(controller, outlet, button_state, pin):
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        #state = defs_common.readINIfile(outlet, "always_state", "OFF", logger=controller.logger)
        state = controller.AppPrefs.outletDict[outlet].always_state
        if state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif state == "ON":
            GPIO.output(pin, False)
            return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_heater(controller, outlet, button_state, pin):
    #global tempProbeDict
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        ################## To do:  if no probe selected should show something in status box....
        probe = defs_common.readINIfile(outlet, "heater_probe", "28-000000000000", logger=controller.logger)

        if controller.AppPrefs.temperaturescale == defs_common.SCALE_F:
            on_temp = defs_common.convertCtoF(controller.AppPrefs.outletDict[outlet].heater_on)
        else:
            on_temp = controller.AppPrefs.outletDict[outlet].heater_on
            
        if controller.AppPrefs.temperaturescale == defs_common.SCALE_F:
            off_temp = defs_common.convertCtoF(controller.AppPrefs.outletDict[outlet].heater_off)
        else:
            off_temp = controller.AppPrefs.outletDict[outlet].heater_off


        for p in controller.AppPrefs.tempProbeDict:
            if controller.AppPrefs.tempProbeDict[p].probeid == probe:
                #print("last temp " + str(controller.AppPrefs.tempProbeDict[p].lastTemperature) + " On temp " + on_temp + " Off temp " + off_temp)
                if float(controller.AppPrefs.tempProbeDict[p].lastTemperature) <= float(on_temp):
                    GPIO.output(pin, False)                
                    return "ON (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"  
                if float(controller.AppPrefs.tempProbeDict[p].lastTemperature) >= float(off_temp):
                    GPIO.output(pin, True)
                    return "OFF (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"
                break

    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_light(controller, outlet, button_state, pin):
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        #on_time = defs_common.readINIfile(outlet, "light_on", "08:00", logger=controller.logger)
        #off_time = defs_common.readINIfile(outlet, "light_off", "17:00", logger=controller.logger)
        on_time = controller.AppPrefs.outletDict[outlet].light_on
        off_time = controller.AppPrefs.outletDict[outlet].light_off
        now = datetime.now()
        now_time = now.time()
        on_time = datetime.strptime(on_time, '%H:%M')
        off_time = datetime.strptime(off_time, '%H:%M')
        # on time before off time
        if datetime.time(on_time) < datetime.time(off_time):
            if now_time >= datetime.time(on_time) and now_time <= datetime.time(off_time):
                GPIO.output(pin, False) #turn on light
                status = "ON" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
            else:
                GPIO.output(pin, True) #turn on light
                status = "OFF" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
        else: # on time after off time
            if now_time <= datetime.time(on_time) and now_time >= datetime.time(off_time):
                GPIO.output(pin, True) #turn off light
                status = "OFF" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
            else:
                GPIO.output(pin, False) #turn on light
                status = "ON" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_returnpump (controller, outlet, button_state, pin):  
    #global feed_PreviousMode
    if controller.AppPrefs.feed_PreviousMode == "A":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_a", "0")
        controller.AppPrefs.feed_ExtraTimeAdded =  controller.AppPrefs.outletDict[outlet].return_feed_delay_a
    elif controller.AppPrefs.feed_PreviousMode == "B":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_b", "0")
        controller.AppPrefs.feed_ExtraTimeAdded =  controller.AppPrefs.outletDict[outlet].return_feed_delay_b
    elif controller.AppPrefs.feed_PreviousMode == "C":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_c", "0")
        controller.AppPrefs.feed_ExtraTimeAdded =  controller.AppPrefs.outletDict[outlet].return_feed_delay_c
    elif controller.AppPrefs.feed_PreviousMode == "D":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_d", "0")
        controller.AppPrefs.feed_ExtraTimeAdded =  controller.AppPrefs.outletDict[outlet].return_feed_delay_d
    else:
        controller.AppPrefs.feed_ExtraTimeAdded = 0
        
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        if controller.AppPrefs.feed_CurrentMode == "A":
            #return_enable_feed_a = defs_common.readINIfile(outlet, "return_enable_feed_a", "False")
            return_enable_feed_a = controller.AppPrefs.outletDict[outlet].return_enable_feed_a
            controller.AppPrefs.feed_PreviousMode = "A"
            if return_enable_feed_a == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_a == "False":
                GPIO.output(pin, False)
                return "ON"
        elif controller.AppPrefs.feed_CurrentMode == "B":
            #return_enable_feed_b = defs_common.readINIfile(outlet, "return_enable_feed_b", "False")
            return_enable_feed_b = controller.AppPrefs.outletDict[outlet].return_enable_feed_b
            controller.AppPrefs.feed_PreviousMode = "B"
            if return_enable_feed_b == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_b == "False":
                GPIO.output(pin, False)
                return "ON"
        elif controller.AppPrefs.feed_CurrentMode == "C":
            #return_enable_feed_c = defs_common.readINIfile(outlet, "return_enable_feed_c", "False")
            return_enable_feed_c = controller.AppPrefs.outletDict[outlet].return_enable_feed_c
            controller.AppPrefs.feed_PreviousMode = "C"
            if return_enable_feed_c == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_c == "False":
                GPIO.output(pin, False)
                return "ON"
        elif controller.AppPrefs.feed_CurrentMode == "D":
            #return_enable_feed_d = defs_common.readINIfile(outlet, "return_enable_feed_d", "False")
            return_enable_feed_d = controller.AppPrefs.outletDict[outlet].return_enable_feed_d
            controller.AppPrefs.feed_PreviousMode = "D"
            if return_enable_feed_d == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_d == "False":
                GPIO.output(pin, False)
                return "ON"
        else:
            difference = round(((int(controller.AppPrefs.feed_ExtraTimeSeed) + (int(controller.AppPrefs.feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
            
            if int(round(time.time())*1000) <= int(controller.AppPrefs.feed_ExtraTimeSeed) + (int(controller.AppPrefs.feed_ExtraTimeAdded)*1000):
                #print("Extra feed time remaining: " + str(difference) + "s")
                print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Delay Mode: " + outlet + " (" + str(controller.AppPrefs.feed_ExtraTimeAdded) + "s) " + " Delay Time Remaining: " + str(round(difference)) + "s"
                   + Style.RESET_ALL)
                GPIO.output(pin, True)
                return "OFF (delay)"
            else:
                GPIO.output(pin, False)
                return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_skimmer (controller, outlet, button_state, pin):  
    if controller.AppPrefs.feed_PreviousMode == "A":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_a", "0")
        controller.AppPrefs.feed_ExtraTimeAdded = controller.AppPrefs.outletDict[outlet].skimmer_feed_delay_a
    elif controller.AppPrefs.feed_PreviousMode == "B":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_b", "0")
        controller.AppPrefs.feed_ExtraTimeAdded = controller.AppPrefs.outletDict[outlet].skimmer_feed_delay_b
    elif controller.AppPrefs.feed_PreviousMode == "C":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_c", "0")
        controller.AppPrefs.feed_ExtraTimeAdded = controller.AppPrefs.outletDict[outlet].skimmer_feed_delay_c
    elif controller.AppPrefs.feed_PreviousMode == "D":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_d", "0")
        controller.AppPrefs.feed_ExtraTimeAdded = controller.AppPrefs.outletDict[outlet].skimmer_feed_delay_d
    else:
        controller.AppPrefs.feed_ExtraTimeAdded = 0

    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        if controller.AppPrefs.feed_CurrentMode == "A":
            #skimmer_enable_feed_a = defs_common.readINIfile(outlet, "skimmer_enable_feed_a", "False")
            skimmer_enable_feed_a = controller.AppPrefs.outletDict[outlet].skimmer_enable_feed_a
            controller.AppPrefs.feed_PreviousMode = "A"
            if skimmer_enable_feed_a == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_a == "False":
                GPIO.output(pin, False)
                return "ON"
        elif controller.AppPrefs.feed_CurrentMode == "B":
            #skimmer_enable_feed_b = defs_common.readINIfile(outlet, "skimmer_enable_feed_b", "False")
            skimmer_enable_feed_b = controller.AppPrefs.outletDict[outlet].skimmer_enable_feed_b
            controller.AppPrefs.feed_PreviousMode = "B"
            if skimmer_enable_feed_b == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_b == "False":
                GPIO.output(pin, False)
                return "ON"
        elif controller.AppPrefs.feed_CurrentMode == "C":
            #skimmer_enable_feed_c = defs_common.readINIfile(outlet, "skimmer_enable_feed_c", "False")
            skimmer_enable_feed_c = controller.AppPrefs.outletDict[outlet].skimmer_enable_feed_c
            controller.AppPrefs.feed_PreviousMode = "C"
            if skimmer_enable_feed_c == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_c == "False":
                GPIO.output(pin, False)
                return "ON"
        elif controller.AppPrefs.feed_CurrentMode == "D":
            #skimmer_enable_feed_d = defs_common.readINIfile(outlet, "skimmer_enable_feed_d", "False")
            skimmer_enable_feed_d = controller.AppPrefs.outletDict[outlet].skimmer_enable_feed_d
            controller.AppPrefs.feed_PreviousMode = "D"
            if skimmer_enable_feed_d == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_d == "False":
                GPIO.output(pin, False)
                return "ON"
        else:
            difference = round(((int(controller.AppPrefs.feed_ExtraTimeSeed) + (int(controller.AppPrefs.feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
            if int(round(time.time())*1000) <= int(controller.AppPrefs.feed_ExtraTimeSeed) + (int(controller.AppPrefs.feed_ExtraTimeAdded)*1000):
                #print("Extra feed time remaining: " + str(difference) + "s")
                print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Delay Mode: " + outlet + " (" + str(controller.AppPrefs.feed_ExtraTimeAdded) + "s) " + " Delay Time Remaining: " + str(round(difference)) + "s"
                   + Style.RESET_ALL)
                GPIO.output(pin, True)
                return "OFF (delay)"
            else:
                GPIO.output(pin, False)
                return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"
