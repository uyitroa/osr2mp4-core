//__kernel void resize(__global const uchar* image, __global uchar* outputImage, int width, int height, int pix, int target_width, int target_height) {
//        const int y = get_global_id(0);
//        const int x = get_global_id(1);
//        const int z = get_global_id(2);
//
//        const float ratio_x = (float)width/target_width;
//        const float ratio_y = (float)height/target_height;
//
//        const float accurate_y = (float)y*ratio_y;
//        const int oly = (int)accurate_y;
//        const int ohy = min(oly+1, height-1);
//
//        const float accurate_x = (float)x*ratio_x;
//        const int olx = (int)accurate_x;
//        const int ohx = min(olx+1, width-1);
//
//        uchar p = image[ohy * width * pix + ohx * pix + z];
//
//        uchar p1 = image[(ohy - 1) * width * pix + ohx * pix + z];      /* neighbour to the North */
//        uchar p2 = image[ohy * width * pix + (ohx - 1) * pix + z];      /* neighbour to the West */
//        uchar p3 = image[(ohy - 1) * width * pix + (ohx - 1) * pix + z];  /* neighbour to the North-West */
//
//        uchar d1 = abs_diff(p, p1);
//        uchar d2 = abs_diff(p, p2);
//        uchar d3 = abs_diff(p, p3);
//        uchar d4 = abs_diff(p1, p2);        /* North to West */
//
//        uchar mini = d1;
//        if (mini > d2) mini = d2;
//        if (mini > d3) mini = d3;
//        if (mini > d4) mini = d4;
//
//        float av;
//        if (mini == d1) {
//                av = (float)0.5f * (p + p1);
//        } else if (mini == d2) {
//                av = (float)0.5f * (p + p2);
//        } else if (mini == d3) {
//                av = (float)0.5f * (p + p3);
//        } else /* mini == d4 */{
//                av = (float)0.5f * (p + 0.5f * (p + p2));
//        }
//        outputImage[y * target_width * pix + x * pix + z] = (uchar)av;
//}

__kernel void scale_down(__global const uchar* image, __global uchar* outputImage, int width, int height, int pix, int target_width, int target_height) {

	const int y = get_global_id(0);
	const int x = get_global_id(1);
	const int k = get_global_id(2);

	uchar q11, q12, q21, q22;

	const float ratio_x = (float)width/target_width;
	const float ratio_y = (float)height/target_height;

	const float accurate_y = (float)y*ratio_y;
	const int oly = (int)accurate_y;
	const int ohy = min(oly+1, height-1);

	const float accurate_x = (float)x*ratio_x;
	const int olx = (int)accurate_x;
	const int ohx = min(olx+1, width-1);

	const int index = y * target_width * pix + x * pix;

    q11 = image[oly * width * pix + olx * pix + k];
    q12 = image[ohy * width * pix + olx * pix + k];
    q21 = image[oly * width * pix + ohx * pix + k];
    q22 = image[ohy * width * pix + ohx * pix + k];
    outputImage[index + k] = (uchar)(q11*(ohy - accurate_y)*(ohx - accurate_x) +
                                    q21*(accurate_y - oly)*(ohx - accurate_x) +
                                    q12*(ohy - accurate_y)*(accurate_x - olx) +
                                    q22*(accurate_y - oly)*(accurate_x - olx));
}



// for less than 2x
__kernel void scale_up(__global const uchar* image, __global uchar* outputImage, int width, int height, int pix, int target_width, int target_height) {
	const int oly = get_global_id(0);
	const int olx = get_global_id(1);
	const int z = get_global_id(2);

	int ohy = max(oly-1, 0);

	int ohx = min(olx+1, width-1);

	uchar p = image[oly * width * pix + olx * pix + z];

	uchar p1 = image[ohy * width * pix + olx * pix + z];      /* pixel below */
	uchar p2 = image[oly * width * pix + ohx * pix + z];      /* pixel to the right  */
	uchar p3 = image[ohy * width * pix + ohx * pix + z];  /* neighbour to the below-right */

	uchar d1 = abs_diff(p, p1);
	uchar d2 = abs_diff(p, p2);
	uchar d3 = abs_diff(p, p3);
	uchar d4 = abs_diff(p1, p2);        /* North to West */

	uchar mini = d1;
	if (mini > d2) mini = d2;
	if (mini > d3) mini = d3;
	if (mini > d4) mini = d4;

	float av;
	if (mini == d1) {
		av = (float)0.5f * (p + p1);
	} else if (mini == d2) {
		av = (float)0.5f * (p + p2);
	} else if (mini == d3) {
		av = (float)0.5f * (p + p3);
	} else /* mini == d4 */{
		av = (float)0.5f * (p + 0.5f * (p + p2));
	}

	const float ratio_x = (float)target_width/width;
	const float ratio_y = (float)target_height/height;

	const float accurate_x = (float)ratio_x * olx;
	const float accurate_y = (float)ratio_y * oly;
	const int x = (int)accurate_x;
	const int y = (int)accurate_y;

	ohy = min(y + 1, target_height - 1);
	ohx = min(x + 1, target_width - 1);

	outputImage[y * target_width * pix + x * pix + z] = p;
	outputImage[y * target_width * pix + ohx * pix + z] = (uchar)av;
	outputImage[ohy * target_width * pix + x * pix + z] = (uchar)av;
	outputImage[ohy * target_width * pix + ohx * pix + z] = (uchar)av;
}

__kernel void scale_up2(__global const uchar* image, __global uchar* outputImage, int width, int height, int pix, int target_width, int target_height) {
	const int oly = get_global_id(0);
	const int olx = get_global_id(1);
	const int z = get_global_id(2);

	int ohy = max(oly-1, 0);

	int ohx = min(olx+1, width-1);

	uchar p = image[oly * width * pix + olx * pix + z];

	uchar p1 = image[ohy * width * pix + olx * pix + z];      /* pixel below */
	uchar p2 = image[oly * width * pix + ohx * pix + z];      /* pixel to the right  */
	uchar p3 = image[ohy * width * pix + ohx * pix + z];  /* neighbour to the below-right */

	uchar d1 = abs_diff(p, p1);
	uchar d2 = abs_diff(p, p2);
	uchar d3 = abs_diff(p, p3);
	uchar d4 = abs_diff(p1, p2);        /* North to West */

	uchar mini = d1;
	if (mini > d2) mini = d2;
	if (mini > d3) mini = d3;
	if (mini > d4) mini = d4;

	float av;
	if (mini == d1) {
		av = (float)0.5f * (p + p1);
	} else if (mini == d2) {
		av = (float)0.5f * (p + p2);
	} else if (mini == d3) {
		av = (float)0.5f * (p + p3);
	} else /* mini == d4 */{
		av = (float)0.5f * (p + 0.5f * (p + p2));
	}

	const float ratio_x = (float)target_width/width;
	const float ratio_y = (float)target_height/height;

	const float accurate_x = (float)ratio_x * olx;
	const float accurate_y = (float)ratio_y * oly;
	const int x = (int)accurate_x;
	const int y = (int)accurate_y;

	for(int k = 0; k < ratio_x; k++) {
		for(int l = 0; l < ratio_x; l++) {
			outputImage[(y + l) * target_width * pix + (x + k) * pix + z] = (uchar)av;
		}
	}
}