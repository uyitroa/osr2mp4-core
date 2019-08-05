class Test:
	a = 1
	def __init__(self):
		self.b = 2

class Nope(Test):
	def __init__(self):
		self.b = 3
		print(self.a)
n = Nope()
