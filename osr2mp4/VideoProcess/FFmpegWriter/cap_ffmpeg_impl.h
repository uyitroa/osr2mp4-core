/*M///////////////////////////////////////////////////////////////////////////////////////
//
//  IMPORTANT: READ BEFORE DOWNLOADING, COPYING, INSTALLING OR USING.
//
//  By downloading, copying, installing or using the software you agree to this license.
//  If you do not agree to this license, do not download, install,
//  copy or use the software.
//
//
//                          License Agreement
//                For Open Source Computer Vision Library
//
// Copyright (C) 2000-2008, Intel Corporation, all rights reserved.
// Copyright (C) 2009, Willow Garage Inc., all rights reserved.
// Third party copyrights are property of their respective owners.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//   * Redistribution's of source code must retain the above copyright notice,
//     this list of conditions and the following disclaimer.
//
//   * Redistribution's in binary form must reproduce the above copyright notice,
//     this list of conditions and the following disclaimer in the documentation
//     and/or other materials provided with the distribution.
//
//   * The name of the copyright holders may not be used to endorse or promote products
//     derived from this software without specific prior written permission.
//
// This software is provided by the copyright holders and contributors "as is" and
// any express or implied warranties, including, but not limited to, the implied
// warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the Intel Corporation or contributors be liable for any direct,
// indirect, incidental, special, exemplary, or consequential damages
// (including, but not limited to, procurement of substitute goods or services;
// loss of use, data, or profits; or business interruption) however caused
// and on any theory of liability, whether in contract, strict liability,
// or tort (including negligence or otherwise) arising in any way out of
// the use of this software, even if advised of the possibility of such damage.
//
//M*/
#ifndef CVFFMPEG_CAPFFMPEG
#define CVFFMPEG_CAPFFMPEG


#include "cap_ffmpeg_legacy_api.h"

#if !(defined(_WIN32) || defined(WINCE))
# include <pthread.h>
#endif
#include <assert.h>
#include <algorithm>
#include <limits>
#include <vector>
#include <string>
#include <sstream>

#define CALC_FFMPEG_VERSION(a,b,c) ( a<<16 | b<<8 | c )

#if defined _MSC_VER && _MSC_VER >= 1200
#pragma warning( disable: 4244 4510 4610 )
#endif

#ifdef __GNUC__
#  pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#endif

#ifndef CV_UNUSED  // Required for standalone compilation mode (OpenCV defines this in base.hpp)
#define CV_UNUSED(name) (void)name
#endif

#ifdef __cplusplus
extern "C" {
#endif

#ifdef __cplusplus
extern "C" {
#endif

#if !defined(_WIN32) || defined(__MINGW32__)
// some versions of FFMPEG assume a C99 compiler, and don't define INT64_C
#include <stdint.h>

// some versions of FFMPEG assume a C99 compiler, and don't define INT64_C
#ifndef INT64_C
#define INT64_C(c) (c##LL)
#endif

#ifndef UINT64_C
#define UINT64_C(c) (c##ULL)
#endif

#include <errno.h>
#endif

#include <libavformat/avformat.h>

#ifdef __cplusplus
}
#endif

#include <libavutil/mathematics.h>

#if LIBAVUTIL_BUILD > CALC_FFMPEG_VERSION(51,11,0)
  #include <libavutil/opt.h>
#endif

#if LIBAVUTIL_BUILD >= (LIBAVUTIL_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(51, 63, 100) : CALC_FFMPEG_VERSION(54, 6, 0))
#include <libavutil/imgutils.h>
#endif

#include <libavcodec/avcodec.h>
#include <libswscale/swscale.h>

#ifdef __cplusplus
}
#endif

#if defined _MSC_VER && _MSC_VER >= 1200
#pragma warning( default: 4244 4510 4610 )
#endif

#ifdef NDEBUG
#define CV_WARN(message)
#else
#define CV_WARN(message) fprintf(stderr, "warning: %s (%s:%d)\n", message, __FILE__, __LINE__)
#endif

#if defined _WIN32
    #include <windows.h>
    #if defined _MSC_VER && _MSC_VER < 1900
    struct timespec
    {
        time_t tv_sec;
        long   tv_nsec;
    };
  #endif
#elif defined __linux__ || defined __APPLE__ || defined __HAIKU__
    #include <unistd.h>
    #include <stdio.h>
    #include <sys/types.h>
    #include <sys/time.h>
#if defined __APPLE__
    #include <sys/sysctl.h>
    #include <mach/clock.h>
    #include <mach/mach.h>
#endif
#endif

#ifndef MIN
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#endif

#if defined(__APPLE__)
#define AV_NOPTS_VALUE_ ((int64_t)0x8000000000000000LL)
#else
#define AV_NOPTS_VALUE_ ((int64_t)AV_NOPTS_VALUE)
#endif

#ifndef AVERROR_EOF
#define AVERROR_EOF (-MKTAG( 'E','O','F',' '))
#endif

#if LIBAVCODEC_BUILD >= CALC_FFMPEG_VERSION(54,25,0)
#  define CV_CODEC_ID AVCodecID
#  define CV_CODEC(name) AV_##name
#else
#  define CV_CODEC_ID CodecID
#  define CV_CODEC(name) name
#endif

#if LIBAVUTIL_BUILD < (LIBAVUTIL_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(51, 74, 100) : CALC_FFMPEG_VERSION(51, 42, 0))
#define AVPixelFormat PixelFormat
#define AV_PIX_FMT_BGR24 PIX_FMT_BGR24
#define AV_PIX_FMT_RGB24 PIX_FMT_RGB24
#define AV_PIX_FMT_GRAY8 PIX_FMT_GRAY8
#define AV_PIX_FMT_YUV422P PIX_FMT_YUV422P
#define AV_PIX_FMT_YUV420P PIX_FMT_YUV420P
#define AV_PIX_FMT_YUV444P PIX_FMT_YUV444P
#define AV_PIX_FMT_YUVJ420P PIX_FMT_YUVJ420P
#define AV_PIX_FMT_GRAY16LE PIX_FMT_GRAY16LE
#define AV_PIX_FMT_GRAY16BE PIX_FMT_GRAY16BE
#endif

#ifndef PKT_FLAG_KEY
#define PKT_FLAG_KEY AV_PKT_FLAG_KEY
#endif

#if LIBAVUTIL_BUILD >= (LIBAVUTIL_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(52, 38, 100) : CALC_FFMPEG_VERSION(52, 13, 0))
#define USE_AV_FRAME_GET_BUFFER 1
#else
#define USE_AV_FRAME_GET_BUFFER 0
#ifndef AV_NUM_DATA_POINTERS // required for 0.7.x/0.8.x ffmpeg releases
#define AV_NUM_DATA_POINTERS 4
#endif
#endif


