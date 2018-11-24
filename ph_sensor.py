# these are the calibration points of the Ph probe.  Change the
# digital values as necessary
dv_ph4 = 980
dv_ph7 = 819
dv_ph10 = 663


# check the digital counts vs the counts at 7.0 ph calibration value
# if it is lower, use the lower cal values, if higher, then
# user the higher cal values.  This is because the slope of the curve is
# different when lower or higher than 7.0 ph. Convert the digital value to a
# ph value
def dv2ph(dv):
    if dv <= dv_ph7:
        ph = 7 + (dv_ph7 - dv) / ((dv_ph7 - dv_ph10) / 3)
    else:
        ph = 7 + (dv_ph7 - dv) / ((dv_ph4 - dv_ph7) / 3)
    return ph
