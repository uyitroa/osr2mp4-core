__kernel void edit_channel(
    __global const uchar *a_g, __global uchar *dest, const int a_w, const int pix, const int target_pix, const float scale)
{
	int colid = get_global_id(0);
	int rowid = get_global_id(1);

    const int a_index = colid * a_w * pix + rowid * pix + target_pix;
	dest[a_index] = a_g[a_index] * scale;
}