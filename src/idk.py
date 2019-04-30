from position import *
def convert(string):
	string = string.split(",")
	p_start = Position(int(string[0]), int(string[1]))

	slider_path = string[5]
	slider_path = slider_path.split("|")
	slider_path = slider_path[1:]
	
	ps = [p_start]
	for pos in slider_path:
		pos = pos.split(":")
		ps.append(Position(int(pos[0]), int(pos[1])))
		end_point = [int(pos[0]), int(pos[1])]
	
	pixel_length = float(string[7])
	return ps, pixel_length, end_point

