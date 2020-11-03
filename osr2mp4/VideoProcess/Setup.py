import numpy as np
from PIL import Image
from recordclass import recordclass

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end, break_index")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")


def get_buffer(img, settings):
	np_img = img.reshape((settings.height, settings.width, 4))
	pbuffer = Image.fromarray(np_img, "RGBA")
	pbuffer.readonly = False
	return np_img, pbuffer
