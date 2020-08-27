from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension(
    name="ccurves",
    sources=["ccurves.pyx", 'BezierApproximator.cpp', 'Vector2.cpp', 'PerfectApproximator.cpp', 'LinearApproximator.cpp', 'CatmullApproximator.cpp', 'curves.cpp'],
    extra_compile_args=["-std=c++11", "-w"],
    language="c++",
    )]

setup(
    name = 'ccurves',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
)    
