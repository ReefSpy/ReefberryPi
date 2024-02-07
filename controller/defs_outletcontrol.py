from datetime import datetime, timedelta, time
import defs_common
import RPi.GPIO as GPIO
import time
import defs_Influx

PIN_ON = False
PIN_OFF = True


def get_on_or_off(pin):
    currentOutletState = GPIO.input(pin)
    if currentOutletState == PIN_ON:
        return "ON"
    elif currentOutletState == PIN_OFF:
        return "OFF"
    else:
        return "UNKNOWN"


def handle_on_off(AppPrefs, outlet, pin, targetstate):

    currentOutletState = GPIO.input(pin)
    #currentOutletState = PIN_ON

    # log any change
    if AppPrefs.outletDict[outlet].enable_log.lower() == "true":
        if currentOutletState != targetstate:
            #defs_common.logtoconsole("I need to log this! " + outlet, fg="YELLOW", bg="BLUE", style="BRIGHT")
            # lets record 1 or 0 in the log
            if currentOutletState == PIN_ON:
                curval = 1
            else:
                curval = 0
            #defs_common.logprobedata(outlet + "_", val)
            # lets record 1 or 0 in the log
            if targetstate == PIN_ON:
                tarval = 1
            else:
                tarval = 0
            # defs_common.logprobedata(outlet + "_", val)
            # defs_common.logtoconsole("***Logged*** Outlet Change " + "[" + outlet + "] " + str(
            #     controller.AppPrefs.outletDict[outlet].outletname) + " = " + str(val), fg="CYAN", style="BRIGHT")
            # controller.logger.info("***Logged*** Outlet Change " + "[" + outlet + "] " + str(
            #     controller.AppPrefs.outletDict[outlet].outletname) + " = " + str(val))
            AppPrefs.Influx_write_api.write(defs_Influx.INFLUXDB_OUTLET_BUCKET_3MO, AppPrefs.influxdb_org, [{"measurement": "outlet_state", "tags": {
                    "appuid": AppPrefs.appuid, "outletid": outlet}, "fields": {"value": curval}, "time": datetime.utcnow()}])
            AppPrefs.Influx_write_api.write(defs_Influx.INFLUXDB_OUTLET_BUCKET_3MO, AppPrefs.influxdb_org, [{"measurement": "outlet_state", "tags": {
                     "appuid": AppPrefs.appuid, "outletid": outlet}, "fields": {"value": tarval}, "time": datetime.utcnow()}])
            AppPrefs.logger.info("***Logged*** Outlet Change " + "[" + outlet + "] " + str(
                 AppPrefs.outletDict[outlet].outletname) + " | Target: " + str(tarval) + " Previous: " + str(curval))

    if targetstate == PIN_ON:
        GPIO.output(pin, False)
        return
    elif targetstate == PIN_OFF:
        GPIO.output(pin, True)
        return


def handle_outlet_always(AppPrefs, outlet, button_state, pin):
    butstate = ""
    if button_state == "OFF":
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        #return "OFF"
        butstate = "OFF"
    elif button_state == "ON":
        #GPIO.output(pin, False)
        handle_on_off(AppPrefs, outlet, pin, PIN_ON)
        #return "ON"
        butstate = "ON"
    elif button_state == "AUTO":
        #state = defs_common.readINIfile(outlet, "always_state", "OFF", logger=controller.logger)
        state = AppPrefs.outletDict[outlet].always_state
        if state == "OFF":
            #GPIO.output(pin, True)
            handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
            #return "OFF"
            butstate = "OFF"
        elif state == "ON":
            #GPIO.output(pin, False)
            handle_on_off(AppPrefs, outlet, pin, PIN_ON)
            #return "ON"
            butstate = "ON"
    else:
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        #return "OFF"
        butstate = "OFF"

   # AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] "  + AppPrefs.outletDict[outlet].outletname + " = " + butstate)
    AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin)
    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                " | Mode: " + AppPrefs.outletDict[outlet].button_state + \
                                " | Status: " + get_on_or_off(pin))       