#ifndef USE_AV_INTERRUPT_CALLBACK
#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 21, 0)
#define USE_AV_INTERRUPT_CALLBACK 1
#else
#define USE_AV_INTERRUPT_CALLBACK 0
#endif
#endif

#if USE_AV_INTERRUPT_CALLBACK
#define LIBAVFORMAT_INTERRUPT_OPEN_TIMEOUT_MS 30000
#define LIBAVFORMAT_INTERRUPT_READ_TIMEOUT_MS 30000

#ifdef _WIN32
// http://stackoverflow.com/questions/5404277/porting-clock-gettime-to-windows

static
inline LARGE_INTEGER get_filetime_offset()
{
    SYSTEMTIME s;
    FILETIME f;
    LARGE_INTEGER t;

    s.wYear = 1970;
    s.wMonth = 1;
    s.wDay = 1;
    s.wHour = 0;
    s.wMinute = 0;
    s.wSecond = 0;
    s.wMilliseconds = 0;
    SystemTimeToFileTime(&s, &f);
    t.QuadPart = f.dwHighDateTime;
    t.QuadPart <<= 32;
    t.QuadPart |= f.dwLowDateTime;
    return t;
}

static
inline void get_monotonic_time(timespec *tv)
{
    LARGE_INTEGER           t;
    FILETIME				f;
    double                  microseconds;
    static LARGE_INTEGER    offset;
    static double           frequencyToMicroseconds;
    static int              initialized = 0;
    static BOOL             usePerformanceCounter = 0;

    if (!initialized)
    {
        LARGE_INTEGER performanceFrequency;
        initialized = 1;
        usePerformanceCounter = QueryPerformanceFrequency(&performanceFrequency);
        if (usePerformanceCounter)
        {
            QueryPerformanceCounter(&offset);
            frequencyToMicroseconds = (double)performanceFrequency.QuadPart / 1000000.;
        }
        else
        {
            offset = get_filetime_offset();
            frequencyToMicroseconds = 10.;
        }
    }

    if (usePerformanceCounter)
    {
        QueryPerformanceCounter(&t);
    } else {
        GetSystemTimeAsFileTime(&f);
        t.QuadPart = f.dwHighDateTime;
        t.QuadPart <<= 32;
        t.QuadPart |= f.dwLowDateTime;
    }

    t.QuadPart -= offset.QuadPart;
    microseconds = (double)t.QuadPart / frequencyToMicroseconds;
    t.QuadPart = microseconds;
    tv->tv_sec = t.QuadPart / 1000000;
    tv->tv_nsec = (t.QuadPart % 1000000) * 1000;
}
#else
static
inline void get_monotonic_time(timespec *time)
{
#if defined(__APPLE__) && defined(__MACH__)
    clock_serv_t cclock;
    mach_timespec_t mts;
    host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &cclock);
    clock_get_time(cclock, &mts);
    mach_port_deallocate(mach_task_self(), cclock);
    time->tv_sec = mts.tv_sec;
    time->tv_nsec = mts.tv_nsec;
#else
    clock_gettime(CLOCK_MONOTONIC, time);
#endif
}
#endif

static
inline timespec get_monotonic_time_diff(timespec start, timespec end)
{
    timespec temp;
    if (end.tv_nsec - start.tv_nsec < 0)
    {
        temp.tv_sec = end.tv_sec - start.tv_sec - 1;
        temp.tv_nsec = 1000000000 + end.tv_nsec - start.tv_nsec;
    }
    else
    {
        temp.tv_sec = end.tv_sec - start.tv_sec;
        temp.tv_nsec = end.tv_nsec - start.tv_nsec;
    }
    return temp;
}

static
inline double get_monotonic_time_diff_ms(timespec time1, timespec time2)
{
    timespec delta = get_monotonic_time_diff(time1, time2);
    double milliseconds = delta.tv_sec * 1000 + (double)delta.tv_nsec / 1000000.0;

    return milliseconds;
}
#endif // USE_AV_INTERRUPT_CALLBACK

static int get_number_of_cpus(void)
{
#if LIBAVFORMAT_BUILD < CALC_FFMPEG_VERSION(52, 111, 0)
    return 1;
#elif defined _WIN32
    SYSTEM_INFO sysinfo;
    GetSystemInfo( &sysinfo );

    return (int)sysinfo.dwNumberOfProcessors;
#elif defined __linux__ || defined __HAIKU__
    return (int)sysconf( _SC_NPROCESSORS_ONLN );
#elif defined __APPLE__
    int numCPU=0;
    int mib[4];
    size_t len = sizeof(numCPU);

    // set the mib for hw.ncpu
    mib[0] = CTL_HW;
    mib[1] = HW_AVAILCPU;  // alternatively, try HW_NCPU;

    // get the number of CPUs from the system
    sysctl(mib, 2, &numCPU, &len, NULL, 0);

    if( numCPU < 1 )
    {
        mib[1] = HW_NCPU;
        sysctl( mib, 2, &numCPU, &len, NULL, 0 );

        if( numCPU < 1 )
            numCPU = 1;
    }

    return (int)numCPU;
#else
    return 1;
#endif
}


struct Image_FFMPEG
{
    unsigned char* data;
    int step;
    int width;
    int height;
    int cn;
};


#if USE_AV_INTERRUPT_CALLBACK
struct AVInterruptCallbackMetadata
{
    timespec value;
    unsigned int timeout_after_ms;
    int timeout;
};

// https://github.com/opencv/opencv/pull/12693#issuecomment-426236731
static
inline const char* _opencv_avcodec_get_name(AVCodecID id)
{
#if LIBAVCODEC_VERSION_MICRO >= 100 \
    && LIBAVCODEC_BUILD >= CALC_FFMPEG_VERSION(53, 47, 100)
    return avcodec_get_name(id);
#else
    const AVCodecDescriptor *cd;
    AVCodec *codec;

    if (id == AV_CODEC_ID_NONE)
    {
        return "none";
    }
    cd = avcodec_descriptor_get(id);
    if (cd)
    {
        return cd->name;
    }
    codec = avcodec_find_decoder(id);
    if (codec)
    {
        return codec->name;
    }
    codec = avcodec_find_encoder(id);
    if (codec)
    {
        return codec->name;
    }

    return "unknown_codec";
#endif
}

static
inline void _opencv_ffmpeg_free(void** ptr)
{
    if(*ptr) free(*ptr);
    *ptr = 0;
}

