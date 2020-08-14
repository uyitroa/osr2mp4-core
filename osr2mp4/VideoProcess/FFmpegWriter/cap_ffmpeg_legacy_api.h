// This file is part of OpenCV project.
// It is subject to the license terms in the LICENSE file found in the top-level directory
// of this distribution and at http://opencv.org/license.html.
#ifndef __OPENCV_FFMPEG_LEGACY_API_H__
#define __OPENCV_FFMPEG_LEGACY_API_H__

#ifdef __cplusplus
extern "C"
{
#endif

#ifndef OPENCV_FFMPEG_API
#if defined(__OPENCV_BUILD)
#   define OPENCV_FFMPEG_API
#elif defined _WIN32
#   define OPENCV_FFMPEG_API __declspec(dllexport)
#elif defined __GNUC__ && __GNUC__ >= 4
#   define OPENCV_FFMPEG_API __attribute__ ((visibility ("default")))
#else
#   define OPENCV_FFMPEG_API
#endif
#endif

typedef struct CvVideoWriter_FFMPEG CvVideoWriter_FFMPEG;

OPENCV_FFMPEG_API struct CvVideoWriter_FFMPEG* cvCreateVideoWriter_FFMPEG(const char* filename,
            const char *codec_name, double fps, int width, int height, const char *ffmpegcmd);
OPENCV_FFMPEG_API int cvWriteFrame_FFMPEG(struct CvVideoWriter_FFMPEG* writer, const unsigned char* data,
                                          int step, int width, int height, int cn, int origin);
OPENCV_FFMPEG_API void cvReleaseVideoWriter_FFMPEG(struct CvVideoWriter_FFMPEG** writer);

#ifdef __cplusplus
}
#endif

#endif  // __OPENCV_FFMPEG_LEGACY_API_H__