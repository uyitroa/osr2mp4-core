#include <iostream>
#include <vector>
#include <cmath>
#include "curves.h"

//void printpos(list_pos &output) {
//    printf("%d\n", output.size());
//    for(int x = 0; x < output.size(); x++) {
//        printf("%f %f\n", output[x][0], output[x][1]);
//    }
//}
//
//
//int main() {
//
////    list_vector control_points = {Vector2<float>(306, 222), Vector2<float>(303, 149), Vector2<float>(303, 149), Vector2<float>(361, 207), Vector2<float>(372, 277), Vector2<float>(372, 277), Vector2<float>(401, 271), Vector2<float>(401, 271), Vector2<float>(413, 339), Vector2<float>(460, 375), Vector2<float>(460, 375), Vector2<float>(514, 306), Vector2<float>(482, 209), Vector2<float>(428, 191), Vector2<float>(428, 191), Vector2<float>(454, 129), Vector2<float>(454, 129), Vector2<float>(403, 88), Vector2<float>(355, 87), Vector2<float>(355, 87), Vector2<float>(368, 38), Vector2<float>(368, 38), Vector2<float>(278, 66), Vector2<float>(156, 53), Vector2<float>(82, 11)};
//    list_vector control_points = {Vector2<float>(302, 117), Vector2<float>(352, 222)};
//
////    CatmullApproximator b(control_points);
//    list_pos output;
//    create_linear(output, control_points);
//    printpos(output);
//    return 0;
//}


bool is_straight_line(list_vector control_points) {
    Vector2<float> a = control_points[0];
    Vector2<float> b = control_points[1];
    Vector2<float> c = control_points[2];
    return (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y) == 0.0f;
}

list_pos get_bezier(list_pos &control_points) {
    list_vector cp(control_points.size());
    list_pos output;
    for (int i = 0; i < control_points.size(); i++) {
        cp[i] = Vector2<float>(control_points[i][0], control_points[i][1]);
    }

    create_bezier(output, cp);
    return output;
}

list_pos get_perfect(list_pos &control_points) {
    list_vector cp(control_points.size());
    list_pos output;
    for (int i = 0; i < control_points.size(); i++) {
        cp[i] = Vector2<float>(control_points[i][0], control_points[i][1]);
    }
    if(is_straight_line(cp) || cp.size() < 3)
        create_linear(output, cp);
    else if(cp.size() > 3)
        create_bezier(output, cp);
    else
        create_perfect(output, cp);
    return output;
}

list_pos get_linear(list_pos &control_points) {
    list_vector cp(control_points.size());
    list_pos output;
    for (int i = 0; i < control_points.size(); i++) {
        cp[i] = Vector2<float>(control_points[i][0], control_points[i][1]);
    }

    create_linear(output, cp);
    return output;
}

list_pos get_catmull(list_pos &control_points) {
    list_vector cp(control_points.size());
    list_pos output;
    for (int i = 0; i < control_points.size(); i++) {
        cp[i] = Vector2<float>(control_points[i][0], control_points[i][1]);
    }

    create_catmull(output, cp);
    return output;
}

double distance(std::vector<float> a, std::vector<float> b) {
    return sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2));
}

Vector2<float> normalize(Vector2<float> value) {
    double val = 1.0f / (double)sqrt((value.x * value.x) + (value.y * value.y));
    value.x *= val;
    value.y *= val;
    return value;
}


std::vector<double> adjust_curve(list_pos &path, double expected_length) {
    const double MIN_SEGMENT_LENGTH = 0.0001;
    double total = 0;

    for (int i = 1; i < path.size(); i++)
        total += distance(path[i - 1], path[i]);

    double excess = total - expected_length;
    while (path.size() >= 2) {
        Vector2<float> v2(path[path.size() - 1][0], path[path.size() - 1][1]);
        Vector2<float> v1(path[path.size() - 2][0], path[path.size() - 2][1]);

        float last_line_length = v1.distance_from(v2);

        if (last_line_length > excess + MIN_SEGMENT_LENGTH) {
            if (v2 != v1) {
                Vector2<float> l = v1 + normalize(v2 - v1) * ((v2 - v1).length() - (float)excess);
                path[path.size() - 1][0] = l.x;
                path[path.size() - 1][1] = l.y;
            }
            break;
        }
        path.pop_back();
        excess -= last_line_length;
    }

    double t = 0;
    std::vector<double> cum_length(path.size()-1);
    for (int i = 1; i < path.size(); i++) {
        t += distance(path[i -1], path[i]);
        cum_length[i-1] = t;
    }

    return cum_length;
}


int binary_search(const std::vector<double> &v, double value) {
   int mid, left = 0 ;
   int right = v.size(); // one position passed the right end
   while (left < right) {
      mid = left + (right - left)/2;
      if (value > v[mid]){
          left = mid+1;
      }
      else if (value < v[mid]){
        right = mid;
      }
      else {
        break;
     }
   }

   return right;
}


std::vector<float> position_at(list_pos &path, std::vector<double> cum_length, double length) {

    if (path.empty() || cum_length.size() == 0)
        return std::vector<float> {0, 0};

    if (length == 0)
        return path[0];

    double end = cum_length[cum_length.size() - 1];
    if (length >= end)
        return path[path.size() - 1];

    int i = binary_search(cum_length, length);
    i = (int)fmin(i, cum_length.size() - 1);

    double length_next = cum_length[i];
    double length_previous = i == 0 ? 0 : cum_length[i - 1];

    i++;

    Vector2<float> res(path[i-1][0], path[i-1][1]);

    Vector2<float> p1(path[i-1][0], path[i-1][1]);
    Vector2<float> p2(path[i][0], path[i][1]);

    if (length_next != length_previous)
        res = res + (p2 - p1) * (float)((length - length_previous) / (length_next - length_previous));

    return std::vector<float> {res.x, res.y};
}

//int main() {
//    std::vector<double> v = {1, 3, 5, 6, 10, 12, 19, 20, 33, 45, 55};
////    printf("%d\n", binary_search(v, 1000));
//    printf("%f\n", v[binary_search(v, 19)]);
//}

//int main() {
//
//    list_vector control_points = {Vector2<float>(306, 222), Vector2<float>(303, 149), Vector2<float>(303, 149), Vector2<float>(361, 207), Vector2<float>(372, 277), Vector2<float>(372, 277), Vector2<float>(401, 271), Vector2<float>(401, 271), Vector2<float>(413, 339), Vector2<float>(460, 375), Vector2<float>(460, 375), Vector2<float>(514, 306), Vector2<float>(482, 209), Vector2<float>(428, 191), Vector2<float>(428, 191), Vector2<float>(454, 129), Vector2<float>(454, 129), Vector2<float>(403, 88), Vector2<float>(355, 87), Vector2<float>(355, 87), Vector2<float>(368, 38), Vector2<float>(368, 38), Vector2<float>(278, 66), Vector2<float>(156, 53), Vector2<float>(82, 11)};
////    list_vector control_points = {Vector2<float>(302, 117), Vector2<float>(352, 222)};
//
//    for(int x = 0; x < 10000; x++) {
//        list_pos output;
//        create_bezier(output, control_points);
//        std::vector<double> cum_length = adjust_curve(output, 1162.50004434586);
//        for(int i = 0; i < cum_length[cum_length.size() - 1]; i+=10) {
//            std::vector<float> pos = position_at(output, cum_length, 1162.50004434586);
//        }
//    }
//    return 0;
//}