static
inline int _opencv_ffmpeg_interrupt_callback(void *ptr)
{
    AVInterruptCallbackMetadata* metadata = (AVInterruptCallbackMetadata*)ptr;
    assert(metadata);

    if (metadata->timeout_after_ms == 0)
    {
        return 0; // timeout is disabled
    }

    timespec now;
    get_monotonic_time(&now);

    metadata->timeout = get_monotonic_time_diff_ms(metadata->value, now) > metadata->timeout_after_ms;

    return metadata->timeout ? -1 : 0;
}
#endif

static
inline void _opencv_ffmpeg_av_packet_unref(AVPacket *pkt)
{
#if LIBAVCODEC_BUILD >= (LIBAVCODEC_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(55, 25, 100) : CALC_FFMPEG_VERSION(55, 16, 0))
    av_packet_unref(pkt);
#else
    av_free_packet(pkt);
#endif
};

static
inline void _opencv_ffmpeg_av_image_fill_arrays(void *frame, uint8_t *ptr, enum AVPixelFormat pix_fmt, int width, int height)
{
#if LIBAVUTIL_BUILD >= (LIBAVUTIL_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(51, 63, 100) : CALC_FFMPEG_VERSION(54, 6, 0))
    av_image_fill_arrays(((AVFrame*)frame)->data, ((AVFrame*)frame)->linesize, ptr, pix_fmt, width, height, 1);
#else
    avpicture_fill((AVPicture*)frame, ptr, pix_fmt, width, height);
#endif
};

static
inline int _opencv_ffmpeg_av_image_get_buffer_size(enum AVPixelFormat pix_fmt, int width, int height)
{
#if LIBAVUTIL_BUILD >= (LIBAVUTIL_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(51, 63, 100) : CALC_FFMPEG_VERSION(54, 6, 0))
    return av_image_get_buffer_size(pix_fmt, width, height, 1);
#else
    return avpicture_get_size(pix_fmt, width, height);
#endif
};

static AVRational _opencv_ffmpeg_get_sample_aspect_ratio(AVStream *stream)
{
#if LIBAVUTIL_VERSION_MICRO >= 100 && LIBAVUTIL_BUILD >= CALC_FFMPEG_VERSION(54, 5, 100)
    return av_guess_sample_aspect_ratio(NULL, stream, NULL);
#else
    AVRational undef = {0, 1};

    // stream
    AVRational ratio = stream ? stream->sample_aspect_ratio : undef;
    av_reduce(&ratio.num, &ratio.den, ratio.num, ratio.den, INT_MAX);
    if (ratio.num > 0 && ratio.den > 0)
        return ratio;

    // codec
    ratio  = stream && stream->codec ? stream->codec->sample_aspect_ratio : undef;
    av_reduce(&ratio.num, &ratio.den, ratio.num, ratio.den, INT_MAX);
    if (ratio.num > 0 && ratio.den > 0)
        return ratio;

    return undef;
#endif
}


#ifndef AVSEEK_FLAG_FRAME
#define AVSEEK_FLAG_FRAME 0
#endif
#ifndef AVSEEK_FLAG_ANY
#define AVSEEK_FLAG_ANY 1
#endif

#if defined(__OPENCV_BUILD) || defined(BUILD_PLUGIN)
typedef cv::Mutex ImplMutex;
#else
class ImplMutex
{
public:
    ImplMutex() { init(); }
    ~ImplMutex() { destroy(); }

    void init();
    void destroy();

    void lock();
    bool trylock();
    void unlock();

    struct Impl;
protected:
    Impl* impl;

private:
    ImplMutex(const ImplMutex&);
    ImplMutex& operator = (const ImplMutex& m);
};

#if defined _WIN32 || defined WINCE

struct ImplMutex::Impl
{
    void init()
    {
#if (_WIN32_WINNT >= 0x0600)
        ::InitializeCriticalSectionEx(&cs, 1000, 0);
#else
        ::InitializeCriticalSection(&cs);
#endif
        refcount = 1;
    }
    void destroy() { DeleteCriticalSection(&cs); }

    void lock() { EnterCriticalSection(&cs); }
    bool trylock() { return TryEnterCriticalSection(&cs) != 0; }
    void unlock() { LeaveCriticalSection(&cs); }

    CRITICAL_SECTION cs;
    int refcount;
};

#ifndef __GNUC__
static int _interlockedExchangeAdd(int* addr, int delta)
{
#if defined _MSC_VER && _MSC_VER >= 1500
    return (int)_InterlockedExchangeAdd((long volatile*)addr, delta);
#else
    return (int)InterlockedExchangeAdd((long volatile*)addr, delta);
#endif
}
#endif // __GNUC__

#elif defined __APPLE__

#include <libkern/OSAtomic.h>

struct ImplMutex::Impl
{
    void init() { sl = OS_SPINLOCK_INIT; refcount = 1; }
    void destroy() { }

    void lock() { OSSpinLockLock(&sl); }
    bool trylock() { return OSSpinLockTry(&sl); }
    void unlock() { OSSpinLockUnlock(&sl); }

    OSSpinLock sl;
    int refcount;
};

#elif defined __linux__ && !defined __ANDROID__

struct ImplMutex::Impl
{
    void init() { pthread_spin_init(&sl, 0); refcount = 1; }
    void destroy() { pthread_spin_destroy(&sl); }

    void lock() { pthread_spin_lock(&sl); }
    bool trylock() { return pthread_spin_trylock(&sl) == 0; }
    void unlock() { pthread_spin_unlock(&sl); }

    pthread_spinlock_t sl;
    int refcount;
};

#else

struct ImplMutex::Impl
{
    void init() { pthread_mutex_init(&sl, 0); refcount = 1; }
    void destroy() { pthread_mutex_destroy(&sl); }

    void lock() { pthread_mutex_lock(&sl); }
    bool trylock() { return pthread_mutex_trylock(&sl) == 0; }
    void unlock() { pthread_mutex_unlock(&sl); }

    pthread_mutex_t sl;
    int refcount;
};

#endif

void ImplMutex::init()
{
    impl = new Impl();
    impl->init();
}
void ImplMutex::destroy()
{
    impl->destroy();
    delete(impl);
    impl = NULL;
}
void ImplMutex::lock() { impl->lock(); }
void ImplMutex::unlock() { impl->unlock(); }
bool ImplMutex::trylock() { return impl->trylock(); }

class AutoLock
{
public:
    AutoLock(ImplMutex& m) : mutex(&m) { mutex->lock(); }
    ~AutoLock() { mutex->unlock(); }
protected:
    ImplMutex* mutex;
private:
    AutoLock(const AutoLock&); // disabled
    AutoLock& operator = (const AutoLock&); // disabled
};
#endif

