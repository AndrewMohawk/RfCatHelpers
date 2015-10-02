import wave
import sys
from struct import *
from collections import Counter

track=wave.open(sys.argv[1])
frames=track.getnframes()
n= 0
max= 0
samples= []
keylen = 12
avg = 0;

print "number of frames: {}".format(frames)

while n < frames:
	n += 1
	current = 0
        frame = track.readframes(1)

        if len(frame) != 2 and len(frame) != 4:
            continue

        left_channel = frame[:2]

	current= unpack("<h",left_channel)[0]
	if current > max:
		max= current;
	samples.append(current)


avg = sum(samples) / len(samples)
avg = avg + (max/100) + 100

print "Max: ",str(max),"Average: ",str(avg)


peaks= []
foundKeys = []
sPeak = 0 #startPeak
ePeak = 0 #endPeak
minPeakDistance = 1 #minimum peak distance

for currFrame in range(0,len(samples)):
	if(samples[currFrame] > avg):
		if(sPeak == 0):
			sPeak = currFrame #~starts here
	else:
		if(sPeak != 0 and (sPeak+minPeakDistance) < currFrame ):
			ePeak = currFrame
			distance = ePeak - sPeak
			peaks.append({"d":distance,"s":ePeak,"e":ePeak})		
			sPeak = 0
currentSeg = []
n = 0

#get average peak distance (to see dividers between signals)
#avgPeakLen = sum(peaks["d"]) / len(peaks)
#avgPeakLen = sum([p['d'] for p in peaks]) / len(peaks)
avgPeakLen = sum([peaks[i+1]['s'] - p['e'] for i, p in enumerate(peaks) if i < len(peaks) - 1])/(i + 1)
avgPeakLen = avgPeakLen * 3
print "avgpl:",avgPeakLen
print "len Peaks",len(peaks)

tmpBin = ""
while n < len(peaks):
	#if(peaks[n]["d"] > avgPeakLen and len(currentSeg) > 0):
	if(n > 1):
		diff = peaks[n]["s"] - peaks[n-1]["e"]
		#if (diff > 30):
			#print diff
	
	if(n > 1 and ((peaks[n]["s"] - peaks[n-1]["e"]) > avgPeakLen and len(currentSeg) > 1)):
		mean = (sum(currentSeg) / len(currentSeg)) - 1
		for c in currentSeg:
			if ( c > mean ):
				tmpBin += "0"
			else:
				tmpBin += "1"
		foundKeys.append(tmpBin)
		#print tmpBin
		tmpBin = "";
		currentSeg = []
	else:
		currentSeg.append(peaks[n]["d"])
	n= n + 1

#leftovers
if (len(currentSeg) > 0):
	mean = (sum(currentSeg) / len(currentSeg)) - 1
	for c in currentSeg:
		if ( c > mean ):
			tmpBin += "0"
		else:
			tmpBin += "1"
	foundKeys.append(tmpBin)
	tmpBin = "";

keyList = Counter(foundKeys)
print "\n\n(Top)Found Keys:"


	
x = 0
for k, v in keyList.most_common(10):
	if (len(k) > 2 and int(k,2) != 0):
		x+=1
		print x,":",k,"(",v,") - len:",len(k), "Hex:",hex(int(k,2))
