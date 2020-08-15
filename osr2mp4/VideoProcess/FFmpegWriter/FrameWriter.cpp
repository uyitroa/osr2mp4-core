//
// Created by yuitora . on 13/08/2020.
//

#include "FrameWriter.h"
#include "cap_ffmpeg_impl.h"


FrameWriter::FrameWriter(const char *filename, const char *codec_name, double fps, int width, int height,
                            const char *ffmpegcmd, uint8_t *buf) {
    this->width = width;
    this->height = height;
    this->fps = fps;
    this->step = width * n_channel * sizeof(uint8_t);
    this->n_channel = 3;
    this->data = buf;
    for (int i = 0; i < width * height * n_channel; i++)
        this->data[i] = 0;

    char buferr[BUFSIZ];
    setbuf(stderr, buferr);

    framewriter = cvCreateVideoWriter_FFMPEG(filename, codec_name, fps, width, height, ffmpegcmd);

    error = std::string(buferr);
    if(framewriter)
        initialized = true;
}

int FrameWriter::write_frame() {
    if (!initialized)
        return 1;
    return framewriter->writeFrame(data, step, width, height, n_channel, 0);
}

void FrameWriter::close_video() {
    if (!initialized)
        return;
    cvReleaseVideoWriter_FFMPEG(&framewriter);
    //free(data);
    initialized = false;
}

FrameWriter::FrameWriter() = default;

bool FrameWriter::is_opened() {
    return initialized;
}

FrameWriter::~FrameWriter() {

}

std::string FrameWriter::geterror() {
    return error;
}


bool is_valid_codec(const char* codec_name) {
    AVCodec *codec = avcodec_find_encoder_by_name(codec_name);
    return codec != nullptr;
}

std::vector<const char *> getcodecname() {
    const AVCodec *current_codec = nullptr;
    void *i = 0;
    std::vector<const char *> codecname;
    current_codec = av_codec_iterate(&i);
    while(current_codec)
    {
        if (current_codec->type == AVMEDIA_TYPE_VIDEO) {
            if (is_valid_codec(current_codec->name)) {
                codecname.push_back(current_codec->name);
            }
        }
        current_codec = av_codec_iterate(&i);
    }
    return codecname;
}

std::vector<const char *> getcodeclongname() {
    const AVCodec *current_codec = nullptr;
    void *i = 0;
    std::vector<const char *> codecname;
    current_codec = av_codec_iterate(&i);
    while(current_codec)
    {
        if (current_codec->type == AVMEDIA_TYPE_VIDEO) {
            if (is_valid_codec(current_codec->name)) {
                codecname.push_back(current_codec->long_name);
            }
        }
        current_codec = av_codec_iterate(&i);
    }
    return codecname;
}



std::vector<const char *> getaudiocodecname() {
    const AVCodec *current_codec = nullptr;
    void *i = 0;
    std::vector<const char *> codecname;
    current_codec = av_codec_iterate(&i);
    while(current_codec)
    {
        if (current_codec->type == AVMEDIA_TYPE_AUDIO) {
            if (is_valid_codec(current_codec->name)) {
                codecname.push_back(current_codec->name);
            }
        }
        current_codec = av_codec_iterate(&i);
    }
    return codecname;
}

std::vector<const char *> getaudiocodeclongname() {
    const AVCodec *current_codec = nullptr;
    void *i = 0;
    std::vector<const char *> codecname;
    current_codec = av_codec_iterate(&i);
    while(current_codec)
    {
        if (current_codec->type == AVMEDIA_TYPE_AUDIO) {
            if (is_valid_codec(current_codec->name)) {
                codecname.push_back(current_codec->long_name);
            }
        }
        current_codec = av_codec_iterate(&i);
    }
    return codecname;
}
