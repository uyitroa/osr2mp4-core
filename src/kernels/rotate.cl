__kernel void rotate(__global const uchar * src, __global uchar * dest, const int width, const int height, const int pix, const float cos, const float sin) {

    const int x1 = get_global_id(0);
    const int y1 = get_global_id(1);

    const int x0 = (int)width/2;
    const int y0 = (int)height/2;

    int xPos = cos * (x1 - x0) - sin * (y1 - y0) + x0;
    int yPos = sin * (x1 - x0) + cos * (y1 - y0) + y0;

    if (xPos >= 0 && yPos >= 0 && xPos < width && yPos < height) {
        dest[x1 * width * pix + y1 * pix] = src[xPos * width * pix + yPos * pix];
        dest[x1 * width * pix + y1 * pix + 1] = src[xPos * width * pix + yPos * pix + 1];
        dest[x1 * width * pix + y1 * pix + 2] = src[xPos * width * pix + yPos * pix + 2];
        dest[x1 * width * pix + y1 * pix + 3] = src[xPos * width * pix + yPos * pix + 3];
    }
}