static ImplMutex _mutex;

static int LockCallBack(void **mutex, AVLockOp op)
{
    ImplMutex* localMutex = reinterpret_cast<ImplMutex*>(*mutex);
    switch (op)
    {
        case AV_LOCK_CREATE:
            localMutex = new ImplMutex();
            if (!localMutex)
                return 1;
            *mutex = localMutex;
            if (!*mutex)
                return 1;
        break;

        case AV_LOCK_OBTAIN:
            localMutex->lock();
        break;

        case AV_LOCK_RELEASE:
            localMutex->unlock();
        break;

        case AV_LOCK_DESTROY:
            delete localMutex;
            localMutex = NULL;
            *mutex = NULL;
        break;
    }
    return 0;
}


static void ffmpeg_log_callback(void *ptr, int level, const char *fmt, va_list vargs)
{
    static bool skip_header = false;
    static int prev_level = -1;
    CV_UNUSED(ptr);
    if (!skip_header || level != prev_level) printf("[OPENCV:FFMPEG:%02d] ", level);
    vprintf(fmt, vargs);
    size_t fmt_len = strlen(fmt);
    skip_header = fmt_len > 0 && fmt[fmt_len - 1] != '\n';
    prev_level = level;
}

class InternalFFMpegRegister
{
public:
    static void init()
    {
        AutoLock lock(_mutex);
        static InternalFFMpegRegister instance;
    }
    InternalFFMpegRegister()
    {
#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 13, 0)
        avformat_network_init();
#endif

        /* register all codecs, demux and protocols */
        av_register_all();

        /* register a callback function for synchronization */
        av_lockmgr_register(&LockCallBack);

#ifndef NO_GETENV
        char* debug_option = getenv("OPENCV_FFMPEG_DEBUG");
        if (debug_option != NULL)
        {
            av_log_set_level(AV_LOG_VERBOSE);
            av_log_set_callback(ffmpeg_log_callback);
        }
        else
#endif
        {
            av_log_set_level(AV_LOG_ERROR);
        }
    }
    ~InternalFFMpegRegister()
    {
        av_lockmgr_register(NULL);
    }
};


void split(const char *cmd, std::vector<std::string> &tokens_out) {
    std::string string_in(cmd);
    std::istringstream iss(string_in);
    std::string token;

    char delim = ' ';

    while (std::getline(iss, token, delim)) {
        tokens_out.push_back(token);
    }
}


///////////////// FFMPEG CvVideoWriter implementation //////////////////////////
struct CvVideoWriter_FFMPEG
{
    bool open( const char* filename, const char *codec_name,
               double fps, int width, int height, const char *ffmpegcmd);
    void close();
    bool writeFrame( const unsigned char* data, int step, int width, int height, int cn, int origin );

    void init();

    AVOutputFormat  * fmt;
    AVFormatContext * oc;
    uint8_t         * outbuf;
    uint32_t          outbuf_size;
    FILE            * outfile;
    AVFrame         * picture;
    AVFrame         * input_picture;
    uint8_t         * picbuf;
    AVStream        * video_st;
    int               input_pix_fmt;
    unsigned char   * aligned_input;
    size_t            aligned_input_size;
    int               frame_width, frame_height;
    int               frame_idx;
    bool              ok;
    struct SwsContext *img_convert_ctx;
};

static const char * icvFFMPEGErrStr(int err)
{
#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 2, 0)
    switch(err) {
    case AVERROR_BSF_NOT_FOUND:
        return "Bitstream filter not found";
    case AVERROR_DECODER_NOT_FOUND:
        return "Decoder not found";
    case AVERROR_DEMUXER_NOT_FOUND:
        return "Demuxer not found";
    case AVERROR_ENCODER_NOT_FOUND:
        return "Encoder not found";
    case AVERROR_EOF:
        return "End of file";
    case AVERROR_EXIT:
        return "Immediate exit was requested; the called function should not be restarted";
    case AVERROR_FILTER_NOT_FOUND:
        return "Filter not found";
    case AVERROR_INVALIDDATA:
        return "Invalid data found when processing input";
    case AVERROR_MUXER_NOT_FOUND:
        return "Muxer not found";
    case AVERROR_OPTION_NOT_FOUND:
        return "Option not found";
    case AVERROR_PATCHWELCOME:
        return "Not yet implemented in FFmpeg, patches welcome";
    case AVERROR_PROTOCOL_NOT_FOUND:
        return "Protocol not found";
    case AVERROR_STREAM_NOT_FOUND:
        return "Stream not found";
    default:
        break;
    }
#else
    switch(err) {
    case AVERROR_NUMEXPECTED:
        return "Incorrect filename syntax";
    case AVERROR_INVALIDDATA:
        return "Invalid data in header";
    case AVERROR_NOFMT:
        return "Unknown format";
    case AVERROR_IO:
        return "I/O error occurred";
    case AVERROR_NOMEM:
        return "Memory allocation error";
    default:
        break;
    }
#endif

    return "Unspecified error";
}

void CvVideoWriter_FFMPEG::init()
{
    fmt = 0;
    oc = 0;
    outbuf = 0;
    outbuf_size = 0;
    outfile = 0;
    picture = 0;
    input_picture = 0;
    picbuf = 0;
    video_st = 0;
    input_pix_fmt = 0;
    aligned_input = NULL;
    aligned_input_size = 0;
    img_convert_ctx = 0;
    frame_width = frame_height = 0;
    frame_idx = 0;
    ok = false;
}

/**
 * the following function is a modified version of code
 * found in ffmpeg-0.4.9-pre1/output_example.c
 */
static AVFrame * icv_alloc_picture_FFMPEG(int pix_fmt, int width, int height, bool alloc)
{
    AVFrame * picture;
    uint8_t * picture_buf = 0;
    int size;

#if LIBAVCODEC_BUILD >= (LIBAVCODEC_VERSION_MICRO >= 100 \
    ? CALC_FFMPEG_VERSION(55, 45, 101) : CALC_FFMPEG_VERSION(55, 28, 1))
    picture = av_frame_alloc();
#else
    picture = avcodec_alloc_frame();
#endif
    if (!picture)
        return NULL;

    picture->format = pix_fmt;
    picture->width = width;
    picture->height = height;

    size = _opencv_ffmpeg_av_image_get_buffer_size( (AVPixelFormat) pix_fmt, width, height);
    if(alloc){
        picture_buf = (uint8_t *) malloc(size);
        if (!picture_buf)
        {
            av_free(picture);
            return NULL;
        }
        _opencv_ffmpeg_av_image_fill_arrays(picture, picture_buf,
                       (AVPixelFormat) pix_fmt, width, height);
    }

    return picture;
}

