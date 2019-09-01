__kernel void downsample(__global const uchar* image, __global uchar* outputImage, int width, int height, int pix, int target_width, int target_height){

	const int x = get_global_id(0);
	const int y = get_global_id(1);

	uchar q11, q12, q21, q22;

	const float ratio_x = (float)width/target_width;
	const float ratio_y = (float)height/target_height;

	const float accurate_y = (float)y*ratio_y;
	const int oly = (int)accurate_y;
	const int ohy = min(oly+1, height-1);

	const float accurate_x = (float)x*ratio_x;
	const int olx = (int)accurate_x;
	const int ohx = min(olx+1, width-1);

	const int index = x * target_width * pix + y * pix;
	for(int k=0; k<pix; k++){
		q11 = image[olx * width * pix + oly * pix + k];
		q12 = image[ohx * width * pix + oly * pix + k];
		q21 = image[olx * width * pix + ohy * pix + k];
		q22 = image[ohx * width * pix + ohy * pix + k];
		outputImage[index + k] = (uchar)(q11*(ohy - accurate_y)*(ohx - accurate_x) +
										q21*(accurate_y - oly)*(ohx - accurate_x) +
										q12*(ohy - accurate_y)*(accurate_x - olx) +
										q22*(accurate_y - oly)*(accurate_x - olx));
  }
}