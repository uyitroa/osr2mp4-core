from collections import namedtuple
from pydub import AudioSegment
from pydub.playback import play

song = AudioSegment.from_mp3("Tengaku.mp3")
hit = AudioSegment.from_wav("hit1.wav")
miss = AudioSegment.from_wav("miss1.wav")

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
for a in my_info:
    if not a[7] == None:
        if a[7] == 0:
            song = song.overlay(miss,position=a[0])
        elif a[7] >0:
            song = song.overlay(hit,position=a[0])
    

song.export("mixxx.mp3",format="mp3")


