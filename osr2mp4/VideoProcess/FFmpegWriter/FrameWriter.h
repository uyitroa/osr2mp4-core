//
// Created by yuitora . on 13/08/2020.
//

#ifndef CVFFMPEG_FRAMEWRITER_H
#define CVFFMPEG_FRAMEWRITER_H

#include "cap_ffmpeg_legacy_api.h"
#include <stdint.h>
#include <vector>
#include <string>


class FrameWriter {
private:
    bool initialized = false;
public:
    CvVideoWriter_FFMPEG* framewriter;
    uint8_t *data;
    std::string error;
    int width;
    int height;
    double fps;
    int n_channel = 3;
    int step;

    FrameWriter();
    FrameWriter(const char* filename, const char *codec_name, double fps, int width, int height, const char *ffmpegcmd, uint8_t *buf);
    int write_frame();
    void close_video();
    bool is_opened();
    std::string geterror();
    ~FrameWriter();

};

std::vector<const char *> getcodecname();
std::vector<const char *> getcodeclongname();
std::vector<const char *> getaudiocodecname();
std::vector<const char *> getaudiocodeclongname();


#endif //CVFFMPEG_FRAMEWRITER_H
