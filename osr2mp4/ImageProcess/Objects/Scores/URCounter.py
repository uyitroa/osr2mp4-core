import numpy
from osr2mp4.CheckSystem.mathhelper import getunstablerate
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Animation.easing import easingout
from osr2mp4.ImageProcess.PrepareFrames.Components.Text import prepare_text
from osr2mp4.osrparse.enums import Mod
from PIL import Image


class URCounter:
    def __init__(self, settings: object, mods: object):
        self.settings = settings
        self.ur: int = 0
        self.real_ur: int = 0
        self.numbers: dict = {}
        self.timeframe = settings.timeframe / settings.fps
        self.mods = mods
        self.divide_by: float = 1.0

        # customizable things
        self.position: list = [
            settings.ppsettings.get('URCounter x', 675),
            settings.ppsettings.get('URCounter y', 720)
        ]
        self.origin: str = settings.ppsettings.get('URCounter Origin', 'center')

        self.get_divide()
        self.load_number()

    def get_divide(self):
        if Mod.DoubleTime in self.mods or Mod.Nightcore in self.mods:
            self.divide_by = 1.5
        
        if Mod.HalfTime in self.mods:
            self.divide_by = 0.75

    def load_number(self):
        numbers = [str(_) for _ in range(10)]
        numbers += ['.']
        numbers += [" "]
        
        frames = prepare_text(
            numbers, 
            25 * self.settings.scale,
            (255, 255, 255),
            self.settings,
            alpha = self.settings.ppsettings.get('URCounter Alpha', 1),
            fontpath = self.settings.ppsettings.get('URCounter Font', 'arial.ttf')
        )

        for index in frames:
            self.numbers[
                int(index) if index.isdigit() else index
            ] = frames[index]
        
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
        

        imageproc.draw_number(
            background,
            self.ur,
            self.numbers, 
            self.position[0] * self.settings.scale,
            self.position[1] * self.settings.scale,
            1,
            self.origin,
            0
        )

        
