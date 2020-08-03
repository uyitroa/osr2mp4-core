from ccurves import create_curve, get_pos_at
#from osr2mp4.ImageProcess.Curves.generate_slider import GenerateSlider
#import numpy as np
#import cv2
for x in range(10000):
	#b, f = create_curve("L", [[172, 289], [230, 281]], 45)
	b,f = create_curve("B", [[294, 109], [192, 35], [39, 49], [39, 49], [48, 154], [123, 263], [123, 263], [152, 127], [279, 6], [279, 6], [401, 70], [447, 126], [476, 260], [450, 365], [450, 365], [366, 316], [341, 204], [341, 204], [308, 217], [236, 180]], 1550)
#b = create_curve("B", [[157, 43], [481, 27], [462, 304], [39, 331], [61, 38], [451, 36], [51, 178]], 620)
#g = GenerateSlider([200, 200, 50], [20, 10, 20], 36, 0.9)

#c = np.int32(b)

	for x in range(0, int(f[-1])+10, 10):
	#g.draw(c)
		pos = get_pos_at(b, f, x)
	#pos[0] = int(pos[0])
	#pos[1] = int(pos[1])
	#g.img[pos[1]-2:pos[1]+2, pos[0]-2:pos[0]+2, :] = [255, 255, 255, 255]
	#cv2.imwrite(f"test{x}.png", g.img)
