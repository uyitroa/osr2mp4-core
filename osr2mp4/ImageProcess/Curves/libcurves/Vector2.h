

#ifndef BEZIER_VECTOR_H
#define BEZIER_VECTOR_H
#define list_pos std::vector<std::vector<float> >

#include <iostream>
#include <vector>

template <class T>
class Vector2 {
public:
    T x, y;

    Vector2() {};
    Vector2(T x, T y);

//    Vector2<T> operator+(Vector2<T> &v);
    Vector2<T> operator+(const Vector2<T> &v);
//    Vector2<T> operator-(Vector2<T> &v);
    Vector2<T> operator-(const Vector2<T> &v);
    Vector2<T> operator*(const int n);
    Vector2<T> operator*(const float n);
    Vector2<T> operator/(const float n);
    bool operator!=(const Vector2<T> &v);
    bool operator==(const Vector2<T> &v);
    void add_to_output(list_pos &output);
    Vector2<T>& operator=(const Vector2<T> &v);
    float length();
    float length_squared();
    float distance_from(const Vector2<T> &v);
};


#endif //BEZIER_VECTOR_H
