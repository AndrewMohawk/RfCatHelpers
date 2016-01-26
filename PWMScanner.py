#!/usr/bin/env python

import sys
import time
from rflib import *
from struct import *
import argparse
import bitstring
import re
import operator
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import datetime as dt
import select
import tty
import termios



chr = 0
keyLen = 0
baudRate = 4800
frequency = 433855000
repeatNum = 25

def ConfigureD(d):
	d.setMdmModulation(MOD_ASK_OOK)
	d.setFreq(frequency)
	d.makePktFLEN(keyLen)
	d.setMdmDRate(baudRate)
	#d.setMdmChanBW(1);
	#d.setMaxPower()
	d.lowball()
	
	if(results.verbose == True):
	  print "[+] Radio Config:"
	  print " [-] ---------------------------------"
	  print " [-] MDMModulation: MOD_ASK_OOK"
	  print " [-] Frequency: ",frequency
	  print " [-] Packet Length:",keyLen
	  print " [-] Baud Rate:",baudRate
	  print "[-] ---------------------------------"

print ""
print "######################################################"
print "#                PWM Scanning with RFCat             #"
print "#                                                    #"
print "#                  @AndrewMohawk                     #"
print "#           http://www.andrewmohawk.com              #"
print "#                                                    #"
print "######################################################"
print ""
parser = argparse.ArgumentParser(description='Simple program to scan for PWM OOK codes',version="RFCat PWM Scanner 0.01 - by Andrew MacPherson (www.andrewmohawk.com) / @AndrewMohawk ")
parser.add_argument('-fa', action="store", default="433000000", dest="startFreq",help='Frequency to start scan at, defaults to 433000000',type=long)
parser.add_argument('-fb', action="store", default="434000000", dest="endFreq",help='Frequency to end scan at, defaults to 434000000',type=long)
parser.add_argument('-fs', action="store", default="50000", dest="stepFreq",help='Frequency step for scanning, defaults to 50000',type=long)
parser.add_argument('-ft', action="store", default="1000", dest="timeStepFreq",help='Frequency step delay, defaults to 1000 milliseconds',type=long)
parser.add_argument('-vv', action="store_true", dest="verbose", default=False,help='Verbose output')
parser.add_argument('-a',action="store_true", default=False,help='Automatically replay after collecting')
parser.add_argument('-br', action="store", dest="baudRate",default=4800,help='Baudrate to transmit at, defaults to 4800',type=int)
parser.add_argument('-r', action="store", dest="repeat", default=15,help='Amount of times to repeat when transmitting, defaults to 15',type=int)
parser.add_argument('-p', action="store", dest="paddingZeros", default=15,help='Amount of repeated zeros to search for when looking for patterns',type=int)
#parser.add_argument('-g',action="store_true",dest="showGraph", default=False,help='Show graph of data')
parser.add_argument('-ms', action="store", dest="minimumStrength", default=-80,help='Minimum strength, defaults to -80',type=int)
parser.add_argument('-ln', action="store", dest="lockNum", default=5,help='Minimum `codes` to receive before locking',type=int)
parser.add_argument('-rp', action="store_true", dest="replayKey", default=True,help='Replay most common code automatically, default true')
results = parser.parse_args()

currFreq = results.startFreq;
repeatNum = results.repeat
frequency = currFreq
sys.stdout.write("Configuring RFCat...\n")
d = RfCat()
ConfigureD(d)
allstrings = {}
lens = dict() 
lockOnSignal = True
lockedFreq = False

'''
if (results.showGraph == True):
	x = range(0,38)
	y = range(0,38)
	line, = plt.plot(x,y,"-")
	plt.ion()
	plt.show()
	plt.draw()
	x = range(0,38)
	line.set_xdata(x)
'''
def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()
BOLD = '\033[1;37;40m'
ENDC = '\033[0m'
RED = '\033[1;31;40m'
BLUE = '\033[1;34;40m'
GREEN = '\033[1;32;40m'
YELLOW = '\033[1;33;40m'
WHITE = '\033[1;37;40m'
LIGHTBLUE = '\033[1;36;40m'



print "Scanning for AM/OOK Remotes... Press " + BOLD + WHITE + "<enter>" + ENDC + " to stop and "  + BOLD + WHITE + " any key" + ENDC + " to continue\n"

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

def showStatus():
	sys.stdout.write('\r' + BOLD +  ENDC + "[ " + BOLD + YELLOW)
	sys.stdout.write(spinner.next())
	strength= 0 - ord(str(d.getRSSI()))
	sigFound = "0"
	if(currFreq in allstrings):
		sigFound = str(len(allstrings[currFreq]))
	sys.stdout.write(ENDC + ' ] Freq: [ ' + LIGHTBLUE + str(currFreq) + ENDC + ' ] Strength [ ' + YELLOW + str(strength) + ENDC + ' ] Signals Found: [ ' + GREEN + sigFound + ENDC + " ]" )
	if(lockedFreq == True):
		sys.stdout.write(ENDC + RED + " [!FREQ LOCKED!]" + ENDC)
	#else:
	#	sys.stdout.write(" " * 30)
	#sys.stdout.write(" " * 10)
	#yes, i know, icky!
	sys.stdout.flush()
	#sys.stdout.write("\n- Press Any Key to End Scan -");

