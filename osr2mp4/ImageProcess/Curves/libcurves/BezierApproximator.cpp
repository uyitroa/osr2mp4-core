//
//  . on 31/07/2020.
//

#include <vector>
#include "Vector2.h"
#include "LinearApproximator.h"

#define list_vector std::vector<Vector2<float> >


bool is_flat_enough(list_vector &control_points, float tolerance_sq) {
	for (int i = 1; i < control_points.size() - 1; i++)
		if ((control_points[i - 1] - control_points[i] * 2 + control_points[i + 1]).length_squared() > tolerance_sq)
			return false;

	return true;
}

void subdivide(list_vector &control_points, list_vector &l, list_vector &r) {
    int count = control_points.size();
    list_vector midpoints(count);

    for (int i = 0; i < count; ++i)
        midpoints[i] = control_points[i];

    for (int i = 0; i < count; i++)
    {
        l[i] = midpoints[0];
        r[count - i - 1] = midpoints[count - i - 1];

        for (int j = 0; j < count - i - 1; j++)
            midpoints[j] = (midpoints[j] + midpoints[j + 1]) / 2;
    }
}

void approximate(list_vector &control_points, list_pos &output) {
    int count = control_points.size();
    list_vector l(count * 2 -1);
    list_vector r(count);

    subdivide(control_points, l, r);

    for (int i = 0; i < count - 1; ++i)
        l[count + i] = r[i + 1];

    control_points[0].add_to_output(output);
    for (int i = 1; i < count - 1; ++i) {
        int index = 2 * i;
        Vector2<float> p =(l[index] * 2 + l[index - 1] + l[index + 1]) * 0.25f;
        p.add_to_output(output);
    }
}

void create_singlebezier(list_pos &output, list_vector &control_points) {
    int count = control_points.size();
    const float TOLERANCE = 0.5f;
    const float TOLERANCE_SQ = TOLERANCE * TOLERANCE;
    list_vector subdivision_buffer1(count);
    list_vector subdivision_buffer2(count * 2 - 1);

    if (count == 0)
        return;

    std::vector<list_vector > to_flatten;
    std::vector<list_vector > free_buffers;

    // "to_flatten" contains all the curves which are not yet approximated well enough.
    // We use a stack to emulate recursion without the risk of running into a stack overflow.
    // (More specifically, we iteratively and adaptively refine our curve with a
    // <a href="https://en.wikipedia.org/wiki/Depth-first_search">Depth-first search</a>
    // over the tree resulting from the subdivisions we make.)
    to_flatten.push_back(control_points);

    list_vector left_child = subdivision_buffer2;

    while (!to_flatten.empty()) {
        list_vector parent = to_flatten.back();
        to_flatten.pop_back();
        if (is_flat_enough(parent, TOLERANCE_SQ)) {
            // If the control points we currently operate on are sufficiently "flat", we use
            // an extension to De Casteljau's algorithm to obtain a piecewise-linear approximation
            // of the bezier curve represented by our control points, consisting of the same amount
            // of points as there are control points.
            approximate(parent, output);
            free_buffers.push_back(parent);
            continue;
        }

        // If we do not yet have a sufficiently "flat" (in other words, detailed) approximation we keep
        // subdividing the curve we are currently operating on.
        list_vector right_child;
        if (!free_buffers.empty()) {
            right_child = free_buffers.back();
            free_buffers.pop_back();
        } else {
            right_child.resize(count);
        }
        subdivide(parent, left_child, right_child);

        // We re-use the buffer of the parent for one of the children, so that we save one allocation per iteration.
        for (int i = 0; i < count; ++i)
            parent[i] = left_child[i];

        to_flatten.push_back(right_child);
        to_flatten.push_back(parent);
    }

    control_points[count - 1].add_to_output(output);
}

void create_bezier(list_pos &output, list_vector &control_points) {
    int last_index = 0;
    for(int i = 0; i < control_points.size(); i++) {
        bool multipart_segment = i < control_points.size() - 2 && (control_points[i] == control_points[i + 1]);
        if(multipart_segment || i == control_points.size() - 1) {
            list_vector sub = list_vector(control_points.begin() + last_index, control_points.begin() + i + 1);
            if (sub.size() == 2) {
                create_linear(output, sub);
            } else {
                create_singlebezier(output, sub);
            }
            if(multipart_segment) i++;
            last_index = i;
        }
    }
}
