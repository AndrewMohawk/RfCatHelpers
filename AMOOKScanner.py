#!/usr/bin/env python

import sys
from rflib import *
import operator
import time
import argparse


parser = argparse.ArgumentParser(description='Application to use a RFCat compatible device to listen and calculate binary of a transmitted signal',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
parser.add_argument('-b', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-vv', action="store_true", dest="verbose", default=False,help='Verbose output')
results = parser.parse_args()


d = RfCat()

d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(results.baseFreq)
d.makePktFLEN(0)
d.setMdmDRate(results.baudRate)
d.lowball(0)
d.setModeRX()



d.setMdmChanSpc(results.chanWidth)
d.setChannel(0)

lens = dict() 
allstrings = []
stored_codes = []


start = time.time()
print "Starting scan..."
while True:
	try:
		
		y, t = d.RFrecv(1)
		sampleString=y.encode('hex')
				
		zeroPadding = [match[0] for match in re.findall(r'((0)\2{25,})', sampleString)]
		for z in zeroPadding:
			currLen = len(z)
			if currLen in lens.keys():
				lens[currLen] = lens[currLen] + 1
			else:
				lens[currLen] = 1
		sorted_lens = sorted(lens.items(), key=operator.itemgetter(1), reverse=True)
		lens = dict()
		if(sorted_lens and sorted_lens[0][0] > 0 and sorted_lens[0][0] < 400):
			zeroPaddingString = "0" * sorted_lens[0][0]
			
			
			possibleStrings = sampleString.split(zeroPaddingString)
			possibleStrings = [s.strip("0") for s in possibleStrings]
			if(results.verbose == True):
				print "Possible codes found (-vv):"
				print "---------------------------"
				print possibleStrings
			
			for s in possibleStrings:
				if(len(s) > 5):
					allstrings.append(s)
			
			if(results.verbose == True):
				print "Binary for codes found (-vv):"
				print "---------------------------"
				
			if(len(allstrings) > 0):
				lengths = [len(i) for i in allstrings]
				most_common_length = max(set(lengths), key=lengths.count)
				binaryKeys = []
				for a in allstrings:
					if(len(a) == most_common_length):
						if(results.verbose == True):
							print str(bin(int(a,16))[2:])
						binaryKeys.append(bin(int(a,16))[2:])
					else:
						if(len(a) -1 == most_common_length):
							if(results.verbose == True):
								print str(bin(int(a,16))[2:-1])
							binaryKeys.append(bin(int(a,16))[2:-1])

				maxlen = len(max(binaryKeys, key=len))
				
				for i in range(0,len(binaryKeys)):
					if(len(binaryKeys[i]) < maxlen):
						binaryKeys[i] = binaryKeys[i] + ("0" * (maxlen - len(binaryKeys[i])))
				
				print "Possible Signals:" + str(len(allstrings))
				finalKey = "";
				for charPos in range(0,maxlen):
					total = 0;
					for i in range(0,len(binaryKeys)):
						thisChar = binaryKeys[i][charPos]
						total += int(thisChar)
					if(total > (len(binaryKeys) / 2)):
						finalKey += "1"
					else:
						finalKey += "0"
				print "Calculated Key (bin): " + finalKey
				print "--------"

	except ChipconUsbTimeoutException:
		pass
	except KeyboardInterrupt:
		d.setModeIDLE()
		print "bye."
		sys.exit()
		pass
d.setModeIDLE()
print "bye."
sys.exit()


