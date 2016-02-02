#!/usr/bin/env python

import sys
import datetime as dt
from rflib import *
from struct import *
import bitstring
import operator
import time
import argparse


APP_NIC =                       0x42
RFCAT_START_SPECAN  =           0x40
RFCAT_STOP_SPECAN   =           0x41
APP_SYSTEM          =           0xff
SYS_CMD_RFMODE      =           0x88
SPECAN_QUEUE        =           1
RFST_SRX            =           0x02

keyLen = 0
baudRate = 4800
leaveLoop = False;



def startJam(rfcatInstance,rfcatjamFreq):
 rfcatInstance.setMaxPower()
 rfcatInstance.setRFRegister(PA_TABLE0, 0xFF)
 rfcatInstance.setRFRegister(PA_TABLE1, 0xFF) 
 rfcatInstance.setFreq(rfcatjamFreq)
 rfcatInstance.setModeTX()
 print "[!] Jamming at " + str(rfcatjamFreq)

def stopJam(rfcatInstance):
 rfcatInstance.setModeIDLE()
 rfcatInstance.setRFRegister(PA_TABLE0, 0x00)
 rfcatInstance.setRFRegister(PA_TABLE1, 0x00) 

def configure(rfcatInstance):
 rfcatInstance.setMdmModulation(MOD_ASK_OOK)
 rfcatInstance.setFreq(baseFreq)
 rfcatInstance.setMdmDRate(4800)

parser = argparse.ArgumentParser(description='Application to use two RfCat compatible devices to scan for a signal and jam it',version="0.1-bricktop")
parser.add_argument('-b', action="store", default="433000000", dest="baseFreq",help='Base frequency to scan from (default 433000000)',type=int)
parser.add_argument('-o', action="store", default="100000", dest="jamOffset",help='Offset from frequency to jam (default 100000 hz)',type=int)
parser.add_argument('-m', action="store", default="-10", dest="minStrength",help='Minimum signal strength to classify signal (default -10 dbm)',type=int)
parser.add_argument('-c', action="store", default="100", dest="count",help='number of channels to scan (default 100)',type=int)
parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
results = parser.parse_args()

baseFreq = results.baseFreq
jamDistance = results.jamOffset
rssi_minimum_for_signal = results.minStrength;
count = results.count
inc = results.chanWidth
 
 
print "Setting up ScanJam - configuring Scanner"
print "----------------------------------------"
print "(i) Start: " + str(baseFreq)
print "(i) End: " +str((baseFreq + (count*inc)))
print "(i) Min dBm: " +str(rssi_minimum_for_signal)

d = RfCat(idx=0)
configure(d)
d.setModeRX()

raw_input("Press Enter to setup Jammer")
d2 = RfCat(idx=1)
configure(d2)

halfwayFreq = baseFreq + ((count * (inc/2)) / 2)


start = time.time()
startJam(d2,halfwayFreq);
end = time.time()
print end-start
time.sleep(1)
d2.setModeIDLE()

raw_input("Press Enter to start scanning...")



d.setMdmChanSpc(inc)
freq, fbytes = d.getFreq()
delta = d.getMdmChanSpc()


d.setFreq(baseFreq)

#print "[+] Scanning for signals from " + str(baseFreq) + " to " + str((baseFreq + (count*inc))) + " for anything stronger than " + str(rssi_minimum_for_signal)
print "[+] Scanning for signals..."
d.send(APP_NIC, RFCAT_START_SPECAN, "%c" % (count) )
jamming = False;
try:
	strongestSignal = rssi_minimum_for_signal #this seemed so reasonable.
	highestFreq = 0 # not sure why i have to use this rather than strongest signal >_<
	
	while True:
		jamFreq = 0
		if(jamming == False):
			#start = time.time()
			rssi_values, timestamp = d.recv(APP_SPECAN, SPECAN_QUEUE, 10000)
			#print "."
			#end = time.time()
			rssiTime = end-start
			rssi_values = [ ((ord(x)^0x80)/2)-88 for x in rssi_values ]
			
			highestVal = max(rssi_values)
			if(highestVal >= strongestSignal):
				strongestSignal = highestVal
				jamFreq = baseFreq + (rssi_values.index(highestVal) * (inc/2))
				startJam(d2,jamFreq + jamDistance)
				print rssi_values
				#end = time.time()
				#jamTime = end-start
				#print "rssitime:" + str(rssiTime)
				#print "jamTime:" + str(jamTime)
				#startJam(d2,433740000)
				#print "[+] Jamming from jammer rfcat ( d2 ) Target freq:" + str(jamFreq)						
				if(jamming == False):
					d.send(APP_NIC, RFCAT_STOP_SPECAN, '')
					print "[-] Stopping scan on scanner rfcat ( d )"
				jamming = True
	
			
			


except KeyboardInterrupt:
	print "bye."
	pass;
	

print "end.";
stopJam(d)
stopJam(d2)
d.setModeIDLE()
d2.setModeIDLE()
