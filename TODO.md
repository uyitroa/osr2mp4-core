# Fix wrong game mechanics
- Wrong score
- Wrong hitresult, most likely because of slider 100s. watch dadada at 22th 100s. When key clicked and cursor is not in the slider, that key will not be counted in slider, so if the cursor move to the slider, it will not be counted.
- Unittest for judgement
- Combo doesn't break sometimes
- Sliderheads don't have notelock
- Sliderfollow disappear immediatly if cursor goes out

# Implement features
- Add animation for sliderball, enable flip sliderball.
- Add animation for sliderfollow whenever touch slidertick
- Add default images for missing images in skin
- Add rotation for sliderb
- Add break time animation (shows background, pass/fail image)
- Add leaderboard
- Implement @x2 images for better result
- Bezier tolerance depends on the size of the slider
- Add continuos cursortrail (cursormiddle)
- Score each digit keep changing until that biggest digit get to the real score digit
- Add mods (HR, DT, HD, EZ)
- Skin default

# Optimisation
- Avoid redrawing unchanged image to reduce execution time. (Slider body, Spinner background, Button, Score can be redrawn less often)
- Pattern search for sliderbody, so instead of storing multiple same slider body, just need to store one. Reduce preparing time and ram memory
