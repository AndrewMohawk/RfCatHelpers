#!/usr/bin/env python

import sys
from rflib import *
from struct import *
import bitstring
import operator
import argparse
import time

parser = argparse.ArgumentParser(description='Dumb application to replay a signal',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-n', action="store", dest="numSignals",default=3,help='Number of signals to capture before replaying',type=int)
parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
results = parser.parse_args()

rawCapture = [];
print "Configuring RfCat"
d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(results.baseFreq)
d.setMdmSyncMode(0)
d.setMdmDRate(results.baudRate)
d.setMdmChanSpc(results.chanWidth)
d.setChannel(0)
d.lowball()

print "Searching..."
while True:
	try:
		
		y, t = d.RFrecv(1)
		sampleString=y.encode('hex')
		strength= 0 - ord(str(d.getRSSI()))
		
		
		if (re.search(r'((0)\2{25,})', sampleString)):
			rawCapture.append(sampleString)
			print "Found " + str(sampleString)
			print "Signal Strength:" + str(strength)
			if(len(rawCapture) >= results.numSignals):
				break;
		
			
		
		
	except ChipconUsbTimeoutException:
		pass
	except KeyboardInterrupt:
		
		
		break

print "Sending..."
raw_input("Press any key to resend packets")
emptykey = '\x00\x00\x00\x00\x00\x00\x00'
d.makePktFLEN(len(emptykey))
d.RFxmit(emptykey)
time.sleep(1)
for i in range(0,len(rawCapture)):
	key_packed = bitstring.BitArray(hex=rawCapture[i]).tobytes()
	d.makePktFLEN(len(key_packed))
	d.RFxmit(key_packed)
	print "Sent " + str(i+1) + " of " + str(len(rawCapture))
print "exiting."
d.setModeIDLE()
