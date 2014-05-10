#!/usr/bin/python3
import gi
import threading

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)

class AudioResampler(Gst.Bin):
	def __init__(self):
		super(AudioResampler, self).__init__()
		convert = Gst.ElementFactory.make('audioconvert', None)
		resample = Gst.ElementFactory.make('audioresample', None)
		capsfilter = Gst.ElementFactory.make('capsfilter', None)

		capsfilter.set_property('caps', Gst.caps_from_string('audio/x-raw, rate=44100'))

		self.add(convert)
		self.add(resample)
		self.add(capsfilter)

		convert.link(resample)
		resample.link(capsfilter)

		self.add_pad(Gst.GhostPad.new('sink', convert.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('src', capsfilter.get_static_pad('src')))

class LameBin(Gst.Bin):
	def __init__(self):
		super(LameBin, self).__init__()
		enc = Gst.ElementFactory.make('lamemp3enc', None)
		parse = Gst.ElementFactory.make('mpegaudioparse', None)
		queue = Gst.ElementFactory.make('queue', None)

		enc.set_property('target', 'bitrate')

		self.add(enc)
		self.add(parse)
		self.add(queue)

		enc.link(parse)
		parse.link(queue)

		self.add_pad(Gst.GhostPad.new('sink', enc.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('src', queue.get_static_pad('src')))

class X264Bin(Gst.Bin):
	def __init__(self):
		super(X264Bin, self).__init__()
		convert = Gst.ElementFactory.make('videoconvert', None)
		enc = Gst.ElementFactory.make('x264enc', None)
		parse = Gst.ElementFactory.make('h264parse', None)
		queue = Gst.ElementFactory.make('queue', None)

		enc.set_property('threads', 4)
		enc.set_property('speed-preset', 'faster')
		enc.set_property('tune', 'zerolatency')
		enc.set_property('bitrate', 3000)

		self.add(convert)
		self.add(enc)
		self.add(parse)
		self.add(queue)

		convert.link(enc)
		enc.link(parse)
		parse.link(queue)

		self.add_pad(Gst.GhostPad.new('sink', convert.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('src', queue.get_static_pad('src')))

pipeline = Gst.Pipeline()

src = Gst.ElementFactory.make('decklinksrc', None)
src.set_property('connection', 1)
src.set_property('mode', 18)

aqueue = Gst.ElementFactory.make('queue', None)
vqueue = Gst.ElementFactory.make('queue', None)

ars = AudioResampler()
aenc = LameBin()
venc = X264Bin()

mkvmux = Gst.ElementFactory.make ('matroskamux', None)

filesink = Gst.ElementFactory.make('filesink', None)
filesink.set_property('location', 'test.mkv')

pipeline.add(src)
pipeline.add(aqueue)
pipeline.add(vqueue)
pipeline.add(ars)
pipeline.add(aenc)
pipeline.add(venc)
pipeline.add(mkvmux)
pipeline.add(filesink)

src.link(aqueue)
src.link(vqueue)

aqueue.link(ars)
ars.link(aenc)
aenc.link(mkvmux)

vqueue.link(venc)
venc.link(mkvmux)

mkvmux.link(filesink)

pipeline.set_state(Gst.State.PLAYING)
loop = GObject.MainLoop()
loop.run()
