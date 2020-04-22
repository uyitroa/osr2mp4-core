from collections import namedtuple
from pydub import AudioSegment
from pydub.playback import play
import time
song = AudioSegment.from_mp3("Tengaku.mp3")
hit = AudioSegment.from_wav("hit1.wav")
miss = AudioSegment.from_wav("miss1.wav")
spinnerSpin = AudioSegment.from_mp3("spinnerspin.mp3")
spinnerBonus = AudioSegment.from_wav("spinnerbonus.wav")

Info = namedtuple("Info", "time combo combostatus showscore score accuracy clicks hitresult timestamp more")
Circle = namedtuple("Circle", "state deltat followstate sliderhead x y")
Slider = namedtuple("Slider", "followstate hitvalue tickend x y")
Spinner = namedtuple("Spinner", "rotate progress bonusscore hitvalue")

a = open("tengaku.txt", "r")
exec("my_info=" + a.read())

'''
Results = [0][7]
Time = [0][0]
'''
length = len(song)
firstH = song[:length/2]
lastH = song[-length/2:]

oneF = firstH[:len(firstH)/2]
secondF = firstH[-len(firstH)/2:]

thirdF = lastH[:len(firstH)/2]
fourthF = lastH[-len(firstH)/2:]

mainLength = len(oneF)

combined = AudioSegment.empty()

start = time.time()
spinBonusTime = 0
spinRotationTime = 0
lenF = int(len(my_info)/4)
for a in range(lenF):
    '''
    if my_info[a].hitresult == None:
        continue

    elif my_info[a].hitresult == 0:
        oneF = oneF.overlay(miss,position=my_info[a].time)

    elif my_info[a].hitresult >0:
        oneF = oneF.overlay(hit,position=my_info[a].time)
'''
    if type(my_info[a].more).__name__ == "Spinner":

        if int(my_info[a].more.rotate) >= 180:
            if my_info[a].time < spinRotationTime:
                continue
            else:
                oneF = oneF.overlay(spinnerSpin,position=my_info[a].time)
                spinRotationTime = my_info[a].time + len(spinnerSpin)

        if my_info[a].more.bonusscore  > 0:
           if my_info[a].time < spinBonusTime:
               continue
           else:
               oneF = oneF.overlay(spinnerBonus,position=my_info[a].time+len(spinnerBonus)*2)
               spinBonusTime = my_info[a].time + len(spinnerBonus)
'''

for b in range(lenF+1,lenF*2,1):
            if my_info[b].hitresult == None:
        continue

    elif my_info[b].hitresult == 0:
        secondF = secondF.overlay(miss,position=my_info[b].time - mainLength)

    elif my_info[b].hitresult >0:
        secondF = secondF.overlay(hit,position=my_info[b].time - mainLength)

for c in range(int(len(my_info)/2)+1,int(len(my_info)/2)+lenF,1):
    if my_info[c].hitresult == None:
        continue

    elif my_info[c].hitresult == 0:
        thirdF = thirdF.overlay(miss,position=my_info[c].time - mainLength-mainLength)

    elif my_info[c].hitresult > 0:
        thirdF = thirdF.overlay(hit,position=my_info[c].time-mainLength-mainLength)


for d in range(int(len(my_info)/2)+lenF+1,len(my_info),1):
    if my_info[d].hitresult == None:
        continue

    elif my_info[d].hitresult == 0:
        fourthF = fourthF.overlay(miss,position=my_info[d].time-mainLength-mainLength-mainLength)

    elif my_info[d].hitresult >0:
        fourthF = fourthF.overlay(hit,position=my_info[d].time-mainLength-mainLength-mainLength)


'''
combined = oneF+secondF+thirdF+fourthF
oneF.export("output.mp3",format="mp3")

end=time.time()
print(end-start)
