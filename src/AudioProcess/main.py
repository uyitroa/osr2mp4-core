from collections import namedtuple
from pydub import AudioSegment
from pydub.playback import play
import time
start = time.time()
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

spinBonusTime = 0
spinRotationTime = 0

lenF = int(len(my_info)/4)
whileV=0

while int(my_info[whileV].time) < len(oneF):
    whileV+=1
    if my_info[whileV].hitresult == None:
        pass

    elif my_info[whileV].hitresult == 0:
        oneF = oneF.overlay(miss,position=my_info[whileV].time)

    elif my_info[whileV].hitresult >0:
        oneF = oneF.overlay(hit,position=my_info[whileV].time)
    if type(my_info[whileV].more).__name__ == "Spinner":
        if int(my_info[whileV].more.rotate) >= 180:
            if my_info[whileV].time < spinRotationTime:
                pass
            else:
                oneF = oneF.overlay(spinnerSpin,position=my_info[whileV].time)
                spinRotationTime = my_info[whileV].time + len(spinnerSpin)

        if my_info[whileV].more.bonusscore  > 0:
           if my_info[whileV].time < spinBonusTime:
               continue
           else:
               oneF = oneF.overlay(spinnerBonus,position=my_info[whileV].time+len(spinnerBonus)*2)
               spinBonusTime = my_info[whileV].time + len(spinnerBonus)

spinBonusTime = 0
spinRotationTime = 0
while int(my_info[whileV].time) < len(oneF*2):
    whileV+=1
    if my_info[whileV].hitresult == None:
        pass

    elif my_info[whileV].hitresult == 0:
        secondF = secondF.overlay(miss,position=my_info[whileV].time - mainLength)

    elif my_info[whileV].hitresult >0:
        secondF = secondF.overlay(hit,position=my_info[whileV].time - mainLength)

    if type(my_info[whileV].more).__name__ == "Spinner":

        if int(my_info[whileV].more.rotate) >= 180:
            if my_info[whileV].time < spinRotationTime:
                pass
            else:
                oneF = oneF.overlay(spinnerSpin,position=my_info[whileV].time)
                spinRotationTime = my_info[whileV].time + len(spinnerSpin)

        if my_info[whileV].more.bonusscore  > 0:
           if my_info[whileV].time < spinBonusTime:
               continue
           else:
               oneF = oneF.overlay(spinnerBonus,position=my_info[whileV].time+len(spinnerBonus)*2)
               spinBonusTime = my_info[whileV].time + len(spinnerBonus)
spinBonusTime = 0
spinRotationTime = 0
while int(my_info[whileV].time) < len(oneF*3):
    whileV+=1
    if my_info[whileV].hitresult == None:
        pass

    elif my_info[whileV].hitresult == 0:
        thirdF = thirdF.overlay(miss,position=my_info[whileV].time - mainLength-mainLength)

    elif my_info[whileV].hitresult > 0:
        thirdF = thirdF.overlay(hit,position=my_info[whileV].time-mainLength-mainLength)

    if type(my_info[whileV].more).__name__ == "Spinner":

        if int(my_info[whileV].more.rotate) >= 180:
            if my_info[whileV].time < spinRotationTime:
                pass
            else:
                oneF = oneF.overlay(spinnerSpin,position=my_info[whileV].time)
                spinRotationTime = my_info[whileV].time + len(spinnerSpin)

        if my_info[whileV].more.bonusscore  > 0:
           if my_info[whileV].time < spinBonusTime:
               continue
           else:
               oneF = oneF.overlay(spinnerBonus,position=my_info[whileV].time+len(spinnerBonus)*2)
               spinBonusTime = my_info[whileV].time + len(spinnerBonus)
spinBonusTime = 0
spinRotationTime = 0
while whileV < len(my_info) - 1:
    whileV+=1
    if my_info[whileV].hitresult == None:
        pass

    elif my_info[whileV].hitresult == 0:
        fourthF = fourthF.overlay(miss,position=my_info[whileV].time-mainLength-mainLength-mainLength)

    elif my_info[whileV].hitresult >0:
        fourthF = fourthF.overlay(hit,position=my_info[whileV].time-mainLength-mainLength-mainLength)
    if type(my_info[whileV].more).__name__ == "Spinner":

        if int(my_info[whileV].more.rotate) >= 180:
            if my_info[whileV].time < spinRotationTime:
                pass
            else:
                oneF = oneF.overlay(spinnerSpin,position=my_info[whileV].time)
                spinRotationTime = my_info[whileV].time + len(spinnerSpin)

        if my_info[whileV].more.bonusscore  > 0:
           if my_info[whileV].time < spinBonusTime:
               continue
           else:
               oneF = oneF.overlay(spinnerBonus,position=my_info[whileV].time+len(spinnerBonus)*2)
               spinBonusTime = my_info[whileV].time + len(spinnerBonus)


combined = oneF+secondF+thirdF+fourthF
combined.export("output.mp3",format="mp3")

end=time.time()
print(end-start)
print("Current Length = {}\nTarget Length = {}".format(whileV,len(song)))
