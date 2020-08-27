from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy


setup(name="zzz", cmdclass = {'build_ext': build_ext},
	ext_modules=[
		Extension("osr2mp4cv", sources=["PyFrameWriter.pyx", "FrameWriter.cpp"], extra_compile_args=["-std=c++11", "-w"],
                language="c++",
                include_dirs = ['include', numpy.get_include()],
        libraries = ['avcodec', 'avutil', 'avformat', 'swresample', 'swscale'],
        library_dirs = ['lib'])])
