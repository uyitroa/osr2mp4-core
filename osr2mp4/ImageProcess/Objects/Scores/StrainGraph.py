from osr2mp4.ImageProcess.Objects.FrameObject import FrameObject
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.PrepareFrames.YImage import YImage
from PIL import Image

class StrainGraph(FrameObject):
	def __init__(self, settings):
		self.settings = settings
		self.x = 110 * self.settings.scale
		self.y = 50 * self.settings.scale  
		self.alpha = 0.9
		self.scale = self.settings.scale * 0.25 # TODO: ALLOW CUSTOMIZATION

	def set_strain_graph(self, filename):
		strain_graph = Image.open(filename).convert("RGBA")
		self.graph = imageproc.change_size(strain_graph, self.scale, self.scale) # TODO: ALLOW CUSTOMIZATION OF SIZE
		return True

	def add_to_frame(self, background, cur_time):

		imageproc.add(self.graph, background, self.x, self.y, alpha=self.alpha)