def handle_outlet_heater(AppPrefs, outlet, button_state, pin):

    #global tempProbeDict
    if button_state == "OFF":
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        #return "OFF"
        AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin)
        AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                " | Mode: OFF" + \
                                " | Status: " + get_on_or_off(pin) )
    elif button_state == "ON":
        #GPIO.output(pin, False)
        handle_on_off(AppPrefs, outlet, pin, PIN_ON)
        #return "ON""
        AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin)
        AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                " | Mode: ON" + \
                                " | Status: " + get_on_or_off(pin) )                        
    elif button_state == "AUTO":
        
        probe = AppPrefs.outletDict[outlet].heater_probe

        if AppPrefs.temperaturescale == defs_common.SCALE_F:
            on_temp = defs_common.convertCtoF(
                AppPrefs.outletDict[outlet].heater_on)
        else:
            on_temp = AppPrefs.outletDict[outlet].heater_on

        if AppPrefs.temperaturescale == defs_common.SCALE_F:
            off_temp = defs_common.convertCtoF(
                AppPrefs.outletDict[outlet].heater_off)
        else:
            off_temp = AppPrefs.outletDict[outlet].heater_off

        for p in AppPrefs.tempProbeDict:
            if AppPrefs.tempProbeDict[p].probeid == probe:
                #print("last temp " + str(controller.AppPrefs.tempProbeDict[p].lastTemperature) + " On temp " + on_temp + " Off temp " + off_temp)
                if float(AppPrefs.tempProbeDict[p].lastTemperature) <= float(on_temp):
                    #GPIO.output(pin, False)
                    handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                    #AppPrefs.logger.debug(AppPrefs.outletDict[outlet].outletname +  " ON (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ") " + AppPrefs.tempProbeDict[p].lastTemperature)
                    AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin) + " (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"
                    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                          "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                          " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                          " | Mode: AUTO | Outlet: ON" + \
                                          " | Range: (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")" + \
                                          " | Current: " + AppPrefs.tempProbeDict[p].lastTemperature +\
                                          " | Status: " + get_on_or_off(pin))
                elif float(AppPrefs.tempProbeDict[p].lastTemperature) >= float(off_temp):
                    #GPIO.output(pin, True)
                    handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                    #AppPrefs.logger.debug(AppPrefs.outletDict[outlet].outletname +  " OFF (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ") " + AppPrefs.tempProbeDict[p].lastTemperature)
                    AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin) + " (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"
                    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                          "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                          " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                          " | Mode: AUTO | Outlet: OFF" + \
                                          " | Range: (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")" + \
                                          " | Current: " + AppPrefs.tempProbeDict[p].lastTemperature + \
                                          " | Status: " + get_on_or_off(pin))
                else:
                    state = get_on_or_off(pin)
                    #AppPrefs.logger.debug( state + " (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")")
                    AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin) + " (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"
                    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                          "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                          " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                          " | Mode: AUTO | Outlet: OFF" + \
                                          " | Range: (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")" + \
                                          " | Current: " + AppPrefs.tempProbeDict[p].lastTemperature + \
                                          " | Status: " + get_on_or_off(pin))
                
 
                break

    else:
        GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        #return "OFF"


   


# def handle_outlet_ph(controller, outlet, button_state, pin):

#     if button_state == "OFF":
#         handle_on_off(controller, outlet, pin, PIN_OFF)
#         return "OFF"
#     elif button_state == "ON":
#         handle_on_off(controller, outlet, pin, PIN_ON)
#         return "ON"
#     elif button_state == "AUTO":
#         probe = controller.AppPrefs.outletDict[outlet].ph_probe
#         ph_high = controller.AppPrefs.outletDict[outlet].ph_high
#         ph_low = controller.AppPrefs.outletDict[outlet].ph_low
#         ph_onwhen = controller.AppPrefs.outletDict[outlet].ph_onwhen

