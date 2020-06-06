import numpy as np
from PIL import Image
from recordclass import recordclass

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end, break_index")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")


def get_buffer(img, settings):
	np_img = np.frombuffer(img, dtype=np.uint8)
	np_img = np_img.reshape((settings.height, settings.width, 4))
	pbuffer = Image.frombuffer("RGBA", (settings.width, settings.height), np_img, 'raw', "RGBA", 0, 1)
	pbuffer.readonly = False
	return np_img, pbuffer
