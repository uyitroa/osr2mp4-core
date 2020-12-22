# Installing
```
cd osr2mp4/
python install.py
pip install cython
cd ImageProcess/Curves/libcurves/
python setup.py build_ext --inplace
```

To enable ffmpeg video writer:
```
cd VideoProcess/FFmpegWriter/
python setup build_ext --inplace
```


Then

### Pillow-SIMD
Download Pillow-SIMD here
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow-simd

Install pillow-simd
`pip install download-file.whl`

### ffmpeg
Download ffmpeg here:
https://www.ffmpeg.org/download.html#build-windows


### Setup config
Setup path for skin, beatmap, replay, default skin and ffmpeg in `osr2mp4/config.json`


`"Start time": 0, "End time": 60` means it will only convert the first minute of the replay.
Set `"End time"` to -1 if you want to convert full replay.

`"Process": 2` means the program will use 2 processes to convert so it will be faster than just 1.
Use `"Process": 0` if you don't want parallel computing.

To render an auto replay, put "auto" in the osr path, and put .osu path in the Beatmap path.
To select a custom mods for replays and auto, put your mods in the "Custom mods" in settings.json. Example: "Custom mods": "HDHR".

### Run tests
```
osr2mp4-core$ python -m unittest discover -s tests -p '*test.py'
```


# Getting started with osr2mp4 library
```python
from osr2mp4.osr2mp4 import Osr2mp4

data = {
   "osu! path": "/Users/yuitora./osu!/",
   "Skin path": "/Users/yuitora./osu!/Skins/-#Whitecat#-",
   "Beatmap path": "/Users/yuitora./osu!/Songs/123456 Hachigatsu, Bou/",
   ".osr path": "/Users/yuitora./osu!/Replays/yuitora_12317423.osr",
   "Default skin path": "/Users/yuitora./Downloads/Default Skin/",
   "Output path": "output.avi",
   "Width": 1920,
   "Height": 1080,
   "FPS": 60,
   "Start time": 0,
   "End time": -1,
   "Video codec": "XVID",
   "Process": 2,
   "ffmpeg path": "Users/yuitora./ffmpeg/bin/ffmpeg.exe"
 }

settings = {
   "Cursor size": 1,
   "In-game interface": True,
   "Show scoreboard": True,
   "Background dim": 90,
   "Always show key overlay": True,
   "Automatic cursor size": False,
   "Rotate sliderball": False,
   "Score meter size": 1.25,
   "Song volume": 50,
   "Effect volume": 100,
   "Ignore beatmap hitsounds": True,
   "Use skin's sound samples": True,
   "Global leaderboard": False,
   "Mods leaderboard": "(HD)HR",
   "api key": "lol"
 }

converter = Osr2mp4(data, settings)
converter.startall()
converter.joinall()
```
 
 Or you can save `data` and `settings` in a json file.
 config.json:
```json
  {
   "osu! path": "/Users/yuitora./osu!/",
   "Skin path": "/Users/yuitora./osu!/Skins/-#Whitecat#-",
   "Beatmap path": "/Users/yuitora./osu!/Songs/123456 Hachigatsu, Bou/",
   ".osr path": "/Users/yuitora./osu!/Replays/yuitora_12317423.osr",
   "Default skin path": "/Users/yuitora./Downloads/Default Skin/",
   "Output path": "output.avi",
   "Width": 1920,
   "Height": 1080,
   "FPS": 60,
   "Start time": 0,
   "End time": -1,
   "Video codec": "XVID",
   "Process": 2,
   "ffmpeg path": "Users/yuitora./ffmpeg/bin/ffmpeg.exe"
 }
```
 
 settings.json:
```json
 {
   "Cursor size": 1,
   "In-game interface": true,
   "Show scoreboard": true,
   "Background dim": 90,
   "Always show key overlay": true,
   "Automatic cursor size": true,
   "Rotate sliderball": false,
   "Score meter size": 1.25,
   "Song volume": 50,
   "Effect volume": 100,
   "Ignore beatmap hitsounds": true,
   "Use skin's sound samples": true,
   "Global leaderboard": false,
   "Mods leaderboard": "(HD)HR",
   "api key": "lol"
 }
```
 
 And to load it in code
```python
from osr2mp4.osr2mp4 import Osr2mp4
converter = Osr2mp4(filedata="config.json", filesettings="settings.json")
converter.startall()
converter.joinall()
```

 ### Others shits
 All available settings are [here](https://github.com/uyitroa/osr2mp4-core/blob/master/osr2mp4/global_var.py#L6) and explanations of settings [here](https://github.com/uyitroa/osr2mp4-app/blob/master/langs/en/tooltips.json)
 
 
 
 `Osr2mp4.startvideo()`
 
 Start video without audio.
 
 `Osr2mp4.joinvideo()`
 
 Wait for video to finish.
 
 `Osr2mp4.startaudio()`
 
 Start audio.
 
 `Osr2mp4.joinaudio()`
 
 Wait for audio to finish.
 
 `Osr2mp4.startall()`
 
 Start video and audio.
 
 `Osr2mp4.joinall()`
 
 Wait for all to finish.
 
 `Osr2mp4.getprogress()`
 
 Return a value from 0 to 100 corresponding to the estimated progress of the conversion.