#         # print(probe)
#         # print(probe[-1:])
#         for p in controller.AppPrefs.mcp3008Dict:
#            # print(controller.AppPrefs.mcp3008Dict[p].ch_num)
#             if str(controller.AppPrefs.mcp3008Dict[p].ch_num) == str(controller.AppPrefs.outletDict[outlet].ph_probe[-1:]):
#                # print("I found the probe: " +  str(controller.AppPrefs.mcp3008Dict[p].ch_num))
#                # print("last ph " + str(controller.AppPrefs.mcp3008Dict[p].lastValue) + " PH High " + ph_high + " PH Low " + ph_low + " On when " + ph_onwhen)
#                 if controller.AppPrefs.mcp3008Dict[p].lastValue == "":
#                     controller.AppPrefs.mcp3008Dict[p].lastValue = 0
#                 if ph_onwhen == "HIGH":
#                     if float(controller.AppPrefs.mcp3008Dict[p].lastValue) >= float(ph_high):
#                         handle_on_off(controller, outlet, pin, PIN_ON)
#                         return "ON (" + str("%.1f" % float(ph_low)) + " - " + str("%.1f" % float(ph_high)) + ")"
#                     elif float(controller.AppPrefs.mcp3008Dict[p].lastValue) <= float(ph_low):
#                         handle_on_off(controller, outlet, pin, PIN_OFF)
#                         return "OFF (" + str("%.1f" % float(ph_low)) + " - " + str("%.1f" % float(ph_high)) + ")"
#                     else:
#                         state = get_on_or_off(pin)
#                         return state + " (" + str("%.1f" % float(ph_low)) + " - " + str("%.1f" % float(ph_high)) + ")"

#                 elif ph_onwhen == "LOW":
#                     if float(controller.AppPrefs.mcp3008Dict[p].lastValue) >= float(ph_high):
#                         handle_on_off(controller, outlet, pin, PIN_OFF)
#                         return "OFF (" + str("%.1f" % float(ph_low)) + " - " + str("%.1f" % float(ph_high)) + ")"
#                     elif float(controller.AppPrefs.mcp3008Dict[p].lastValue) <= float(ph_low):
#                         handle_on_off(controller, outlet, pin, PIN_ON)
#                         return "ON (" + str("%.1f" % float(ph_low)) + " - " + str("%.1f" % float(ph_high)) + ")"
#                     else:
#                         state = get_on_or_off(pin)
#                         return state + " (" + str("%.1f" % float(ph_low)) + " - " + str("%.1f" % float(ph_high)) + ")"
#                 break

#     else:
#         #GPIO.output(pin, True)
#         handle_on_off(controller, outlet, pin, PIN_OFF)
#         return "OFF"


def handle_outlet_light(AppPrefs, outlet, button_state, pin):
    if button_state == "OFF":
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        #return "OFF"
        status = "OFF"
    elif button_state == "ON":
        #GPIO.output(pin, False)
        handle_on_off(AppPrefs, outlet, pin, PIN_ON)
        #return "ON"
        status = "ON"
    elif button_state == "AUTO":
        #on_time = defs_common.readINIfile(outlet, "light_on", "08:00", logger=controller.logger)
        #off_time = defs_common.readINIfile(outlet, "light_off", "17:00", logger=controller.logger)
        on_time = AppPrefs.outletDict[outlet].light_on
        off_time = AppPrefs.outletDict[outlet].light_off
        now = datetime.now()
        now_time = now.time()
        on_time = datetime.strptime(on_time, '%H:%M')
        off_time = datetime.strptime(off_time, '%H:%M')
        # on time before off time
        if datetime.time(on_time) < datetime.time(off_time):
            if now_time >= datetime.time(on_time) and now_time <= datetime.time(off_time):
               # GPIO.output(pin, False) #turn on light
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                status = "ON" + " (" + str(datetime.strftime(on_time, '%H:%M')) + \
                    " - " + str(datetime.strftime(off_time, '%H:%M')) + ")"
                #return status
            else:
               # GPIO.output(pin, True) #turn off light
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                status = "OFF" + " (" + str(datetime.strftime(on_time, '%H:%M')) + \
                    " - " + str(datetime.strftime(off_time, '%H:%M')) + ")"
                #return status
        else:  # on time after off time
            if now_time <= datetime.time(on_time) and now_time >= datetime.time(off_time):
               # GPIO.output(pin, True) #turn off light
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                status = "OFF" + " (" + str(datetime.strftime(on_time, '%H:%M')) + \
                    " - " + str(datetime.strftime(off_time, '%H:%M')) + ")"
                #return status
            else:
              #  GPIO.output(pin, False) #turn on light
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                status = "ON" + " (" + str(datetime.strftime(on_time, '%H:%M')) + \
                    " - " + str(datetime.strftime(off_time, '%H:%M')) + ")"
                #return status
    else:
       # GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        #return "OFF"
    # AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin) + " (" + str(datetime.strftime(on_time, '%H:%M')) + \
    #                 " - " + str(datetime.strftime(off_time, '%H:%M')) + ")"
    
    AppPrefs.outletDict[outlet].outletstatus = status

    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                          "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                          " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                          " | Mode: " + AppPrefs.outletDict[outlet].button_state + \
                                          " | Status: " + status  )