/* add a video output stream to the container */
static AVStream *icv_add_video_stream_FFMPEG(AVFormatContext *oc,
                                             CV_CODEC_ID codec_id,
                                             int w, int h, int bitrate,
                                             double fps, int pixel_format)
{
    AVCodecContext *c;
    AVStream *st;
    int frame_rate, frame_rate_base;
    AVCodec *codec;

#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 10, 0)
    st = avformat_new_stream(oc, 0);
#else
    st = av_new_stream(oc, 0);
#endif

    if (!st) {
        CV_WARN("Could not allocate stream");
        return NULL;
    }

#if LIBAVFORMAT_BUILD > 4628
    c = st->codec;
#else
    c = &(st->codec);
#endif

#if LIBAVFORMAT_BUILD > 4621
    c->codec_id = av_guess_codec(oc->oformat, NULL, oc->filename, NULL, AVMEDIA_TYPE_VIDEO);
#else
    c->codec_id = oc->oformat->video_codec;
#endif

    if(codec_id != CV_CODEC(CODEC_ID_NONE)){
        c->codec_id = codec_id;
    }

    //if(codec_tag) c->codec_tag=codec_tag;
    codec = avcodec_find_encoder(c->codec_id);

    c->codec_type = AVMEDIA_TYPE_VIDEO;

#if LIBAVCODEC_BUILD >= CALC_FFMPEG_VERSION(54,25,0)
    // Set per-codec defaults
    AVCodecID c_id = c->codec_id;
    avcodec_get_context_defaults3(c, codec);
    // avcodec_get_context_defaults3 erases codec_id for some reason
    c->codec_id = c_id;
#endif

    /* put sample parameters */
    int64_t lbit_rate = (int64_t)bitrate;
    lbit_rate += (bitrate / 2);
    lbit_rate = fmin(lbit_rate, (int64_t)INT_MAX);
    c->bit_rate = lbit_rate;

    // took advice from
    // http://ffmpeg-users.933282.n4.nabble.com/warning-clipping-1-dct-coefficients-to-127-127-td934297.html
    c->qmin = 3;

    /* resolution must be a multiple of two */
    c->width = w;
    c->height = h;

    /* time base: this is the fundamental unit of time (in seconds) in terms
       of which frame timestamps are represented. for fixed-fps content,
       timebase should be 1/framerate and timestamp increments should be
       identically 1. */
    frame_rate=(int)(fps+0.5);
    frame_rate_base=1;
    while (fabs(((double)frame_rate/frame_rate_base) - fps) > 0.001){
        frame_rate_base*=10;
        frame_rate=(int)(fps*frame_rate_base + 0.5);
    }
#if LIBAVFORMAT_BUILD > 4752
    c->time_base.den = frame_rate;
    c->time_base.num = frame_rate_base;
    /* adjust time base for supported framerates */
    if(codec && codec->supported_framerates){
        const AVRational *p= codec->supported_framerates;
        AVRational req = {frame_rate, frame_rate_base};
        const AVRational *best=NULL;
        AVRational best_error= {INT_MAX, 1};
        for(; p->den!=0; p++){
            AVRational error= av_sub_q(req, *p);
            if(error.num <0) error.num *= -1;
            if(av_cmp_q(error, best_error) < 0){
                best_error= error;
                best= p;
            }
        }
        if (best == NULL)
            return NULL;
        c->time_base.den= best->num;
        c->time_base.num= best->den;
    }
#else
    c->frame_rate = frame_rate;
    c->frame_rate_base = frame_rate_base;
#endif

    c->gop_size = 12; /* emit one intra frame every twelve frames at most */
    c->pix_fmt = (AVPixelFormat) pixel_format;

    if (c->codec_id == CV_CODEC(CODEC_ID_MPEG2VIDEO)) {
        c->max_b_frames = 2;
    }
    if (c->codec_id == CV_CODEC(CODEC_ID_MPEG1VIDEO) || c->codec_id == CV_CODEC(CODEC_ID_MSMPEG4V3)){
        /* needed to avoid using macroblocks in which some coeffs overflow
           this doesn't happen with normal video, it just happens here as the
           motion of the chroma plane doesn't match the luma plane */
        /* avoid FFMPEG warning 'clipping 1 dct coefficients...' */
        c->mb_decision=2;
    }

#if LIBAVUTIL_BUILD > CALC_FFMPEG_VERSION(51,11,0)
    /* Some settings for libx264 encoding, restore dummy values for gop_size
     and qmin since they will be set to reasonable defaults by the libx264
     preset system. Also, use a crf encode with the default quality rating,
     this seems easier than finding an appropriate default bitrate. */
    if (c->codec_id == AV_CODEC_ID_H264) {
      c->gop_size = -1;
      c->qmin = -1;
      c->bit_rate = 0;
//      if (c->priv_data) {
//          av_opt_set(c->priv_data, "crf", "23", 0);
//      }
    }
#endif

#if LIBAVCODEC_VERSION_INT>0x000409
    // some formats want stream headers to be separate
    if(oc->oformat->flags & AVFMT_GLOBALHEADER)
    {
#if LIBAVCODEC_BUILD > CALC_FFMPEG_VERSION(56, 35, 0)
        c->flags |= AV_CODEC_FLAG_GLOBAL_HEADER;
#else
        c->flags |= CODEC_FLAG_GLOBAL_HEADER;
#endif
    }
#endif

#if LIBAVCODEC_BUILD >= CALC_FFMPEG_VERSION(52, 42, 0)
#if defined(_MSC_VER)
    AVRational avg_frame_rate = {frame_rate, frame_rate_base};
    st->avg_frame_rate = avg_frame_rate;
#else
    st->avg_frame_rate = (AVRational){frame_rate, frame_rate_base};
#endif
#endif
#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(55, 20, 0)
    st->time_base = c->time_base;
#endif

    return st;
}

static const int OPENCV_NO_FRAMES_WRITTEN_CODE = 1000;

