cmake_minimum_required(VERSION 3.12)
project(Bezier)

set(CMAKE_CXX_STANDARD 14)

add_executable(Bezier curves.cpp Vector2.cpp Vector2.h BezierApproximator.cpp BezierApproximator.h PerfectApproximator.cpp PerfectApproximator.h CatmullApproximator.cpp CatmullApproximator.h LinearApproximator.cpp LinearApproximator.h Approximator.h curves.h)
target_link_libraries(Bezier)