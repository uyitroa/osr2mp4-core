#define pi 3.14159265358979323846

#include <cmath>
#include "Approximator.h"


double circle_t_at(Vector2<float> pt, Vector2<float> centre) {
    return atan2(pt.y - centre.y, pt.x - centre.x);
}


void circle_through_points(list_vector &control_points, Vector2<float> &centre, float &radius,
                                                double &t_initial, double &t_final) {
    // Circle through 3 points
    // http://en.wikipedia.org/wiki/Circumscribed_circle#Cartesian_coordinates

    Vector2<float> a = control_points[0];
    Vector2<float> b = control_points[1];
    Vector2<float> c = control_points[2];

    float d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
    float amagsq = a.length_squared();
    float bmagsq = b.length_squared();
    float cmagsq = c.length_squared();
    centre = Vector2<float>(
        (amagsq * (b.y - c.y) + bmagsq * (c.y - a.y) + cmagsq * (a.y - b.y)) / d,
        (amagsq * (c.x - b.x) + bmagsq * (a.x - c.x) + cmagsq * (b.x - a.x)) / d);
    radius = a.distance_from(centre);

    t_initial = circle_t_at(a, centre);
    double t_mid = circle_t_at(b, centre);
    t_final = circle_t_at(c, centre);

    while (t_mid < t_initial) t_mid += 2 * pi;
    while (t_final < t_initial) t_final += 2 * pi;
    if (t_mid > t_final)
    {
        t_final -= 2 * pi;
    }
}

Vector2<float> circle_point(Vector2<float> centre, float radius, double t) {
    return Vector2<float>((float)(cos(t) * radius), (float)(sin(t) * radius)) + centre;
}

void create_perfect(list_pos &output, list_vector &control_points) {

    Vector2<float> centre;
    float radius;
    double t_initial, t_final;
    const float TOLERANCE = 0.125f;

    circle_through_points(control_points, centre, radius, t_initial, t_final);

    double curve_length = abs((t_final - t_initial) * radius);
    int _segments = (int)(curve_length * TOLERANCE);

    control_points[0].add_to_output(output);

    for (int i = 1; i < _segments; i++)
    {
        double progress = (double)i / (double)_segments;
        double t = t_final * progress + t_initial * (1 - progress);

        Vector2<float> new_point = circle_point(centre, radius, t);
        new_point.add_to_output(output);

    }

    control_points[2].add_to_output(output);
}