static int icv_av_write_frame_FFMPEG( AVFormatContext * oc, AVStream * video_st,
#if LIBAVCODEC_BUILD >= CALC_FFMPEG_VERSION(54, 1, 0)
                                      uint8_t *, uint32_t,
#else
                                      uint8_t * outbuf, uint32_t outbuf_size,
#endif
                                      AVFrame * picture )
{
#if LIBAVFORMAT_BUILD > 4628
    AVCodecContext * c = video_st->codec;
#else
    AVCodecContext * c = &(video_st->codec);
#endif
    int ret = OPENCV_NO_FRAMES_WRITTEN_CODE;

#if LIBAVFORMAT_BUILD < CALC_FFMPEG_VERSION(57, 0, 0)
    if (oc->oformat->flags & AVFMT_RAWPICTURE)
    {
        /* raw video case. The API will change slightly in the near
           futur for that */
        AVPacket pkt;
        av_init_packet(&pkt);

        pkt.flags |= PKT_FLAG_KEY;
        pkt.stream_index= video_st->index;
        pkt.data= (uint8_t *)picture;
        pkt.size= sizeof(AVPicture);

        ret = av_write_frame(oc, &pkt);
    }
    else
#endif
    {
        /* encode the image */
        AVPacket pkt;
        av_init_packet(&pkt);
#if LIBAVCODEC_BUILD >= CALC_FFMPEG_VERSION(54, 1, 0)
        int got_output = 0;
        pkt.data = NULL;
        pkt.size = 0;
        ret = avcodec_encode_video2(c, &pkt, picture, &got_output);
        if (ret < 0)
            ;
        else if (got_output) {
            if (pkt.pts != (int64_t)AV_NOPTS_VALUE)
                pkt.pts = av_rescale_q(pkt.pts, c->time_base, video_st->time_base);
            if (pkt.dts != (int64_t)AV_NOPTS_VALUE)
                pkt.dts = av_rescale_q(pkt.dts, c->time_base, video_st->time_base);
            if (pkt.duration)
                pkt.duration = av_rescale_q(pkt.duration, c->time_base, video_st->time_base);
            pkt.stream_index= video_st->index;
            ret = av_write_frame(oc, &pkt);
            _opencv_ffmpeg_av_packet_unref(&pkt);
        }
        else
            ret = OPENCV_NO_FRAMES_WRITTEN_CODE;
#else
        int out_size = avcodec_encode_video(c, outbuf, outbuf_size, picture);
        /* if zero size, it means the image was buffered */
        if (out_size > 0) {
#if LIBAVFORMAT_BUILD > 4752
            if(c->coded_frame->pts != (int64_t)AV_NOPTS_VALUE)
                pkt.pts = av_rescale_q(c->coded_frame->pts, c->time_base, video_st->time_base);
#else
            pkt.pts = c->coded_frame->pts;
#endif
            if(c->coded_frame->key_frame)
                pkt.flags |= PKT_FLAG_KEY;
            pkt.stream_index= video_st->index;
            pkt.data= outbuf;
            pkt.size= out_size;

            /* write the compressed frame in the media file */
            ret = av_write_frame(oc, &pkt);
        }
#endif
    }
    return ret;
}

/// write a frame with FFMPEG
bool CvVideoWriter_FFMPEG::writeFrame( const unsigned char* data, int step, int width, int height, int cn, int origin )
{
    // check parameters
    if (input_pix_fmt == AV_PIX_FMT_BGR24) {
        if (cn != 3) {
            return false;
        }
    }
    else if (input_pix_fmt == AV_PIX_FMT_GRAY8) {
        if (cn != 1) {
            return false;
        }
    }
    else {
        assert(false);
    }

    if( (width & -2) != frame_width || (height & -2) != frame_height || !data )
        return false;
    width = frame_width;
    height = frame_height;

    // typecast from opaque data type to implemented struct
#if LIBAVFORMAT_BUILD > 4628
    AVCodecContext *c = video_st->codec;
#else
    AVCodecContext *c = &(video_st->codec);
#endif

    // FFmpeg contains SIMD optimizations which can sometimes read data past
    // the supplied input buffer.
    // Related info: https://trac.ffmpeg.org/ticket/6763
    // 1. To ensure that doesn't happen, we pad the step to a multiple of 32
    // (that's the minimal alignment for which Valgrind doesn't raise any warnings).
    // 2. (dataend - SIMD_SIZE) and (dataend + SIMD_SIZE) is from the same 4k page
    const int CV_STEP_ALIGNMENT = 32;
    const size_t CV_SIMD_SIZE = 32;
    const size_t CV_PAGE_MASK = ~(4096 - 1);
    const unsigned char* dataend = data + ((size_t)height * step);
    if (step % CV_STEP_ALIGNMENT != 0 ||
        (((size_t)dataend - CV_SIMD_SIZE) & CV_PAGE_MASK) != (((size_t)dataend + CV_SIMD_SIZE) & CV_PAGE_MASK))
    {
        int aligned_step = (step + CV_STEP_ALIGNMENT - 1) & ~(CV_STEP_ALIGNMENT - 1);

        size_t new_size = (aligned_step * height + CV_SIMD_SIZE);

        if (!aligned_input || aligned_input_size < new_size)
        {
            if (aligned_input)
                av_freep(&aligned_input);
            aligned_input_size = new_size;
            aligned_input = (unsigned char*)av_mallocz(aligned_input_size);
        }

        if (origin == 1)
            for( int y = 0; y < height; y++ )
                memcpy(aligned_input + y*aligned_step, data + (height-1-y)*step, step);
        else
            for( int y = 0; y < height; y++ )
                memcpy(aligned_input + y*aligned_step, data + y*step, step);

        data = aligned_input;
        step = aligned_step;
    }

    if ( c->pix_fmt != input_pix_fmt ) {
        assert( input_picture );
        // let input_picture point to the raw data buffer of 'image'
        _opencv_ffmpeg_av_image_fill_arrays(input_picture, (uint8_t *) data,
                       (AVPixelFormat)input_pix_fmt, width, height);
        input_picture->linesize[0] = step;

        if( !img_convert_ctx )
        {
            img_convert_ctx = sws_getContext(width,
                                             height,
                                             (AVPixelFormat)input_pix_fmt,
                                             c->width,
                                             c->height,
                                             c->pix_fmt,
                                             SWS_BICUBIC,
                                             NULL, NULL, NULL);
            if( !img_convert_ctx )
                return false;
        }

        if ( sws_scale(img_convert_ctx, input_picture->data,
                       input_picture->linesize, 0,
                       height,
                       picture->data, picture->linesize) < 0 )
            return false;
    }
    else{
        _opencv_ffmpeg_av_image_fill_arrays(picture, (uint8_t *) data,
                       (AVPixelFormat)input_pix_fmt, width, height);
        picture->linesize[0] = step;
    }

    picture->pts = frame_idx;
    bool ret = icv_av_write_frame_FFMPEG( oc, video_st, outbuf, outbuf_size, picture) >= 0;
    frame_idx++;

    return ret;
}

