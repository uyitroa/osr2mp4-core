# distutils: language = c++
from cpython cimport Py_buffer
import ctypes
import numpy as np
cimport numpy as np
from libcpp.vector cimport vector
from libcpp.string cimport string

# Declare the class with cdef
cdef extern from "FrameWriter.h":
	cdef cppclass FrameWriter:

		int width;
		int height;
		int n_channel;
		unsigned char *data;

		FrameWriter();
		FrameWriter(const char *filename, const char *codec_name, double fps, int width, int height, const char *ffmpegcmd, unsigned char *buf);
		void close_video();
		int write_frame();
		int is_opened();
		string geterror();

	vector[const char *] getcodecname();
	vector[const char *] getcodeclongname();

	vector[const char *] getaudiocodecname();
	vector[const char *] getaudiocodeclongname();

cdef class PyFrameWriter:
	cdef FrameWriter c_writer

	def __cinit__(self, const char *filename, const char *codec_name, double fps, int width, int height, const char *ffmpegcmd, np.ndarray im):
		cdef np.ndarray[np.uint8_t, ndim=1, mode = 'c'] np_buf = np.ascontiguousarray(im, dtype = np.uint8)
		cdef unsigned char* buf = <unsigned char*> np_buf.data
		self.c_writer = FrameWriter(filename, codec_name, fps, width, height, ffmpegcmd, buf)

	def release(self):
		return self.c_writer.close_video()

	def write(self):
		return self.c_writer.write_frame()

	def isOpened(self):
		return self.c_writer.is_opened()

	def geterror(self):
		return self.c_writer.geterror()


def getcodec():
	codecs = {}
	codecname = getcodecname()
	codeclongname = getcodeclongname()

	for i in range(len(codecname)):
		codecs[codecname[i]] = codeclongname[i]
	return codecs

def getaudiocodec():
	codecs = {}
	codecname = getaudiocodecname()
	codeclongname = getaudiocodeclongname()

	for i in range(len(codecname)):
		codecs[codecname[i]] = codeclongname[i]
	return codecs