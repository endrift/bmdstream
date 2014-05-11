#!/bin/bash
GST="gst-launch-1.0 -v"

CONNECTION=1
MODE=18

SRC="decklinksrc mode=$MODE connection=$CONNECTION name=src"

AUDIO_EXTRA="autoaudiosrc ! queue ! audioconvert ! audioresample ! audio/x-raw, rate=44100 ! adder."
AUDIO_ENC="lamemp3enc target=bitrate ! mpegaudioparse ! queue ! mux."
AUDIO_DISP="queue ! autoaudiosink sync=false"
AUDIO_BOTH="tee name=audio ! $AUDIO_ENC audio. ! $AUDIO_DISP"
AUDIO_OUT=$AUDIO_BOTH
AUDIO="src. ! queue ! audioconvert ! interaudiosink interaudiosrc ! audioresample ! audio/x-raw, rate=44100 ! adder name=adder ! $AUDIO_OUT"

VIDEO_ENC="videoconvert ! x264enc threads=4 speed-preset=faster tune=zerolatency bitrate=3072 ! h264parse ! queue ! mux."
VIDEO_DISP="videoconvert ! autovideosink sync=false"
VIDEO_BOTH="tee name=video ! $VIDEO_ENC video. ! $VIDEO_DISP"
VIDEO_OUT=$VIDEO_BOTH
VIDEO="src. ! queue ! $VIDEO_OUT"

MUX="flvmux streamable=true name=mux ! filesink location=test.flv"

$GST $SRC $AUDIO $AUDIO_EXTRA $VIDEO $MUX
