__kernel void copy(
    __global const uchar *a_g, __global uchar *b_g, const int a_w, const int b_w, const int pix, const int x_offset, const int y_offset)
{
	int colid = get_global_id(0);
	int rowid = get_global_id(1);
    int pixid = get_global_id(2);

    const int a_index = colid * a_w * pix + rowid * pix + pixid;
    const int b_index = (colid + y_offset) * b_w * pix + (rowid + x_offset) * pix + pixid;
	b_g[b_index] = a_g[a_index];
}