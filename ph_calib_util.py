# PH probe
# Written by ReefSpy for the ReefBerry Pi, (c) 2018

import time
import os
import RPi.GPIO as GPIO
import numpy
import matplotlib.pyplot as plt
import mcp3008

# these are the calibration points of the Ph probe.  Change the
# digital values as necessary
dv_ph4 = 932
dv_ph7 = 775
dv_ph10 = 621

# data collection variables
ph_ListLength = 120     # how many ph samples to collect
ph_SamplingInterval = 1 # seconds
ph_Sigma = 1            # how many standard deviations to include 
                        # (and throw out the outliers)
binsize = 5             # bin size for each bar in the histogram graph

ph_List = []
ph_ListCounts = []

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Pi
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# ph probe connected to adc #0
ph_adc = 0;

while True:
    # read the analog pin
    ph_val = mcp3008.readadc(ph_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    ph_ListCounts.append(ph_val)
    print (len(ph_ListCounts),":", ph_val)    

    # once we hit our desired sample size ph_ListLength (ie: 120)
    # then calculate the average value
    if len(ph_ListCounts) >= ph_ListLength:
        ph_FilteredCounts = numpy.array(ph_ListCounts)
        ph_FilteredMean = numpy.mean(ph_FilteredCounts, axis=0)
        ph_FlteredSD = numpy.std(ph_FilteredCounts, axis=0)
        ph_FilteredCountList = [x for x in ph_FilteredCounts if
                                (x >= ph_FilteredMean - ph_Sigma * ph_FlteredSD)]
        ph_FilteredCountList = [x for x in ph_FilteredCountList if
                                (x <= ph_FilteredMean + ph_Sigma * ph_FlteredSD)]
            
        #ph_Avg = sum(ph_List)/len(ph_List)
        #ph_AvgCounts = int(sum(ph_ListCounts)/len(ph_ListCounts))
        ph_AvgCountsFiltered = int(sum(ph_FilteredCountList)/len(ph_FilteredCountList))


        # check the digital counts vs the counts at 7.0 ph calibration value
        # if it is lower, use the lower cal values, if higher, then
        # user the higher cal values.  This is because the slope of the curve is
        # different when lower or higher than 7.0 ph
        if ph_AvgCountsFiltered <= dv_ph7:
            ph_AvgFiltered = 7 + (dv_ph7 - ph_AvgCountsFiltered) / ((dv_ph7 - dv_ph10) / 3)
        else:
            ph_AvgFiltered = 7 + (dv_ph7 - ph_AvgCountsFiltered) / ((dv_ph4 - dv_ph7) / 3)
                
        # print ("ph avg:", "{:.1f}".format(ph_Avg))
        #print ("ph filtered:", "{:.1f}".format(ph_AvgFiltered))
        # print ("counts avg:", "{:.0f}".format(ph_AvgCounts))
        #print ("filtered avg:", "{:.0f}".format(ph_AvgCountsFiltered))
        print("############################################################")
        print("# 3-stage ph calibration")
        print("# set these to the correct values to calculate accurate ph")
        print("############################################################")
        print("# ph 4.0 calibration point:  " + str(dv_ph4))
        print("# ph 7.0 calibration point:  " + str(dv_ph7))
        print("# ph 10.0 calibration point: " + str(dv_ph10))
        print("############################################################")
        print("total samples = " + str(len(ph_ListCounts)))
        print("sample frequency = " + str(ph_SamplingInterval) + "s")
        print("mean = {:.2f}".format(ph_FilteredMean))
        print("std. dev. = {:.2f}".format(ph_FlteredSD))
        print("sigma (outlier cutoff) = " + str(ph_Sigma))
        print("__________________________________________")
        print("  ")
        print(" >>> mean dv (filtered) = " + "{:.0f}".format(ph_AvgCountsFiltered) + " <<<")
        print(" >>> ph (calculated)   = " + "{:.2f}".format(ph_AvgFiltered) + " <<<")
        print("__________________________________________  ")

        # lets plot the histogram
        bins = range (0,1023,binsize) # set up bins for histogram
        fig, ax = plt.subplots()
        n, dvbins, patches = ax.hist(ph_ListCounts, bins)
        #n, dvbins, patches = ax.hist(ph_ListCounts, bins, normed=True)
        y = ((1 / (numpy.sqrt(2 * numpy.pi) * ph_FlteredSD)) *
             numpy.exp(-0.5 * (1 / ph_FlteredSD * (bins - ph_FilteredMean))**2)) * 100 * n.max()
        ax.plot(bins,y,'--')
        
        plt.axvline(x=(ph_FilteredMean - ph_Sigma * ph_FlteredSD), color='red')

        plt.axvline(x=(ph_FilteredMean + ph_Sigma * ph_FlteredSD), color='red')
        plt.text((ph_FilteredMean + ph_Sigma * ph_FlteredSD)+4, (n.max()/2), "+" + str(ph_Sigma) +
                 r'$\sigma$', rotation=90)
        plt.text((ph_FilteredMean - ph_Sigma * ph_FlteredSD)-24, (n.max()/2),"-" + str(ph_Sigma) +
                 r'$\sigma$', rotation=90)
        #plt.text(60,10, "total samples = " + str(len(ph_ListCounts)))
        #plt.text(60,8, "sample frequency = " + str(ph_SamplingInterval) + "s")
        #plt.text(60,6, "mean = {:.2f}".format(ph_FilteredMean))
        #plt.text(60,4, r'std. dev.($\sigma$) = ' + "{:.2f}".format(ph_FlteredSD))
        #plt.text(60,2, "calibration point = " + "{:.0f}".format(ph_AvgCountsFiltered))
        plt.xlabel("digital value")
        plt.ylabel("number of samples")
        plt.title("Reefberry Pi pH Probe Test Utility")
        plt.show() 
        
        #print("clear list")       
        #ph_List.clear()
        ph_ListCounts.clear()

    # record the new sampling time
    #ph_SamplingTime = int(round(time.time()*1000)) #convert time to milliseconds
    time.sleep(ph_SamplingInterval)
