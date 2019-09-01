__kernel void add_to_frame4(
    __global const uchar *a_g, __global uchar *b_g, const int a_w, const int a_z, const int b_w, const int b_z)
{
	int rowid = get_global_id(0);
	int colid = get_global_id(1);

	int b_index = rowid * b_w * b_z + colid * b_z;
	int a_index = rowid * a_w * a_z + colid * a_z;
	const float alpha = 1 - a_g[a_index+3] / 255.0;
	b_g[b_index] = a_g[a_index] + b_g[b_index] * alpha;
	b_g[b_index+1] = a_g[a_index+1] + b_g[b_index+1] * alpha;
	b_g[b_index+2] = a_g[a_index+2] + b_g[b_index+2] * alpha;
	b_g[b_index+3] = a_g[a_index+3] + b_g[b_index+3] * alpha;
}