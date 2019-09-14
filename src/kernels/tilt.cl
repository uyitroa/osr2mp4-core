__kernel void rot90(__global const uchar* src, __global uchar* dst, int width, int height, int pix) {

    const int y = get_global_id(0);
    const int x = get_global_id(1);

    dst[x * height * pix + (height - y - 1) * pix] = src[y * width * pix + x * pix];
    dst[x * height * pix + (height - y - 1) * pix + 1] = src[y * width * pix + x * pix + 1];
    dst[x * height * pix + (height - y - 1) * pix + 2] = src[y * width * pix + x * pix + 2];
    dst[x * height * pix + (height - y - 1) * pix + 3] = src[y * width * pix + x * pix + 3];
}


__kernel void rot180(__global const uchar* src, __global uchar* dst, int width, int height, int pix) {

	const int y = get_global_id(0);
	const int x = get_global_id(1);

    dst[y * width * pix + (width - x - 1) * pix] = src[y * width * pix + x * pix];
    dst[y * width * pix + (width - x - 1) * pix + 1] = src[y * width * pix + x * pix + 1];
    dst[y * width * pix + (width - x - 1) * pix + 2] = src[y * width * pix + x * pix + 2];
    dst[y * width * pix + (width - x - 1) * pix + 3] = src[y * width * pix + x * pix + 3];
}


__kernel void rot270(__global const uchar* src, __global uchar* dst, int width, int height, int pix) {

    const int y = get_global_id(0);
    const int x = get_global_id(1);

    dst[(width - x - 1) * height * pix + y * pix] = src[y * width * pix + x * pix];
    dst[(width - x - 1) * height * pix + y * pix + 1] = src[y * width * pix + x * pix + 1];
    dst[(width - x - 1) * height * pix + y * pix + 2] = src[y * width * pix + x * pix + 2];
    dst[(width - x - 1) * height * pix + y * pix + 3] = src[y * width * pix + x * pix + 3];
}