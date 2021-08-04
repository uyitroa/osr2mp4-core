from PIL import Image
import numpy as np

from osr2mp4.osrparse.enums import Mod
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Animation.easing import easingout
from osr2mp4.ImageProcess.Objects.Scores.ACounter import ACounter

class URCounter(ACounter):
    def __init__(self, settings: object, mods: Mod = [Mod.NoMod]):
        super().__init__(settings, settings.ppsettings, prefix='URCounter')
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

    def draw_number(self, background: Image):
        x = self.countersettings.get('x', 675) * self.settings.scale
        y = self.countersettings.get('y', 710) * self.settings.scale
        origin = self.countersettings.get('Origin', 'right')

        imageproc.draw_number(background, self.ur, self.frames, x, y, self.countersettings.get('Alpha', 1), origin=origin, gap=0)

    def update_ur(self, error_time: list):
        if len(error_time) == 0: return

        self.real_ur = np.std(error_time) / self.divide_by
        ur = float(self.ur)
        change = self.real_ur - ur
        ur = easingout(self.timeframe, ur, change, 100)
        self.ur = '{:.2f}'.format(ur)

    def add_to_frame(self, background: Image, alpha: int = 1):
        # change alpha; abit of a hack but eh /shrug
        self.countersettings['Alpha'] = alpha
        super().add_to_frame(background)
        

