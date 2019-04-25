import math
import numpy as np
from PIL import Image
from PIL import ImageDraw
import cv2


def convert(string, scale):
    string = string.split(",")
    ps = [[int(string[0]), int(string[1])]]
    slider_path = string[5]
    slider_path = slider_path.split("|")
    slider_path = slider_path[1:]

    for pos in slider_path:
        pos = pos.split(":")
        ps.append([int(int(pos[0]) * scale), int(int(pos[1]) * scale)])

        end_point = [int(pos[0]), int(pos[1])]

    pixel_length = float(string[7])
    return ps#, pixel_length, end_point


def pascal_row(n, memo={}):
    # This returns the nth row of Pascal's Triangle
    if n in memo:
        return memo[n]
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n//2+1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n&1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    memo[n] = result
    return result


def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n-1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier


if __name__ == '__main__':
    WIDTH, HEIGHT = 1920, 1080
    im = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    ts = [t/100.0 for t in range(101)]
    string = "88,100,0,2,0,B|158:2|424:158|140:382|88:100,1,475"
    playfield_width, playfield_height = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8
    scale = playfield_width / 512
    xys = convert(string, scale)
    bezier = make_bezier(xys)
    points = bezier(ts)

    draw.polygon(points, fill='red')
    im.save('out.png')