/// close video output stream and free associated memory
void CvVideoWriter_FFMPEG::close()
{
    // nothing to do if already released
    if ( !picture )
        return;

    /* no more frame to compress. The codec has a latency of a few
       frames if using B frames, so we get the last frames by
       passing the same picture again */
    // TODO -- do we need to account for latency here?

    /* write the trailer, if any */
    if(ok && oc)
    {
#if LIBAVFORMAT_BUILD < CALC_FFMPEG_VERSION(57, 0, 0)
        if (!(oc->oformat->flags & AVFMT_RAWPICTURE))
#endif
        {
            for(;;)
            {
                int ret = icv_av_write_frame_FFMPEG( oc, video_st, outbuf, outbuf_size, NULL);
                if( ret == OPENCV_NO_FRAMES_WRITTEN_CODE || ret < 0 )
                    break;
            }
        }
        av_write_trailer(oc);
    }

    if( img_convert_ctx )
    {
        sws_freeContext(img_convert_ctx);
        img_convert_ctx = 0;
    }

    // free pictures
#if LIBAVFORMAT_BUILD > 4628
    if( video_st->codec->pix_fmt != input_pix_fmt)
#else
    if( video_st->codec.pix_fmt != input_pix_fmt)
#endif
    {
        if(picture->data[0])
            free(picture->data[0]);
        picture->data[0] = 0;
    }
    av_free(picture);

    if (input_picture)
        av_free(input_picture);

    /* close codec */
#if LIBAVFORMAT_BUILD > 4628
    avcodec_close(video_st->codec);
#else
    avcodec_close(&(video_st->codec));
#endif

    av_free(outbuf);

    if (oc)
    {
        if (!(fmt->flags & AVFMT_NOFILE))
        {
            /* close the output file */

#if LIBAVCODEC_VERSION_INT < ((52<<16)+(123<<8)+0)
#if LIBAVCODEC_VERSION_INT >= ((51<<16)+(49<<8)+0)
            url_fclose(oc->pb);
#else
            url_fclose(&oc->pb);
#endif
#else
            avio_close(oc->pb);
#endif

        }

        /* free the stream */
        avformat_free_context(oc);
    }

    av_freep(&aligned_input);

    init();
}

#define CV_PRINTABLE_CHAR(ch) ((ch) < 32 ? '?' : (ch))

