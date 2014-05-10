#!/bin/bash
GST="gst-launch-1.0"

CONNECTION=1
MODE=18

SRC="decklinksrc mode=$MODE connection=$CONNECTION name=src"

AUDIO_ENC="lamemp3enc target=bitrate ! mpegaudioparse ! queue ! mux."
AUDIO_DISP="queue ! autoaudiosink sync=false"
AUDIO_BOTH="tee name=audio ! $AUDIO_ENC audio. ! $AUDIO_DISP"
AUDIO_OUT=$AUDIO_BOTH
AUDIO="src. ! queue ! audioconvert ! interaudiosink interaudiosrc ! audioresample ! audio/x-raw, rate=44100 ! $AUDIO_OUT"

VIDEO_ENC="x264enc threads=4 speed-preset=faster tune=zerolatency bitrate=3072 ! h264parse ! queue ! mux."
VIDEO_DISP="queue ! autovideosink sync=false"
VIDEO_BOTH="tee name=video ! $VIDEO_ENC video. ! $VIDEO_DISP"
VIDEO_OUT=$VIDEO_BOTH
VIDEO="src. ! queue ! videoconvert ! $VIDEO_OUT"

MUX="flvmux streamable=true name=mux ! filesink location=test.flv"

$GST $SRC $AUDIO $VIDEO $MUX
