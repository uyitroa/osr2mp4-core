
#include "Vector2.h"
#define list_vector std::vector<Vector2<float> >

void create_linear(list_pos &output, list_vector &control_points) {
    for (int i = 1; i < control_points.size(); i++) {
        Vector2<float> l1 = control_points[i - 1];
        Vector2<float> l2 = control_points[i];
        int segments = 1;

        for (int j = 0; j <= segments; j++)
        {
            Vector2<float> v1 = l1 + (l2 - l1) * ((float)j / segments);
//            Vector2<float> v2 = l1 + (l2 - l1) * ((float)(j + 1) / segments);
            v1.add_to_output(output);

        }

//        path[path.Count - 1].forceEnd = true;
    }
}