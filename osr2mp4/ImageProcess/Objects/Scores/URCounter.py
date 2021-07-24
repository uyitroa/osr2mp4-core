from osr2mp4.CheckSystem.mathhelper import getunstablerate
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

        # customizable things
        self.position: list = [
            settings.ppsettings.get('URCounter x', 675),
            settings.ppsettings.get('URCounter y', 720)
        ]

        self.get_divide()

    def get_divide(self):
        if Mod.DoubleTime in self.mods or Mod.Nightcore in self.mods:
            self.divide_by = 1.5
        
        if Mod.HalfTime in self.mods:
            self.divide_by = 0.75

    def add_to_frame(self, background: Image, result_info: object, time: int = 0):
        self.real_ur = getunstablerate(result_info, time)[2] / self.divide_by
        ur = float(self.ur)
        
        change = self.real_ur - ur
        ur = easingout(
            self.timeframe,
            ur,
            change,
            500
        )

        self.ur = '{:.2f}'.format(ur)
        self.score = self.ur
        super().add_to_frame(background)
        

