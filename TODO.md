#Fix wrong game mechanics
- Wrong score
- Wrong hitresult, most likely because of slider 100s. watch dadada at 22th 100s. When key clicked and cursor is not in the slider, that key will not be counted in slider, so if the cursor move to the slider, it will not be counted.
- Unittest for judgement

#Implement features
- Add animation for sliderball, enable flip sliderball.
- Add animation for sliderfollow whenever touch slidertick
- Add default images for missing images in skin
- Add rotation for sliderb
- Add break time animation (shows background, pass/fail image)
- Add leaderboard
- Implement @x2 images for better result

#Optimisation
- Optimize newalpha() method in abstract class -> could potentially reduce a lot of execution time
- Optimize RAM Memory by reducing the amount of prepared frame
