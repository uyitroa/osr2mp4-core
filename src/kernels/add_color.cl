__kernel void add_color(__global uchar* image, int width, int height, int pix, int blue, int green, int red){

	const int x = get_global_id(0);
	const int y = get_global_id(1);

	const int index = x * width * pix + y * pix;
	image[index] *= blue / 255.0;
	image[index+1] *= green / 255.0;
	image[index+2] *= red / 255.0;

}