def handle_outlet_returnpump(AppPrefs, outlet, button_state, pin):
    #global feed_PreviousMode
    
    if AppPrefs.feed_PreviousMode == "A":
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].return_feed_delay_a
    elif AppPrefs.feed_PreviousMode == "B":
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].return_feed_delay_b
    elif AppPrefs.feed_PreviousMode == "C":
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].return_feed_delay_c
    elif AppPrefs.feed_PreviousMode == "D":
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].return_feed_delay_d
    else:
        AppPrefs.feed_ExtraTimeAdded = 0

    if button_state == "OFF":
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        # return "OFF"
    elif button_state == "ON":
        #GPIO.output(pin, False)
        handle_on_off(AppPrefs, outlet, pin, PIN_ON)
        # return "ON"
    elif button_state == "AUTO":
        if AppPrefs.feed_CurrentMode == "A":
            return_enable_feed_a = AppPrefs.outletDict[outlet].return_enable_feed_a
            AppPrefs.feed_PreviousMode = "A"
            if return_enable_feed_a == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif return_enable_feed_a == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        elif AppPrefs.feed_CurrentMode == "B":
            return_enable_feed_b = AppPrefs.outletDict[outlet].return_enable_feed_b
            AppPrefs.feed_PreviousMode = "B"
            if return_enable_feed_b == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif return_enable_feed_b == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        elif AppPrefs.feed_CurrentMode == "C":
            return_enable_feed_c = AppPrefs.outletDict[outlet].return_enable_feed_c
            AppPrefs.feed_PreviousMode = "C"
            if return_enable_feed_c == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif return_enable_feed_c == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        elif AppPrefs.feed_CurrentMode == "D":
            return_enable_feed_d = AppPrefs.outletDict[outlet].return_enable_feed_d
            AppPrefs.feed_PreviousMode = "D"
            if return_enable_feed_d == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif return_enable_feed_d == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        else:
            difference = round(((int(AppPrefs.feed_ExtraTimeSeed) + (int(
                AppPrefs.feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)

            if int(round(time.time())*1000) <= int(AppPrefs.feed_ExtraTimeSeed) + (int(AppPrefs.feed_ExtraTimeAdded)*1000):
                #print("Extra feed time remaining: " + str(difference) + "s")
                # print(Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                #       " Delay Mode: " + outlet +
                #       " (" + str(controller.AppPrefs.feed_ExtraTimeAdded) + "s) " +
                #       " Delay Time Remaining: " + str(round(difference)) + "s"
                #       + Style.RESET_ALL)
                AppPrefs.logger.debug("Delay Mode: " + outlet +
                      " (" + str(AppPrefs.feed_ExtraTimeAdded) + "s) " +
                      " Delay Time Remaining: " + str(round(difference)) + "s")
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (delay)"
                # return "OFF (delay " + str(round(difference)) + "s" + ")"
            else:
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
    else:
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        # return "OFF"

    AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin)
    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                          "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                          " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                          " | Mode: " + AppPrefs.outletDict[outlet].button_state + \
                                          " | Status: " + get_on_or_off(pin)  )


def handle_outlet_skimmer(AppPrefs, outlet, button_state, pin):
    if AppPrefs.feed_PreviousMode == "A":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_a", "0")
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].skimmer_feed_delay_a
    elif AppPrefs.feed_PreviousMode == "B":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_b", "0")
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].skimmer_feed_delay_b
    elif AppPrefs.feed_PreviousMode == "C":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_c", "0")
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].skimmer_feed_delay_c
    elif AppPrefs.feed_PreviousMode == "D":
        #controller.AppPrefs.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_d", "0")
        AppPrefs.feed_ExtraTimeAdded = AppPrefs.outletDict[
            outlet].skimmer_feed_delay_d
    else:
        AppPrefs.feed_ExtraTimeAdded = 0

    if button_state == "OFF":
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        # return "OFF"
    elif button_state == "ON":
        #GPIO.output(pin, False)
        handle_on_off(AppPrefs, outlet, pin, PIN_ON)
        # return "ON"
    elif button_state == "AUTO":
        if AppPrefs.feed_CurrentMode == "A":
            #skimmer_enable_feed_a = defs_common.readINIfile(outlet, "skimmer_enable_feed_a", "False")
            skimmer_enable_feed_a = AppPrefs.outletDict[outlet].skimmer_enable_feed_a
            AppPrefs.feed_PreviousMode = "A"
            if skimmer_enable_feed_a == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif skimmer_enable_feed_a == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        elif AppPrefs.feed_CurrentMode == "B":
            #skimmer_enable_feed_b = defs_common.readINIfile(outlet, "skimmer_enable_feed_b", "False")
            skimmer_enable_feed_b = AppPrefs.outletDict[outlet].skimmer_enable_feed_b
            AppPrefs.feed_PreviousMode = "B"
            if skimmer_enable_feed_b == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif skimmer_enable_feed_b == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        elif AppPrefs.feed_CurrentMode == "C":
            #skimmer_enable_feed_c = defs_common.readINIfile(outlet, "skimmer_enable_feed_c", "False")
            skimmer_enable_feed_c = AppPrefs.outletDict[outlet].skimmer_enable_feed_c
            AppPrefs.feed_PreviousMode = "C"
            if skimmer_enable_feed_c == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif skimmer_enable_feed_c == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        elif AppPrefs.feed_CurrentMode == "D":
            #skimmer_enable_feed_d = defs_common.readINIfile(outlet, "skimmer_enable_feed_d", "False")
            skimmer_enable_feed_d = AppPrefs.outletDict[outlet].skimmer_enable_feed_d
            AppPrefs.feed_PreviousMode = "D"
            if skimmer_enable_feed_d == "true":
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (feed)"
            elif skimmer_enable_feed_d == "false":
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
        else:
            difference = round(((int(AppPrefs.feed_ExtraTimeSeed) + (int(
                AppPrefs.feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
            if int(round(time.time())*1000) <= int(AppPrefs.feed_ExtraTimeSeed) + (int(AppPrefs.feed_ExtraTimeAdded)*1000):
                #print("Extra feed time remaining: " + str(difference) + "s")
                # print(Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                #       " Delay Mode: " + outlet +
                #       " (" + str(controller.AppPrefs.feed_ExtraTimeAdded) + "s) " +
                #       " Delay Time Remaining: " + str(round(difference)) + "s"
                #       + Style.RESET_ALL)
                
                AppPrefs.logger.info ("Delay Mode: " + outlet +
                      " (" + str(AppPrefs.feed_ExtraTimeAdded) + "s) " +
                      " Delay Time Remaining: " + str(round(difference)) + "s")
                #GPIO.output(pin, True)
                handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
                # return "OFF (delay)"
                # return "OFF (delay " + str(round(difference)) + "s" + ")"
            else:
                #GPIO.output(pin, False)
                handle_on_off(AppPrefs, outlet, pin, PIN_ON)
                # return "ON"
    else:
        #GPIO.output(pin, True)
        handle_on_off(AppPrefs, outlet, pin, PIN_OFF)
        # return "OFF"
    
    AppPrefs.outletDict[outlet].outletstatus = get_on_or_off(pin)
    AppPrefs.logger.debug("[" + AppPrefs.outletDict[outlet].outletid + "] " + \
                                          "Type: " + AppPrefs.outletDict[outlet].control_type + \
                                          " | Name: " + AppPrefs.outletDict[outlet].outletname +  \
                                          " | Mode: " + AppPrefs.outletDict[outlet].button_state + \
                                          " | Status: " + get_on_or_off(pin)  )
