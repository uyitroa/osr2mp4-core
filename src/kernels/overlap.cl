__kernel void overlap_scalar(__global uchar * src, const int width, const int height, const int pix, const int x_offset, const int y_offset, const int r, const int g, const int b, const int a) {

    const int y1 = get_global_id(0) + y_offset;
    const int x1 = get_global_id(1) + x_offset;

    src[y1 * width * pix + x1 * pix] = b;
    src[y1 * width * pix + x1 * pix + 1] = g;
    src[y1 * width * pix + x1 * pix + 2] = r;
    src[y1 * width * pix + x1 * pix + 3] = a;
}