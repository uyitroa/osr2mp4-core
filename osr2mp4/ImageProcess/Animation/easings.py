import math


''' 
	Easing shit - FireRedz
	copied from my storyboard renderer which is copied from some random gist
	
	t is the current time (or position) of the tween.
	b is the beginning value of the property.
	c is the change between the beginning and destination value of the property. | basically destination-start
	d is the total time of the tween.
'''

def easeLinear(t, b, c, d):
	return c*t/d + b

def easeInQuad(t, b, c, d):
	t /= d
	return c*t*t + b


def easeOutQuad(time, initial, change, duration):
	t = time/duration
	return -change * (t * (t-2)) + initial

def easeInOutQuad(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t + b
	t-=1
	return -c/2 * (t*(t-2) - 1) + b


def easeInOutCubic(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t*t + b
	t -= 2
	return c/2*(t*t*t + 2) + b

def easeInQuart(t, b, c, d):
	t /= d
	return c*t*t*t*t + b

def easeOutQuart(t, b, c, d):
	t /= d
	t -= 1
	return -c * (t*t*t*t - 1) + b

def easeInOutQuart(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t*t*t + b
	t -= 2
	return -c/2 * (t*t*t*t - 2) + b

def easeInQuint(t, b, c, d):
	t /= d
	return c*t*t*t*t*t + b

def easeOutQuint(t, b, c, d):
	t /= d
	t -= 1
	return c*(t*t*t*t*t + 1) + b

def easeInOutQuint(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t*t*t*t + b
	t -= 2
	return c/2*(t*t*t*t*t + 2) + b

def easeInSine(t, b, c, d):
	return -c * math.cos(t/d * (math.pi/2)) + c + b

def easeOutSine(t, b, c, d):
	return c * math.sin(t/d * (math.pi/2)) + b


def easeInOutSine(t, b, c, d):
	return -c/2 * (math.cos(math.pi*t/d) - 1) + b

def easeInExpo(t, b, c, d):
	return c * math.pow( 2, 10 * (t/d - 1) ) + b

def easeOutExpo(t, b, c, d):
	return c * ( -math.pow( 2, -10 * t/d ) + 1 ) + b


def easeInOutExpo(t, b, c, d):
	t /= d/2
	if t < 1: 
		return c/2 * math.pow( 2, 10 * (t - 1) ) + b
	t -= 1
	return c/2 * ( -math.pow( 2, -10 * t) + 2 ) + b

def easeInCirc(t, b, c, d):
	t /= d
	return -c * (math.sqrt(1 - t*t) - 1) + b

def easeOutCirc(t, b, c, d):
	t /= d
	t -= 1
	return c * math.sqrt(1 - t*t) + b

def easeInOutCirc(t, b, c, d):
	t /= d/2
	if t < 1:
		return -c/2 * (math.sqrt(1 - t*t) - 1) + b
	t -= 2
	return c/2 * (math.sqrt(1 - t*t) + 1) + b


def easeInElastic(t, b, c, d):
	s = 1.70158
	a = c

	if t == 0:
		return b
	t /= d
	if t == 1:
		return b + c

	p = d * 0.3
	if a < abs(c):
		a = c
		s = p / 4
	else:
		s = p / (2 * math.pi) * math.asin(c / a)

	t -= 1
	return -(a * pow(2, 10 * t) * math.sin((t * d - s) * (2 * math.pi) / p)) + b

def easeOutElastic(t, b, c, d):
	s, a = 1.70158, c

	if t == 0:
		return b
	t /= d
	if t == 1:
		return b + c

	p = d * 0.3
	if a < abs(c):
		a, s = c, p / 4
	else:
		s = p / (2 * math.pi) * math.asin(c / a)

	return a * pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p) + c + b

def easeInOutElastic(t, b, c, d):
	s, a = 1.70158, c

	if t == 0:
		return b
	t /= (d / 2)
	if t == 2:
		return b + c

	p = d * (0.3 * 1.5)
	if a < abs(c):
		a, s = c, p / 4
	else:
		s = p / (2 * math.pi) * math.asin(c / a)

	if t < 1:
		t -= 1
		return -0.5 * (a * pow(2, 10 * t) * math.sin((t * d - s) * (2 * math.pi) / p)) + b

	t -= 1
	return a * pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p ) * 0.5 + c + b

def easeInBack(t, b, c, d, s = 1.70158):
	t /= d
	return c * t * t * ((s + 1) * t - s) + b

def easeOutBack(t, b, c, d, s = 1.70158):
	t = t / d - 1
	return c * (t * t * ((s + 1) * t + s) + 1) + b

def easeInOutBack(t, b, c, d, s = 1.70158):
	t /= d / 2
	s *= 1.525
	if t < 1:
		return c / 2 * (t * t * ((s + 1) * t - s)) + b

	t -= 2
	return c/2 * (t * t * ((s + 1) * t + s) + 2) + b

def easeInBounce(t, b, c, d):
		return c - easeOutBounce(d-t, 0, c, d) + b

def easeOutBounce(t, b, c, d):
	t /= d
	if t < (1/2.75):
		return c*(7.5625*t*t) + b

	elif t < (2/2.75):
		t -= (1.5/2.75)
		return c*(7.5625*t*t + 0.75) + b

	elif t < (2.5/2.75):
		t -= (2.25/2.75)
		return c*(7.5625*t*t + 0.9375) + b

	else:
		t -= (2.625/2.75)
		return c*(7.5625*t*t + 0.984375) + b

def easeInOutBounce(t, b, c, d):
	if t < d/2:
		return easeInBounce(t*2, 0, c, d) * .5 + b

	return easeOutBounce(t*2-d, 0, c, d) * .5 + c*.5 + b

