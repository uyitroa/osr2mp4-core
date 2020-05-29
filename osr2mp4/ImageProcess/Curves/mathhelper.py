import math

def clamp(value, mn, mx):
    return min(max(mn, value), mx)

def sign(value):
    if value == 0:
        return 0
    elif value > 0:
        return 1
    else:
        return -1

def cpn(p, n):
    if p < 0 or p > n:
        return 0
    p = min(p, n - p)
    out = 1
    for i in range(1, p + 1):
        out = out * (n - p + i) / i

    return out

def catmull(p, t): # WARNING:   Worst math formula incomming
    return 0.5 * (
        (2 * p[1]) +
        (-p[0] + p[2]) * t +
        (2 * p[0] - 5 * p[1] + 4 * p[2] - p[3]) * pow(t, 2) +
        (-p[0] + 3 * p[1] - 3 * p[2] + p[3]) * pow(t, 3))

def point_on_line(p0, p1, length):
    full_length = pow(pow(p1.x - p0.x, 2) + pow(p1.y - p0.y, 2), 0.5)
    n = full_length - length

    x = (n * p0.x + length * p1.x) / full_length
    y = (n * p0.y + length * p1.y) / full_length
    return Vec2(x, y)

def angle_from_points(p0, p1):
    return math.atan2(p1.y - p0.y, p1.x - p0.x)

def distance_from_points(array):
    distance = 0

    for i in range(1, len(array)):
        distance += array[i].distance(array[i - 1])

    return distance

def cart_from_pol(r, t):
    x = (r * math.cos(t))
    y = (r * math.sin(t))

    return Vec2(x, y)

def point_at_distance(array, distance): #TODO: Optimize...
    i = 0
    current_distance = 0
    new_distance = 0

    if len(array) < 2:
        return Vec2(0, 0)

    if distance == 0:
        return array[0]

    if distance_from_points(array) <= distance:
        return array[len(array) - 1]

    for i in range(len(array) - 2):
        x = (array[i].x - array[i + 1].x)
        y = (array[i].y - array[i + 1].y)

        new_distance = math.sqrt(x * x + y * y)
        current_distance += new_distance

        if distance <= current_distance:
            break

    current_distance -= new_distance

    if distance == current_distance:
        return array[i]
    else:
        angle = angle_from_points(array[i], array[i + 1])
        cart = cart_from_pol((distance - current_distance), angle)

        if array[i].x > array[i + 1].x:
            coord = Vec2((array[i].x - cart.x), (array[i].y - cart.y))
        else:
            coord = Vec2((array[i].x + cart.y), (array[i].y + cart.y))

        return coord

class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return pow(x*x + y*y, 0.5)  #sqrt, lol

    def calc(self, value, other):   #I dont know what to call this function yet
        x = self.x + value * other.x
        y = self.y + value * other.y
        return Vec2(x, y)
