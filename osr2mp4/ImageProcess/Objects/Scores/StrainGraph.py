from osr2mp4.ImageProcess.Objects.FrameObject import FrameObject
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.PrepareFrames.YImage import YImage
from PIL import Image

class StrainGraph(FrameObject):
	def __init__(self, settings, beatmap_start_time, beatmap_end_time):
		self.settings = settings
		self.x = 100 * self.settings.scale
		self.y = 150 * self.settings.scale  
		self.alpha = 0.85
		self.scale = self.settings.scale * 0.35 # TODO: ALLOW CUSTOMIZATION
		self.graph = None
		self.graph_pixel_access = None
		self.start_time = beatmap_start_time
		self.end_time = beatmap_end_time
		self.last_position = 0
		self.width, self.height = (0,0)
		self.progress_offset_ms = 1.5*1000

	def set_strain_graph(self, filename):
		strain_graph = Image.open(filename).convert("RGBA")
		self.graph = imageproc.change_size(strain_graph, self.scale, self.scale) # TODO: ALLOW CUSTOMIZATION OF SIZE
		self.graph_pixel_access = self.graph.load()
		self.width, self.height = self.graph.size
		return True

	def update_progress(self, cur_time):
		ratio = (self.progress_offset_ms+cur_time-self.start_time)/max(self.end_time-self.start_time, 1)
		progress = min(self.width, int(ratio*self.graph.size[0]))
		if( (progress >= 0) & (progress > self.last_position) ):
			self.set_graph_progress_opacity(self.last_position, progress, 200) # TODO: ALLOW CUSTOM COLOR
			self.last_position = progress

	def set_graph_progress_opacity(self, x0, x1, opacity):
		for y in range(self.height):
			for x in range(x0,x1):
				if self.graph_pixel_access[x, y][-1] > 0:
					pix = self.graph_pixel_access[x, y]
					self.graph_pixel_access[x, y] = (pix[0], pix[1], pix[2], opacity)

	def add_to_frame(self, background, cur_time):
		self.update_progress(cur_time)
		imageproc.add(self.graph, background, self.x, self.y, alpha=self.alpha)