class Info:
	def __init__(self, time, combo, combostatus, showscore, score, accuracy, clicks, hitresult, timestamp, idd, more):
		self.more = more
		self.timestamp = timestamp
		self.hitresult = hitresult
		self.clicks = clicks
		self.accuracy = accuracy
		self.score = score
		self.showscore = showscore
		self.combostatus = combostatus
		self.combo = combo
		self.time = time
		self.idd = idd


class Circle:
	def __init__(self, state, deltat, followstate):
		self.state = state
		self.deltat = deltat
		self.followstate = followstate


class Slider:
	def __init__(self, followstate, hitvalue, combostatus, tickend):
		self.followstate = followstate
		self.hitvalue = hitvalue
		self.combostatus = combostatus
		self.tickend = tickend


class Spinner:
	def __init__(self, rotate, progress, bonusscore, hitvalue):
		self.rotate = rotate
		self.progress = progress
		self.bonusscore = bonusscore
		self.hitvalue = hitvalue
