from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from collections import namedtuple
import time
from collections import namedtuple
import os.path

class Position(namedtuple('Position', 'x y')):  
		pass

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

    
def checkAudio(sPath,dPath,beatmap,audio_name):
            song = beatmap + audio_name
            checked = []
            fileNames = [sPath + "normal-hitnormal",song,sPath + "miss1",sPath + "spinnerbonus",sPath + "spinnerspin",sPath + "normal-hitnormal",sPath+"spinnerspin"]
            fileNames2 = [dPath + "normal-hitnormal",song,dPath + "miss1",dPath + "spinnerbonus",dPath + "spinnerspin",dPath + "normal-hitnormal",dPath+"spinnerspin"]

            fileTypes = ".mp3",".wav"
            print(sPath)
            for x in range(7):
                if os.path.exists(sPath):
                    if os.path.exists(fileNames[x] + fileTypes[0]):
                        checked.append(fileNames[x] + fileTypes[0])
                        print("Adding: " + fileNames[x] + fileTypes[0] + "to skin path: " + sPath)
                    elif os.path.exists(fileNames[x] + fileTypes[1]):
                        checked.append(fileNames[x] + fileTypes[1])
                        print("Adding: " + fileNames[x] + fileTypes[1] + "to skin path: " + sPath)
                    else:
                       if os.path.exists(fileNames2[x] + fileTypes[0]):
                           checked.append(fileNames2[x] + fileTypes[0])
                           print("Adding: " + fileNames2[x] + fileTypes[0] + "to default skin path")
                       elif os.path.exists(fileNames2[x] + fileTypes[1]):
                            checked.append(fileNames2[x] + fileTypes[1])
                            print("Adding: " + fileNames2[x] + fileTypes[1] + "to default skin path")
                else:
                       if os.path.exists(fileNames2[x] + fileTypes[0]):
                           checked.append(fileNames2[x] + fileTypes[0])
                           print("Adding: " + fileNames2[x] + fileTypes[0] + "to default skin path")
                       elif os.path.exists(fileNames2[x] + fileTypes[1]):
                            checked.append(fileNames2[x] + fileTypes[1])
                            print("Adding: " + fileNames2[x] + fileTypes[1] + "to default skin path")
            ratey, y = read(checked[0])
            rate, z = read(checked[1])
            rateM, m = read(checked[2])
            ratesb, b = read(checked[3])
            ratesc, c = read(checked[4])
            rateS, s = read(checked[5])
            spinSound = AudioSegment.from_wav(checked[6])
        

            return rate,y,rate,z,rateM,m,ratesb,b,ratesc,c,rateS,s,spinSound



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


def processAudio(my_info,beatmap_info,skin_path,offset,default_skinP,beatmap_path,audio_name):
        rate,y,rate,z,rateM,m,ratesb,b,ratesc,c,rateS,s,spinSound = checkAudio(skin_path,default_skinP,beatmap_path,audio_name)
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
        for x in range(len(my_info)):
            start_index = int(my_info[x].time/1000 * rate)

            if type(my_info[x].more).__name__ == "Circle":
                spinSpeedup = 6
                if my_info[x].more.sliderhead == True:
                        
                        arrow_time_list = []
                        if len(sliderTime) > 0:
                            for a in range(repeatedTime[0]):
                                        arrow_time_list.append(sliderTime[0] + durationTime[0] * (a+1))
                            start_index2 = int(sliderTime[0]/1000 * rate)
                            z[start_index2:start_index2 + len(s)] += s * 0.5
                            for abc in arrow_time_list:
                                    start_index2 = int(abc/1000 * rate)
                                    z[start_index2:start_index2+ len(s)] += s * 0.5
                            
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
        offset = int(offset)
        write('z.mp3', rate, z[int(offset/1000*rate):int((len(z)/rate))*rate])
        
        end=time.time()
        print(end-start)
        
if __name__ == '__main__':
        res, beat = parseData()
        #args =(my_info,beatmap_info,skin_path,offset,default_skinP,beatmap_path,audio_name):
        processAudio(res, beat,"C:/Users/Shiho/Desktop/Projects/osr2mp4/src/AudioProcess/",27431.0,"C:/Users/Shiho/Downloads/Compressed/skin/","C:/Users/Shiho/Desktop/Projects/osr2mp4/src/AudioProcess/","Tengaku")


