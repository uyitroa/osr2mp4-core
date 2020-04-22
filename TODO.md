# Fix wrong game mechanics
- Wrong score
- Wrong hitresult, most likely because of slider 100s. watch dadada at 22th 100s. When key clicked and cursor is not in the slider, that key will not be counted in slider, so if the cursor move to the slider, it will not be counted.
- Unittest for judgement

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

# Optimisation
- Optimize RAM Memory by reducing the amount of prepared frame
- Avoid redrawing unchanged image to reduce execution time. (Slider body, Spinner background, Button, Score can be redrawn less often)
- Delete uunsed prepared frames
- Pattern search for sliderbody, so instead of storing multiple same slider body, just need to store one. Reduce preparing time and ram memory
- Converting Pillow Image to numpy array is using too much time
- Convert slider body images to pillow class later to reduce ram memory? to test

# Clean up code
- All class must be independent from each others
- Add comment
- add_to_frame of Circle and Slider and prepare_frame of Circle are too complicated. Need to refactor them
