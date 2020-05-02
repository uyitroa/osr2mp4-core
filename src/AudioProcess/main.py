from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from collections import namedtuple
import time
from collections import namedtuple
start=time.time()



class Position(namedtuple('Position', 'x y')):
        pass


a = open("map_thegame.txt", "r")

beatmap_info = eval(a.read())
Info = namedtuple("Info", "time combo combostatus showscore score accuracy clicks hitresult timestamp more")
Circle = namedtuple("Circle", "state deltat followstate sliderhead x y")
Slider = namedtuple("Slider", "followstate hitvalue tickend x y")
Spinner = namedtuple("Spinner", "rotate progress bonusscore hitvalue")

a = open("tengaku.txt", "r")
exec("my_info=" + a.read())

def read(f):
        if f[-1] == "3":
            a = AudioSegment.from_mp3(f)
        else:
            a = AudioSegment.from_file(f)
        y = np.array(a.get_array_of_samples())
        if a.channels == 2:
                y = y.reshape((-1, 2))
        if a.channels == 1:
                y1 = np.zeros((len(y), 2), dtype=y.dtype)
                y1[:, 0] = y
                y1[:, 1] = y
                y = y1
        return a.frame_rate, np.float32(y) / 2**(a.sample_width * 8 - 1)

def pydubtonumpy(a):
        y = np.array(a.get_array_of_samples())
        if a.channels == 2:
                y = y.reshape((-1, 2))
        if a.channels == 1:
                y1 = np.zeros((len(y), 2), dtype=y.dtype)
                y1[:, 0] = y
                y1[:, 1] = y
                y = y1
        return a.frame_rate, np.float32(y) / 2**(a.sample_width * 8 - 1)

ratey, y = read('hit1.wav')
rate, z = read('Tengaku.mp3')
rateM, m = read('miss1.wav')
ratesb, b = read('spinnerbonus.wav')
ratesc, c = read('spinnerspin.wav')
#rateS, s = read('slider.wav')

spinSound = AudioSegment.from_wav("spinnerspin.wav")
slider12 = AudioSegment.from_wav("slider.wav")

spinBonusTime = 0
spinRotationTime = 0
length_bonus = len(b)/ratesb
length_spin = len(c)/ratesc
spinSpeedup = 6
speedup_dict = {}
for x in range(6,0,-2):
    fr = spinSound.frame_rate + int(spinSound.frame_rate / x)
    faster_senpai = spinSound._spawn(spinSound.raw_data, overrides={'frame_rate': fr})
    faster_senpai_export = faster_senpai.set_frame_rate(44100)
    faster_rate , faster_c = pydubtonumpy(faster_senpai_export)
    speedup_dict["sound_" + str(x)] =  faster_c



slider_duration = 0
arrow_time = 0
arrow_time_list = []
countT = 0
for x in range(len(my_info)):


    start_index = int(my_info[x].time/1000 * rate)

    if x < len(beatmap_info) and "slider" in beatmap_info[x]["type"]:
        spinSpeedup = 6
        arrow_time_list = []    
        for a in range(beatmap_info[x]["repeated"]):
                arrow_time_list.append(beatmap_info[x]["time"] + beatmap_info[x]["duration"] * a+1)
        
        if my_info[x].time <  beatmap_info[x]["time"] + beatmap_info[x]["duration"] * beatmap_info[x]["repeated"]:
                for abc in arrow_time_list:
                        start_index2 = int(abc/1000 * rate)
                        z[start_index2:start_index2 + len(y)] += y * 0.5
                
    if not type(my_info[x].more).__name__ == "Spinner":
                spinSpeedup = 6
                if my_info[x].hitresult == None:
                        continue

                elif my_info[x].hitresult > 0:
                        z[start_index:start_index + len(y)] += y * 0.5
                elif my_info[x].hitresult == 0:
                        z[start_index:start_index + len(m)] += m * 0.5



    elif type(my_info[x].more).__name__ == "Spinner":
        if int(my_info[x].more.rotate) >= 180:
            if my_info[x].time/1000 < spinRotationTime:
                pass
            else:
                z[start_index:start_index + len(speedup_dict["sound_" + str(spinSpeedup)])] += speedup_dict["sound_" + str(spinSpeedup)] * 0.5
                spinRotationTime = my_info[x].time/1000 + length_spin
                if spinSpeedup != 2:
                    spinSpeedup -= 2

        if my_info[x].more.bonusscore  > 0:
            if my_info[x].time/1000 < spinBonusTime:
                continue
            else:
                z[start_index:start_index + len(b)] += b * 0.5
                spinBonusTime = my_info[x].time/1000 + length_bonus



write('out.mp3', rate, z)

end=time.time()
print(end-start)
