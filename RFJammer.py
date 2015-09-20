#!/usr/bin/env python

import sys
import datetime as dt
from rflib import *
from struct import *
import bitstring
import operator
import time
import argparse

keyLen = 0
baudRate = 4800
frequency = 433880000
repeatNum = 25

def ConfigureD(d):
	d.setMdmModulation(MOD_ASK_OOK)
	d.setFreq(frequency)
	d.makePktFLEN(0)
	d.setMdmDRate(4800)
	d.setRFRegister(PA_TABLE0, 0xFF)
	d.setRFRegister(PA_TABLE1, 0xFF)

def jamFreq(d,freq):
 d.setModeTX()

def stopJam(d):
 d.setModeIDLE()
 d.setRFRegister(PA_TABLE0, 0x00)
 d.setRFRegister(PA_TABLE1, 0x00) 
 
 
parser = argparse.ArgumentParser(description='Application to use a RFCat compatible device to Jam a particular frequency',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-t', action="store", dest="jamTime",default=15,help='Seconds to jam for, defaults to 15 seconds',type=int)
results = parser.parse_args()

print "Configuring RfCat"
d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(results.baseFreq)
d.setMdmSyncMode(0)
d.setMdmDRate(results.baudRate)
d.setMdmChanSpc(24000)
d.setModeIDLE()



abort_after = results.jamTime
start = time.time()
print "Starting Jam on " + str(results.baseFreq)
try:
	jamFreq(d,results.baseFreq)
except ChipconUsbTimeoutException:
	pass

while True:
  delta = time.time() - start
  if delta >= abort_after:
    break

print "Completed Jam"
d.setModeIDLE()