/// Create a video writer object that uses FFMPEG
bool CvVideoWriter_FFMPEG::open( const char * filename, const char *codec_name,
                                 double fps, int width, int height, const char *ffmpegcmd )
{
    InternalFFMpegRegister::init();
    int err, codec_pix_fmt;
    double bitrate_scale = 1;

    close();

    // check arguments
    if( !filename )
        return false;
    if(fps <= 0)
        return false;

    // we allow frames of odd width or height, but in this case we truncate
    // the rightmost column/the bottom row. Probably, this should be handled more elegantly,
    // but some internal functions inside FFMPEG swscale require even width/height.
    width &= -2;
    height &= -2;
    if( width <= 0 || height <= 0 )
        return false;


#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 2, 0)
    fmt = av_guess_format(NULL, filename, NULL);
#else
    fmt = guess_format(NULL, filename, NULL);
#endif

    if (!fmt)
        return false;

    input_pix_fmt = AV_PIX_FMT_BGR24;


    AVCodec *codecc = avcodec_find_encoder_by_name(codec_name);
    if (!codecc) {
        fprintf(stderr, "Codec '%s' not found\n", codec_name);
        return false;
    }

    CV_CODEC_ID codec_id = codecc->id;

    // alloc memory for context
#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 2, 0)
    oc = avformat_alloc_context();
#else
    oc = av_alloc_format_context();
#endif
    assert (oc);

    /* set file name */
    oc->oformat = fmt;
    snprintf(oc->filename, sizeof(oc->filename), "%s", filename);

    /* set some options */
    oc->max_delay = (int)(0.7*AV_TIME_BASE);  /* This reduces buffer underrun warnings with MPEG */

    // set a few optimal pixel formats for lossless codecs of interest..
    switch (codec_id) {
#if LIBAVCODEC_VERSION_INT>((50<<16)+(1<<8)+0)
    case CV_CODEC(CODEC_ID_JPEGLS):
        // BGR24 or GRAY8 depending on is_color...
        // supported: bgr24 rgb24 gray gray16le
        // as of version 3.4.1
        codec_pix_fmt = input_pix_fmt;
        break;
#endif
    case CV_CODEC(CODEC_ID_HUFFYUV):
        // supported: yuv422p rgb24 bgra
        // as of version 3.4.1
        switch(input_pix_fmt)
        {
            case AV_PIX_FMT_RGB24:
            case AV_PIX_FMT_BGRA:
                codec_pix_fmt = input_pix_fmt;
                break;
            case AV_PIX_FMT_BGR24:
                codec_pix_fmt = AV_PIX_FMT_RGB24;
                break;
            default:
                codec_pix_fmt = AV_PIX_FMT_YUV422P;
                break;
        }
        break;
    case CV_CODEC(CODEC_ID_PNG):
        // supported: rgb24 rgba rgb48be rgba64be pal8 gray ya8 gray16be ya16be monob
        // as of version 3.4.1
        switch(input_pix_fmt)
        {
            case AV_PIX_FMT_GRAY8:
            case AV_PIX_FMT_GRAY16BE:
            case AV_PIX_FMT_RGB24:
            case AV_PIX_FMT_BGRA:
                codec_pix_fmt = input_pix_fmt;
                break;
            case AV_PIX_FMT_GRAY16LE:
                codec_pix_fmt = AV_PIX_FMT_GRAY16BE;
                break;
            case AV_PIX_FMT_BGR24:
                codec_pix_fmt = AV_PIX_FMT_RGB24;
                break;
            default:
                codec_pix_fmt = AV_PIX_FMT_YUV422P;
                break;
        }
        break;
    case CV_CODEC(CODEC_ID_FFV1):
        // supported: MANY
        // as of version 3.4.1
        switch(input_pix_fmt)
        {
            case AV_PIX_FMT_GRAY8:
            case AV_PIX_FMT_GRAY16LE:
#ifdef AV_PIX_FMT_BGR0
            case AV_PIX_FMT_BGR0:
#endif
            case AV_PIX_FMT_BGRA:
                codec_pix_fmt = input_pix_fmt;
                break;
            case AV_PIX_FMT_GRAY16BE:
                codec_pix_fmt = AV_PIX_FMT_GRAY16LE;
                break;
            case AV_PIX_FMT_BGR24:
            case AV_PIX_FMT_RGB24:
#ifdef AV_PIX_FMT_BGR0
                codec_pix_fmt = AV_PIX_FMT_BGR0;
#else
                codec_pix_fmt = AV_PIX_FMT_BGRA;
#endif
                break;
            default:
                codec_pix_fmt = AV_PIX_FMT_YUV422P;
                break;
        }
        break;
    case CV_CODEC(CODEC_ID_MJPEG):
    case CV_CODEC(CODEC_ID_LJPEG):
        codec_pix_fmt = AV_PIX_FMT_YUVJ420P;
        bitrate_scale = 3;
        break;
    case CV_CODEC(CODEC_ID_RAWVIDEO):
        switch(input_pix_fmt)
        {
            case AV_PIX_FMT_GRAY8:
            case AV_PIX_FMT_GRAY16LE:
            case AV_PIX_FMT_GRAY16BE:
                codec_pix_fmt = input_pix_fmt;
                break;
            default:
                codec_pix_fmt = AV_PIX_FMT_YUV420P;
                break;
        }
        break;
    default:
        // good for lossy formats, MPEG, etc.
        codec_pix_fmt = AV_PIX_FMT_YUV420P;
        break;
    }

    double bitrate = MIN(bitrate_scale*fps*width*height, (double)INT_MAX/2);

    // TODO -- safe to ignore output audio stream?
    video_st = icv_add_video_stream_FFMPEG(oc, codec_id,
                                           width, height, (int)(bitrate + 0.5),
                                           fps, codec_pix_fmt);

    /* set the output parameters (must be done even if no
   parameters). */
#if LIBAVFORMAT_BUILD < CALC_FFMPEG_VERSION(53, 2, 0)
    if (av_set_parameters(oc, NULL) < 0) {
        return false;
    }
#endif

#if 0
#if FF_API_DUMP_FORMAT
    dump_format(oc, 0, filename, 1);
#else
    av_dump_format(oc, 0, filename, 1);
#endif
#endif

    /* now that all the parameters are set, we can open the audio and
     video codecs and allocate the necessary encode buffers */
    if (!video_st){
        return false;
    }

    AVCodec *codec;
    AVCodecContext *c;

#if LIBAVFORMAT_BUILD > 4628
    c = (video_st->codec);
#else
    c = &(video_st->codec);
#endif

    c->codec_tag = NULL;
    /* find the video encoder */
    codec = avcodec_find_encoder(c->codec_id);
    if (!codec) {
        fprintf(stderr, "Could not find encoder for codec id %d: %s\n", c->codec_id, icvFFMPEGErrStr(
        #if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(53, 2, 0)
                AVERROR_ENCODER_NOT_FOUND
        #else
                -1
        #endif
                ));
        return false;
    }

    int64_t lbit_rate = (int64_t)c->bit_rate;
    lbit_rate += (bitrate / 2);
    lbit_rate = fmin(lbit_rate, (int64_t)INT_MAX);
    c->bit_rate_tolerance = (int)lbit_rate;
    c->bit_rate = (int)lbit_rate;

    std::vector<std::string> ffmpegargs;
    split(ffmpegcmd, ffmpegargs);
    AVDictionary *opt = NULL;
    for (int i = 0; i+1 < ffmpegargs.size(); i+=2) {
        av_dict_set(&opt, ffmpegargs[i].data() + 1, ffmpegargs[i + 1].data(), 0);

    }

    /* open the codec */
    if ((err=
#if LIBAVCODEC_VERSION_INT >= ((53<<16)+(8<<8)+0)
        avcodec_open2(c, codec, &opt)
#else
         avcodec_open(c, codec)
#endif
         ) < 0) {
        av_dict_free(&opt);
        fprintf(stderr, "Could not open codec '%s': %s\n", codec->name, icvFFMPEGErrStr(err));
        return false;
    }
    av_dict_free(&opt);
    outbuf = NULL;


#if LIBAVFORMAT_BUILD < CALC_FFMPEG_VERSION(57, 0, 0)
    if (!(oc->oformat->flags & AVFMT_RAWPICTURE))
#endif
    {
        /* allocate output buffer */
        /* assume we will never get codec output with more than 4 bytes per pixel... */
        outbuf_size = width*height*4;
        outbuf = (uint8_t *) av_malloc(outbuf_size);
    }

    bool need_color_convert;
    need_color_convert = (c->pix_fmt != input_pix_fmt);

    /* allocate the encoded raw picture */
    picture = icv_alloc_picture_FFMPEG(c->pix_fmt, c->width, c->height, need_color_convert);
    if (!picture) {
        return false;
    }

    /* if the output format is not our input format, then a temporary
   picture of the input format is needed too. It is then converted
   to the required output format */
    input_picture = NULL;
    if ( need_color_convert ) {
        input_picture = icv_alloc_picture_FFMPEG(input_pix_fmt, c->width, c->height, false);
        if (!input_picture) {
            return false;
        }
    }

    /* open the output file, if needed */
    if (!(fmt->flags & AVFMT_NOFILE)) {
#if LIBAVFORMAT_BUILD < CALC_FFMPEG_VERSION(53, 2, 0)
        if (url_fopen(&oc->pb, filename, URL_WRONLY) < 0)
#else
            if (avio_open(&oc->pb, filename, AVIO_FLAG_WRITE) < 0)
#endif
            {
            return false;
        }
    }

#if LIBAVFORMAT_BUILD >= CALC_FFMPEG_VERSION(52, 111, 0)
    /* write the stream header, if any */
    err=avformat_write_header(oc, NULL);
#else
    err=av_write_header( oc );
#endif

    if(err < 0)
    {
        close();
        remove(filename);
        return false;
    }
    frame_width = width;
    frame_height = height;
    frame_idx = 0;
    ok = true;

    return true;
}


CvVideoWriter_FFMPEG* cvCreateVideoWriter_FFMPEG( const char* filename, const char *codec_name, double fps,
                                                  int width, int height, const char *ffmpegcmd) {
    CvVideoWriter_FFMPEG* writer = (CvVideoWriter_FFMPEG*)malloc(sizeof(*writer));
    if (!writer)
        return 0;
    writer->init();
    if( writer->open( filename, codec_name, fps, width, height, ffmpegcmd))
        return writer;
    writer->close();
    free(writer);
    return 0;
}

void cvReleaseVideoWriter_FFMPEG( CvVideoWriter_FFMPEG** writer ) {
    if( writer && *writer ) {
        (*writer)->close();
        free(*writer);
        *writer = 0;
    }
}


int cvWriteFrame_FFMPEG( CvVideoWriter_FFMPEG* writer,
                         const unsigned char* data, int step,
                         int width, int height, int cn, int origin) {
    return writer->writeFrame(data, step, width, height, cn, origin);
}

#endif //CVFFMPEG_CAPFFMPEG
