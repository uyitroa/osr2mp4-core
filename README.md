# Installing
```
cd src/
python setup.py
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


### Download the default skin link
https://osu.ppy.sh/community/forums/topics/129191?start=2997865


### Setup config
Setup path for skin, beatmap, replay, default skin and ffmpeg in `src/config.json`


`"Start time": 0, "End time": 60` means it will only convert the first minute of the replay.
Set `"End time"` to -1 if you want to convert full replay.

`"Process": 2` means the program will use 2 processes to convert so it will be faster than just 1.
Use `"Process": 0` if you don't want parallel computing.

