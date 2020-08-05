//
//  . on 01/08/2020.
//

#ifndef BEZIER_APPROXIMATOR_H
#define BEZIER_APPROXIMATOR_H
#define list_pos std::vector<std::vector<float> >
#define list_vector std::vector<Vector2<float> >

#include "Vector2.h"
#include <iostream>
#include <vector>

class Approximator {
protected:
    list_vector control_points;
public:
    virtual void create(list_pos &output) = 0;
};


#endif //BEZIER_APPROXIMATOR_H
