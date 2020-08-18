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

