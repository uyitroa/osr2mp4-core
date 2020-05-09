import cv2


class TimePie:
	def __init__(self, scale, accuracy):
		# need to initalize this right after initializing accuracy class
		self.scale = scale
		self.y = int(accuracy.y + accuracy.frames[0].size[1]//2)
		# frames[10[ is percent
		size = accuracy.frames[1].size[0] + (accuracy.frames[0].size[0] - accuracy.gap) * 4 + accuracy.frames[11].size[0] - accuracy.gap
		self.x = int(accuracy.width * 0.99 - accuracy.frames[10].size[0] - size)

	def add_to_frame(self, background, cur_time, end_time):
		ratio = cur_time/end_time
		angle = 270
		startangle = -360 + ratio * 360
		endangle = -360
		radius = int(12.5 * self.scale)
		axes = (radius, radius)
		cv2.ellipse(background, (self.x, self.y), axes, angle, startangle, endangle, (125, 125, 125, 255), -1, cv2.LINE_AA)
		cv2.circle(background, (self.x, self.y), radius, (255, 255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
		cv2.circle(background, (self.x, self.y), min(1, int(self.scale)), (255, 255, 255, 255), thickness=-1, lineType=cv2.LINE_AA)
