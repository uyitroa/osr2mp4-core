from osr2mp4.CheckSystem.mathhelper import getunstablerate
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Animation.easing import easingout
from osr2mp4.ImageProcess.Objects.Scores.ACounter import ACounter
from osr2mp4.osrparse.enums import Mod
from PIL import Image


class URCounter(ACounter):
    def __init__(self, settings: object, mods: object):
        super().__init__(settings, settings.ppsettings, prefix='URCounter ')
        self.ur: int = 0
        self.real_ur: int = 0
        self.mods = mods
        self.timeframe = settings.timeframe / settings.fps
        self.divide_by: float = 1.0

        self.get_divide()

    def get_divide(self):
        if Mod.DoubleTime in self.mods or Mod.Nightcore in self.mods:
            self.divide_by = 1.5
        
        if Mod.HalfTime in self.mods:
            self.divide_by = 0.75

    def draw_number(self, background):
        x = self.countersettings['URCounter x'] * self.settings.scale
        y = self.countersettings['URCounter y'] * self.settings.scale
        origin = self.countersettings.get('URCounter Origin', 'right')

        imageproc.draw_number(background, self.ur, self.frames, x, y, self.countersettings[self.prefix + 'Alpha'], origin=origin, gap=0)

    def add_to_frame(self, background: Image, result_info: object, time: int = 0):
        self.real_ur = getunstablerate(result_info, time)[2] / self.divide_by

        ur = float(self.ur)
        change = self.real_ur - ur
        ur = easingout(self.timeframe, ur, change, 500)

        self.ur = '{:.2f}'.format(ur)
        super().add_to_frame(background)
        

