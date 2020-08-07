#include "Vector2.h"
#include <cmath>


template<class T>
Vector2<T>::Vector2(T x, T y) {
        this->x = x;
        this->y = y;
}

//template<class T>
//Vector2<T> Vector2<T>::operator+(Vector2<T> &v) {
//    return Vector2<T>(T(this->x + v.x), T(this->y + v.y));
//}

template<class T>
Vector2<T> Vector2<T>::operator+(const Vector2<T> &v) {
    return Vector2<T>(T(this->x + v.x), T(this->y + v.y));
}


//template<class T>
//Vector2<T> Vector2<T>::operator-(Vector2<T> &v) {
//    return Vector2<T>(T(this->x - v.x), T(this->y - v.y));
//}

template<class T>
Vector2<T> Vector2<T>::operator-(const Vector2<T> &v) {
    return Vector2<T>(T(this->x - v.x), T(this->y - v.y));
}

template<class T>
Vector2<T> Vector2<T>::operator*(const int n) {
    return Vector2<T>(T(this->x * n), T(this->y * n));
}

template<class T>
Vector2<T> Vector2<T>::operator*(const float n) {
    return Vector2<T>(T(this->x * n), T(this->y * n));
}

//template<class T>
//Vector2<T> Vector2<T>::operator/(const int n) {
//    return Vector2<T>(T(this->x / n), T(this->y / n));
//}

template<class T>
float Vector2<T>::length() {
    return sqrt(this->length_squared());
}

template<class T>
float Vector2<T>::length_squared() {
    return (pow(this->x, 2) + pow(this->y, 2));
}

template<class T>
Vector2<T>& Vector2<T>::operator=(const Vector2<T> &v) {
    this->x = v.x;
    this->y = v.y;
    return *this;
}

template<class T>
void Vector2<T>::add_to_output(list_pos &output) {
//    if (output.size() > 0)
//        if(output[output.size() - 1][0] == this->x && output[output.size() - 1][1] == this->y)
//            return;
    output.push_back(std::vector<float> {this->x, this->y});
}

template<class T>
Vector2<T> Vector2<T>::operator/(const float n) {
    return Vector2<T>(T(this->x / n), T(this->y / n));
}

template<class T>
float Vector2<T>::distance_from(const Vector2<T> &v) {
    return sqrt(pow(this->x - v.x, 2) + pow(this->y - v.y, 2));
}

template<class T>
bool Vector2<T>::operator!=(const Vector2<T> &v) {
    return (this->x != v.x) || (this->y != v.y);
}

template<class T>
bool Vector2<T>::operator==(const Vector2<T> &v) {
    return (this->x == v.x) && (this->y == v.y);
}

template class Vector2<float>;