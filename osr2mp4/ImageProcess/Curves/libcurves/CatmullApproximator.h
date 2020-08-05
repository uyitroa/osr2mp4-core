//
//  . on 01/08/2020.
//

#ifndef BEZIER_CATMULLAPPROXIMATOR_H
#define BEZIER_CATMULLAPPROXIMATOR_H

#include "Vector2.h"

#define list_pos std::vector<std::vector<float> >
#define list_vector std::vector<Vector2<float> >


Vector2<float> catmul_rom(Vector2<float> v1, Vector2<float> v2, Vector2<float> v3, Vector2<float> v4, float amount);
void create_catmull(list_pos &output, list_vector &control_points);


#endif //BEZIER_CATMULLAPPROXIMATOR_H
