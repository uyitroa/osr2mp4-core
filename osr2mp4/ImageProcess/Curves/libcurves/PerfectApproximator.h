//
//  . on 01/08/2020.
//

#ifndef BEZIER_PERFECTAPPROXIMATOR_H
#define BEZIER_PERFECTAPPROXIMATOR_H

#include "Vector2.h"

#define list_vector std::vector<Vector2<float> >

void circle_through_points(list_vector &control_points, Vector2<float> &centre, float &radius, double &t_initial, double &t_final);
double circle_t_at(Vector2<float> pt, Vector2<float> centre);
Vector2<float> circle_point(Vector2<float> centre, float radius, double t);
void create_perfect(list_pos &output, list_vector &control_points);


#endif //BEZIER_PERFECTAPPROXIMATOR_H
