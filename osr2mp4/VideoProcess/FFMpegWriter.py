import os
import subprocess as sp
import numpy as np

class FFMpegWriter:
    def __init__(
        self,
        ffmpeg_binary,
        filename,
        size,
        fps,
        codec="libx264",
        audiofile=None,
        audiocodec="aac",
        preset="medium",
        bitrate=None,
        with_mask=False,
        logfile=None,
        threads=None,
        ffmpeg_params=None,
        pixel_format=None,
    ):
        if logfile is None:
            logfile = sp.PIPE
        self.logfile = logfile
        self.filename = filename
        self.codec = codec
        self.ext = self.filename.split(".")[-1]
        if not pixel_format:
            pixel_format = "rgba" if with_mask else "rgb24"

        # order is important
        cmd = [
            ffmpeg_binary,
            "-y",
            "-loglevel",
            "error" if logfile == sp.PIPE else "info",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            "%dx%d" % (size[0], size[1]),
            "-pix_fmt",
            pixel_format,
            "-r",
            "%.02f" % fps,
            "-an",
            "-i",
            "-",
        ]
        if audiofile is not None:
            cmd.extend(["-i", audiofile, "-acodec", audiocodec])
        cmd.extend(["-vcodec", codec, "-preset", preset, "-crf", "23"])
        if ffmpeg_params is not None:
            cmd.extend(ffmpeg_params)
        if bitrate is not None:
            cmd.extend(["-ab", bitrate])

        if threads is not None:
            cmd.extend(["-threads", str(threads)])

        #if (codec == "libx264") and (size[0] % 2 == 0) and (size[1] % 2 == 0):
        #    cmd.extend(["-pix_fmt", "yuv420p"])
        cmd.extend([filename])

        popen_params = {"stdout": sp.DEVNULL, "stderr": logfile, "stdin": sp.PIPE, "bufsize": 40960}

        # This was added so that no extra unwanted window opens on windows
        # when the child process is created
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

        self.proc = sp.Popen(cmd, **popen_params)

    def write_frame(self, img_array):
        """ Writes one frame in the file."""
        try:
            self.proc.stdin.write(img_array.tobytes())
        except IOError as err:
            _, ffmpeg_error = self.proc.communicate()
            if ffmpeg_error is not None:
                ffmpeg_error = ffmpeg_error.decode()
            else:
                # The error was redirected to a logfile with `write_logfile=True`,
                # so read the error from that file instead
                self.logfile.seek(0)
                ffmpeg_error = self.logfile.read()

            error = (
                f"{err}\n\nMoviePy error: FFMPEG encountered the following error while "
                f"writing file {self.filename}:\n\n {ffmpeg_error}"
            )

            if "Unknown encoder" in ffmpeg_error:
                error += (
                    "\n\nThe video export failed because FFMPEG didn't find the "
                    f"specified codec for video encoding {self.codec}. "
                    "Please install this codec or change the codec when calling "
                    "write_videofile.\nFor instance:\n"
                    "  >>> clip.write_videofile('myvid.webm', codec='libvpx')"
                )

            elif "incorrect codec parameters ?" in ffmpeg_error:
                error += (
                    "\n\nThe video export failed, possibly because the codec "
                    f"specified for the video {self.codec} is not compatible with "
                    f"the given extension {self.ext}.\n"
                    "Please specify a valid 'codec' argument in write_videofile.\n"
                    "This would be 'libx264' or 'mpeg4' for mp4, "
                    "'libtheora' for ogv, 'libvpx for webm.\n"
                    "Another possible reason is that the audio codec was not "
                    "compatible with the video codec. For instance, the video "
                    "extensions 'ogv' and 'webm' only allow 'libvorbis' (default) as a"
                    "video codec."
                )

            elif "bitrate not specified" in ffmpeg_error:

                error += (
                    "\n\nThe video export failed, possibly because the bitrate "
                    "specified was too high or too low for the video codec."
                )

            elif "Invalid encoder type" in ffmpeg_error:

                error += (
                    "\n\nThe video export failed because the codec "
                    "or file extension you provided is not suitable for video"
                )

            raise IOError(error)

    def release(self):
        if self.proc:
            self.proc.stdin.close()
            if self.proc.stderr is not None:
                self.proc.stderr.close()
            self.proc.wait()

            self.proc = None

    # Support the Context Manager protocol, to ensure that resources are cleaned up.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()