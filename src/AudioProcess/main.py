from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from collections import namedtuple
import time
from collections import namedtuple
import os
from pathlib import Path


class Position(namedtuple('Position', 'x y')):  
		pass
def checkAudio(skin_path,default_skinP):
        skin_path += "/"
        default_skinP += "/"
        try:
            ratey, y = read(skin_path + 'normal-hitnormal.wav')
            rate, z = read(skin_path + 'Tengaku.mp3')
            rateM, m = read(skin_path + 'miss1.wav')
            ratesb, b = read(skin_path + 'spinnerbonus.wav')
            ratesc, c = read(skin_path + 'spinnerspin.wav')
            rateS, s = read(skin_path + 'slider.wav')

            spinSound = AudioSegment.from_wav(skin_path + "spinnerspin.wav")
            slider12 = AudioSegment.from_wav(skin_path + "slider.wav")
        except FileNotFoundError:
            ratey, y = read(skin_path + 'normal-hitnormal.mp3')
            rate, z = read(skin_path + 'Tengaku.wav')
            rateM, m = read(skin_path + 'miss1.mp3')
            ratesb, b = read(skin_path + 'spinnerbonus.mp3')
            ratesc, c = read(skin_path + 'spinnerspin.mp3')
            rateS, s = read(skin_path + 'slider.mp3')

            spinSound = AudioSegment.from_wav(skin_path + "spinnerspin.mp3")
            slider12 = AudioSegment.from_wav(skin_path + "slider.mp3")
        else:
            try:
                ratey, y = read(default_skinP + 'normal-hitnormal.wav')
                rate, z = read(default_skinP + 'Tengaku.mp3')
                rateM, m = read(default_skinP + 'miss1.wav')
                ratesb, b = read(default_skinP + 'spinnerbonus.wav')
                ratesc, c = read(default_skinP + 'spinnerspin.wav')
                rateS, s = read(default_skinP + 'slider.wav')

                spinSound = AudioSegment.from_wav(default_skinP + "spinnerspin.wav")
                slider12 = AudioSegment.from_wav(default_skinP + "slider.wav")
            except FileNotFoundError:
                ratey, y = read(default_skinP + 'normal-hitnormal.mp3')
                rate, z = read(default_skinP + 'Tengaku.wav')
                rateM, m = read(default_skinP + 'miss1.mp3')
                ratesb, b = read(default_skinP + 'spinnerbonus.mp3')
                ratesc, c = read(default_skinP + 'spinnerspin.mp3')
                rateS, s = read(default_skinP + 'slider.mp3')

                spinSound = AudioSegment.from_wav(default_skinP + "spinnerspin.mp3")
                slider12 = AudioSegment.from_wav(default_skinP + "slider.mp3")
        return rate,y,rate,z,rateM,m,ratesb,b,ratesc,c,rateS,s

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

def parseData():

        a = open("map_thegame.txt", "r")

        beatmap_info = eval(a.read())
        Info = namedtuple("Info", "time combo combostatus showscore score accuracy clicks hitresult timestamp more")
        Circle = namedtuple("Circle", "state deltat followstate sliderhead x y")
        Slider = namedtuple("Slider", "followstate hitvalue tickend x y")
        Spinner = namedtuple("Spinner", "rotate progress bonusscore hitvalue")

        a = open("tengaku.txt", "r")
        my_info = eval(a.read())
        return my_info, beatmap_info

def processAudio(my_info,beatmap_info,skin_path,audio_name,offset,default_skinP):
        rate,y,rate,z,rateM,m,ratesb,b,ratesc,c,rateS,s = checkAudio(skin_path,default_skinP)
        start=time.time()


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
        sliderTime = []
        repeatedTime = []
        durationTime = []
        endTime = []
            
        for bp in range(len(beatmap_info)):
                if "slider" in beatmap_info[bp]["type"]:
                        sliderTime.append(beatmap_info[bp]["time"])
                        repeatedTime.append(beatmap_info[bp]["repeated"])
                        durationTime.append(beatmap_info[bp]["duration"])
                        endTime.append(beatmap_info[bp]["end time"])
        print("Total Slider Length: " + str(len(sliderTime)))
        sliderCount = 0
        for x in range(len(my_info)):
            start_index = int(my_info[x].time/1000 * rate)

            if type(my_info[x].more).__name__ == "Circle":
                spinSpeedup = 6
                if my_info[x].more.sliderhead == True:
                        
                        arrow_time_list = []
                        for a in range(repeatedTime[0]):        
                                arrow_time_list.append(sliderTime[0] + durationTime[0] * (a+1))
                        start_index2 = int(sliderTime[0]/1000 * rate)
                        z[start_index2:start_index2 + len(s)] += s * 0.5
                        for abc in arrow_time_list:
                                start_index2 = int(abc/1000 * rate)
                                z[start_index2:start_index2+ len(s)] += s * 0.5
                            
                        sliderCount+=1
                        durationTime.pop(0)
                        sliderTime.pop(0)
                        endTime.pop(0)
                        repeatedTime.pop(0)
                        continue
                if my_info[x].hitresult == None:
                        pass

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
        print("Total Slider Added: " + str(sliderCount))
        offset = int(offset)
        write('z.mp3', rate, z[int(offset/1000)*rate:int((len(z)/rate))*rate])
        o.close()
        end=time.time()
        print(end-start)
        
if __name__ == '__main__':
        res, beat = parseData()
        processAudio(res, beat,"C:/Users/Shiho/Desktop/Projects/osr2mp4/src/AudioProcess")


