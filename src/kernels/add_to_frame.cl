__kernel void add_to_frame3(
    __global const uchar *overlay_g, __global uchar *bg_g, const int a_w, const int a_z, const int b_w, const int b_z, const int bx_offset, const int by_offset, const int ax_offset, const int ay_offset, const float alpha)
{
	int colid = get_global_id(0);
	int rowid = get_global_id(1);

	int b_index = (colid + by_offset) * b_w * b_z + (rowid + bx_offset) * b_z;
	int a_index = (colid + ay_offset) * a_w * a_z + (rowid + ax_offset) * a_z;
	const float alpha_s = overlay_g[a_index+3] * alpha / 255.0;
	const float alpha_l = 1 - alpha_s;
	bg_g[b_index] = overlay_g[a_index] * alpha_s + bg_g[b_index] * alpha_l;
	bg_g[b_index+1] = overlay_g[a_index+1] * alpha_s + bg_g[b_index+1] * alpha_l;
	bg_g[b_index+2] = overlay_g[a_index+2] * alpha_s + bg_g[b_index+2] * alpha_l;
}


// TODO: optimize
__kernel void add_to_frame4(
    __global const uchar *overlay_g, __global uchar *bg_g, const int a_w, const int a_z, const int b_w, const int b_z, const int bx_offset, const int by_offset, const int ax_offset, const int ay_offset, const float alpha)
{
	int colid = get_global_id(0);
	int rowid = get_global_id(1);

	int b_index = (colid + by_offset) * b_w * b_z + (rowid + bx_offset) * b_z;
	int a_index = (colid + ay_offset) * a_w * a_z + (rowid + ax_offset) * a_z;
	const float alpha_s = overlay_g[a_index+3] / 255.0 * alpha;
	const float alpha_l = 1 - alpha_s;
	const float dst_alpha = bg_g[b_index+3] / 255.0;
	const float out_alpha = alpha_s + dst_alpha * alpha_l;
	if (out_alpha == 0) {
	    bg_g[b_index] = 0;
	    bg_g[b_index+1] = 0;
	    bg_g[b_index+2] = 0;
	    bg_g[b_index+3] = 0;
	}
	bg_g[b_index] = (overlay_g[a_index] * alpha_s + bg_g[b_index] * alpha_l * dst_alpha)/out_alpha;
	bg_g[b_index+1] = (overlay_g[a_index+1] * alpha_s + bg_g[b_index+1] * alpha_l * dst_alpha)/out_alpha;
	bg_g[b_index+2] = (overlay_g[a_index+2] * alpha_s + bg_g[b_index+2] * alpha_l * dst_alpha)/out_alpha;
	bg_g[b_index+3] = out_alpha * 255.0;
}