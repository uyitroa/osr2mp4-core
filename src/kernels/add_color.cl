__kernel void add_color(__global const uchar* src, __global uchar* dst, int width, int pix, int blue, int green, int red) {

	const int y = get_global_id(0);
	const int x = get_global_id(1);

	const int index = y * width * pix + x * pix;
	dst[index] = src[index] * blue / 255.0;
	dst[index+1] = src[index+1] * green / 255.0;
	dst[index+2] = src[index+2] * red / 255.0;
	dst[index+3] = src[index+3];

}