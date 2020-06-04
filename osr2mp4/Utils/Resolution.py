def get_screensize(width, height):
	playfield_scale = 595.5/768  # source: https://www.reddit.com/r/osugame/comments/4pz8nr/how_to_click_beside_circles_in_osu_and_get_300/
	playfield_height = height * playfield_scale  # actual playfield is smaller than screen res
	playfield_width = playfield_height * 4/3
	scale = height / 768
	playfield_scale *= scale * 2  # don't ask
	move_right = round((width-playfield_width)/2.1)  # center the playfield
	move_down = round((height-playfield_height)/1.9)
	return playfield_scale, playfield_width, playfield_height, scale, move_right, move_down

