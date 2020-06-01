# Fix wrong game mechanics

# Implement features
- Add option to animate sliderball (this can be optimised)
- Add rank number to scoreboard

# Optimisation
- Avoid redrawing unchanged image to reduce execution time. (Slider body, Spinner background, Button, Score can be redrawn less often)
- Pattern search for sliderbody, so instead of storing multiple same slider body, just need to store one. Reduce preparing time and ram memory
- paste without mask if no overlay
