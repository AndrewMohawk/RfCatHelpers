import sys
from rflib import *
from struct import *
import bitstring
import argparse


def makeKey(key,large = True):
    if(key[0:1] == "1"):
     key = "1" + key
    pwm_str_key = ""
    for k in key:
        x = "*"
        if(k == "0"):
         x = "1110" # <mossmann> A zero is encoded as a longer high pulse (high-high-low)
        if(k == "1"):
         x = "1100" #<mossmann> and a one is encoded as a shorter high pulse (high-low-low).
        if(k == "x"):
         x = "0000" #<mossmann> AndrewMac: Maybe the transmitter is slow to warm up to maximum power?  What happens if you add some zero padding at the start?
        if(large == True):
         x = x + "0"
        pwm_str_key = pwm_str_key + x
    key_packed = bitstring.BitArray(bin=pwm_str_key).tobytes()
    return key_packed;
	
def makeKeyFull(key,large = True):
    pwm_str_key = key
    key_packed = bitstring.BitArray(bin=pwm_str_key).tobytes()
    return key_packed;

def sendKey(key,num):
    for i in range(0,num):
        d.RFxmit(key)
		
parser = argparse.ArgumentParser(description='Application to use a RFCat compatible device to transmit a particular AM/OOK binary signal\n Use -b for a calculated(full) binary or -c for a compact binary (full will be calculated) ',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-b', action="store", dest="fullBin",default=False,help='Full binary value to Transmit')
group.add_argument('-c', action="store", dest="compactBin", default=False,help='Compact binary value to Transmit')
parser.add_argument('-t', action="store", dest="repeatTimes",default=15,help='Number of times to repeat the signal,defaults to 15',type=int)
parser.add_argument('-vv', action="store_true", dest="verbose", default=False,help='Verbose output')
results = parser.parse_args()

freq = results.baseFreq
baudRate = results.baudRate

d = RfCat()

d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(freq)
d.setMdmSyncMode(0)
d.setMdmDRate(baudRate)

fullKey = ''
if(results.compactBin is not False):
	fullKey = makeKey(results.compactBin,True)
if(results.fullBin is not False):
	fullKey = makeKeyFull(results.fullBin,True)

d.makePktFLEN(len(fullKey))
print "Transmitting..."
sendKey(fullKey,results.repeatTimes)
print "Done."
d.setModeIDLE()
