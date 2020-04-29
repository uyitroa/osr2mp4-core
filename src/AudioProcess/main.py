from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from collections import namedtuple
import time
start=time.time()


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

ratey, y = read('hit1.wav')
rate, z = read('Tengaku.mp3')
rateM, m = read('miss1.wav')
ratesb, b = read('spinnerbonus.wav')
ratesc, c = read('spinnerspin.wav')

spinBonusTime = 0
spinRotationTime = 0
length_bonus = ratesb/len(b)
length_spin = ratesc/len(c)
for x in range(len(my_info)):
    start_index = int(my_info[x].time/1000 * rate)

    if not type(my_info[x].more).__name__ == "Spinner":
        if my_info[x].hitresult == None:
                continue
        if my_info[x].hitresult == 0:
                z[start_index:start_index + len(m)] += m * 0.5

        if my_info[x].hitresult > 0:
                z[start_index:start_index + len(y)] += y * 0.5

    elif type(my_info[x].more).__name__ == "Spinner":

        if int(my_info[x].more.rotate) >= 180:
            if my_info[x].time/1009 < spinRotationTime:
                pass
            else:
                z[start_index:start_index + len(c)] += c * 0.5
                spinRotationTime = my_info[x].time/1000 + length_spin

        if my_info[x].more.bonusscore  > 0:
            if my_info[x].time/1000 < spinBonusTime:
                continue
            else:
                z[start_index:start_index + len(b)] += b * 0.5
                spinBonusTime = my_info[x].time/1000 + length_bonus


write('out.wav', rate, z)

end=time.time()
print(end-start)
az = AudioSegment.from_wav("out.wav")
az.export("out.mp3",format="mp3")
