//
//  . on 31/07/2020.
//

#ifndef BEZIER_BEZIERAPPROXIMATOR_H
#define BEZIER_BEZIERAPPROXIMATOR_H


#include "Vector2.h"
#define list_pos std::vector<std::vector<float> >
#define list_vector std::vector<Vector2<float> >


bool is_flat_enough(list_vector &control_points, float tolerance_sq);
void subdivide(list_vector &control_points, list_vector &l, list_vector &r);
void approximate(list_vector &control_points, list_pos &output);
void create_singlebezier(list_pos &output, list_vector &control_points);
void create_bezier(list_pos &output, list_vector &control_points);


#endif //BEZIER_BEZIERAPPROXIMATOR_H
