import math

import cv2

from ... import imageproc


class TimePie:
	def __init__(self, accuracy, starttime, endtime, scorebarbg, settings):
		# need to initalize this right after initializing accuracy class
		self.settings = settings
		self.scale = self.settings.scale
		self.y = int(accuracy.y + accuracy.frames[0].size[1]//2)
		self.radius = int(15 * self.settings.scale)
		# frames[10[ is percent
		accsize = (-accuracy.sizegap) * 6 + accuracy.frames[11].size[0] - accuracy.gap
		self.x = int(accuracy.startx - accuracy.frames[10].size[0] - accsize - self.radius)

		self.starttime = starttime
		self.endtime = endtime

		extended = self.radius * math.sqrt(2)
		self.overlayimg = scorebarbg[0].crop((self.x - extended, self.y - extended, self.x + extended, self.y + extended))

	def add_to_frame(self, np_img, background, cur_time, scorebarh, scorebaralpha, inbreak):
		ratio = (cur_time-self.starttime)/max(self.endtime-self.starttime, 1)
		color = (125, 125, 125, 255)
		if ratio < 0:
			color = (80, 125, 80, 255)
		angle = 270
		startangle = -360 + ratio * 360
		endangle = -360
		axes = (self.radius, self.radius)

		if self.settings.settings["In-game interface"] or inbreak:
			cv2.ellipse(np_img, (self.x, self.y), axes, angle, startangle, endangle, color, -1, cv2.LINE_AA)
			cv2.circle(np_img, (self.x, self.y), self.radius, (255, 255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
			cv2.circle(np_img, (self.x, self.y), max(1, int(self.scale)), (255, 255, 255, 255), thickness=-1, lineType=cv2.LINE_AA)

			imageproc.add(self.overlayimg, background, self.x, self.y - scorebarh, alpha=scorebaralpha)