n1=dt.datetime.now()



while True:
	try:
		if isData():
			x= ord(sys.stdin.read(1))
			if (x == 3 or x == 10):
				break
			elif(x == 32):
				print "unlocking";
				currFreq += results.stepFreq
				lockedFreq = False
		y, t = d.RFrecv(1)
		sampleString=y.encode('hex')
		# lets find all the zero's
		showStatus();
		#print "Received:  %s" % (y.encode('hex'))
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
			#print "zeros used in padding: " , zeroPaddingString

			possibleStrings = sampleString.split(zeroPaddingString)
			possibleStrings = [s.strip("0") for s in possibleStrings]
			#print possibleStrings
			for s in possibleStrings:
				if(currFreq in allstrings):
					allstrings[currFreq].append(s)
				else:
					allstrings[currFreq] = [s]
				if((len(allstrings[currFreq]) > results.lockNum) and lockOnSignal == True):
					lockedFreq = True

		n2=dt.datetime.now()
		if(((n2-n1).microseconds * 1000) >= results.timeStepFreq):
			if(lockedFreq == False):
				currFreq += results.stepFreq
				if(currFreq > results.endFreq):
					currFreq = results.startFreq
				n1=dt.datetime.now()
				d.setFreq(currFreq)
		
	except KeyboardInterrupt:
		break
	except ChipconUsbTimeoutException:
		pass
	
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
# hacky, but i wanna get rid of the line:
print "\r" + (" " * 150)


print "Scanning stopped, keys found in following frequencies:"
sortedKeys = sorted(allstrings, key=lambda k: len(allstrings[k]), reverse=True)

num = 1;
if(results.verbose == True):
	print "**VERBOSE** ALL keys found:"
	for sK in sortedKeys:
		currLen  = len(allstrings[sK])
		print num,": ",str(sK)," - Num signals Found:",currLen
		print "-----------------------------------------------"
		for verbose_key in allstrings[sK]:
			print verbose_key
		num=num+1
num = 1;
for sK in sortedKeys:
	currLen  = len(allstrings[sK])
	print num,": ",str(sK)," - Num signals Found:",currLen
	num=num+1


if(results.replayKey == True and len(sortedKeys) > 0):
	var = 200;
	while((var < 0) or (var > len(sortedKeys))):
		try:
			var = int(raw_input("Please enter key to use for replaying: "))
		except ValueError:
			pass
	allstrings = allstrings[sortedKeys[var-1]]
	d.setFreq(sortedKeys[var-1])
	
	for a in allstrings:
		currLen = len(a)
		if currLen in lens.keys():
			lens[currLen] = lens[currLen] + 1
		else:
			lens[currLen] = 1

	sorted_lens = sorted(lens.items(), key=operator.itemgetter(1), reverse=True)
	if len(sorted_lens) > 0:
		searchLen = sorted_lens[0][0]
		if(results.verbose == True):
			print "\nFound most keys in string have a length of " + str(searchLen) + " using those keys to calculate common key."
		foundKeys = []
		for a in allstrings:
			if(len(a) == searchLen):
				foundKeys.append(bin(int(a,16))[2:])
		 #print bin(int(a,16))


		maxlen = 0;
		for foundKey in foundKeys:
			if len(foundKey) > maxlen:
				maxlen = len(foundKey)
		#print maxlen
		for i in range(0,len(foundKeys)):
			if(len(foundKeys[i]) < maxlen):
				foundKeys[i] = foundKeys[i] + ("0" * (maxlen - len(foundKeys[i])))

		finalKey = "";
		for charPos in range(0,maxlen):
			total = 0;
			for i in range(0,len(foundKeys)):
				thisChar = foundKeys[i][charPos]
				total += int(thisChar)
			if(total > (len(foundKeys) / 2)):
				finalKey += "1"
			else:
				finalKey += "0"
		if(results.verbose == True):
			print "\nUsing Final Key as:"
			print BOLD + "BIN:" + ENDC + str(finalKey)

		key_packed = bitstring.BitArray(bin=finalKey).tobytes()

		keyLen = len(key_packed)

		print "[+] Key len:\n\t",keyLen,""
		print "[+] Key:\n\t", key_packed.encode('hex')
		print "[+] Freq:\n\t", str(sortedKeys[var-1])
		
		d.makePktFLEN(keyLen)

		print "[+] Transmitting key: ",repeatNum," times"
		barSize = 50
		for i in range(0,repeatNum):
			d.RFxmit(key_packed)
			progress = (float(i+1)/repeatNum)
			progVal = int(round(progress * barSize))
			progressBar = ("#" * progVal) + (" " * (barSize - progVal))
			sys.stdout.write("\r\tPercent: [ " + str(progressBar) + " ] " + str(int(progress * 100)) + "%")
			sys.stdout.flush()

		sys.stdout.write("\nDone.\n")
		d.setModeIDLE()
	 
	
else:
	print "\n\nNo keys found :(\nbye."
