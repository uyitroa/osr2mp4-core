# Getting started
```python
from osr2mp4 import Osr2mp4

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

`"Process": n` means the amount of parallel computing. Theorically the more the faster. Usually 2-4 is fast and above that is slower.
 