#!/usr/bin/env python

import sys
from rflib import *
from struct import *
import bitstring
import operator
import argparse
import time
import pickle

parser = argparse.ArgumentParser(description='Dumb application to replay a signal',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
parser.add_argument('-p', action="store", default="100", dest="power",help='Power level for re-transmitting',type=int)
parser.add_argument('-o', action="store", default="", required=True, dest="inFile",help='File to read in')
parser.add_argument('-k', action="store", dest="waitForKeypress", default=True,help='Wait for keypress before resending')
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
d.setPower(results.power)
d.setMaxPower()
#d.setRFRegister(PA_TABLE0, 0xFF)
#d.setRFRegister(PA_TABLE1, 0xFF) 


rawCapture = pickle.load(open(results.inFile,"rb"))
if(len(rawCapture) == 0):
	print "No captures found"
	sys.exit()
else:
	print "loaded" + str(len(rawCapture))
print "Send Phase..."

emptykey = '\x00\x00\x00\x00\x00\x00\x00'
d.makePktFLEN(len(emptykey))
d.RFxmit(emptykey)
while True:
	try:
		freq = raw_input("Press <enter> to resend or type the frequency you wish to send on now:")
		if(freq != ''):
			d.setFreq(int(freq))
			
		for i in range(0,len(rawCapture)):
			key_packed = bitstring.BitArray(hex=rawCapture[i]).tobytes()
			d.makePktFLEN(len(key_packed))
			if(results.waitForKeypress == True):
				raw_input(" Press any key to send " + str(i+1) + " of " + str(len(rawCapture)))
			d.RFxmit(key_packed)
			print "Sent " + str(i+1) + " of " + str(len(rawCapture))
	except KeyboardInterrupt:
		print "Bye!"
		d.setModeIDLE()
		sys.exit()
		break;
print "exiting."
d.setModeIDLE()
#d.setRFRegister(PA_TABLE0, 0x00)
#d.setRFRegister(PA_TABLE1, 0x00) 
