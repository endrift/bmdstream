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
		resample = Gst.ElementFactory.make('audioresample', None)
		capsfilter = Gst.ElementFactory.make('capsfilter', None)

		capsfilter.set_property('caps', Gst.caps_from_string('audio/x-raw, rate=44100'))

		self.add(resample)
		self.add(capsfilter)

		resample.link(capsfilter)

		self.add_pad(Gst.GhostPad.new('sink', resample.get_static_pad('sink')))
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

class AudioDisplay(Gst.Bin):
	def __init__(self):
		super(AudioDisplay, self).__init__()
		queue = Gst.ElementFactory.make('queue', None)
		sink = Gst.ElementFactory.make('autoaudiosink', None)

		sink.set_property('sync', False)

		self.add(queue)
		self.add(sink)

		queue.link(sink)

		self.add_pad(Gst.GhostPad.new('sink', queue.get_static_pad('sink')))

class VideoDisplay(Gst.Bin):
	def __init__(self):
		super(VideoDisplay, self).__init__()
		convert = Gst.ElementFactory.make('videoconvert', None)
		sink = Gst.ElementFactory.make('autovideosink', None)

		sink.set_property('sync', False)

		self.add(convert)
		self.add(sink)

		convert.link(sink)

		self.add_pad(Gst.GhostPad.new('sink', convert.get_static_pad('sink')))

class DeckLinkPipeline(Gst.Pipeline):
	def __init__(self):
		super(DeckLinkPipeline, self).__init__()
		src = Gst.ElementFactory.make('decklinksrc', None)
		src.set_property('connection', 1)
		src.set_property('mode', 18)

		aqueue = Gst.ElementFactory.make('queue', None)
		self.atee = Gst.ElementFactory.make('tee', None)
		vqueue = Gst.ElementFactory.make('queue', None)
		self.vtee = Gst.ElementFactory.make('tee', None)

		intersink = Gst.ElementFactory.make('interaudiosink')
		intersink.set_property('channel', 'ach')
		intersrc = Gst.ElementFactory.make('interaudiosrc')
		intersrc.set_property('channel', 'ach')

		self.adder = Gst.ElementFactory.make('adder')

		aconv = Gst.ElementFactory.make('audioconvert')
		ars = AudioResampler()

		self.add(src)
		self.add(aqueue)
		self.add(self.atee)
		self.add(vqueue)
		self.add(self.vtee)
		self.add(intersink)
		self.add(intersrc)
		self.add(self.adder)
		self.add(aconv)
		self.add(ars)

		src.link(aqueue)
		src.link(vqueue)

		aqueue.link(aconv)
		aconv.link(intersink)
		intersrc.link(ars)
		ars.link(self.adder)

		self.adder.link(self.atee)

		vqueue.link(self.vtee)

	def attach_mic(self):
		mic = Gst.ElementFactory.make('autoaudiosrc')
		mqueue = Gst.ElementFactory.make('queue')
		mrs = AudioResampler()

		self.add(mic)
		self.add(mqueue)
		self.add(mrs)

		mic.link(mqueue)
		mqueue.link(mrs)
		mrs.link(self.adder)


	def attach_flv_muxer(self):
		aenc = LameBin()
		venc = X264Bin()

		flvmux = Gst.ElementFactory.make ('flvmux', None)
		flvmux.set_property('streamable', True)

		filesink = Gst.ElementFactory.make('filesink', None)
		filesink.set_property('location', 'test.flv')

		self.add(aenc)
		self.add(venc)
		self.add(flvmux)
		self.add(filesink)

		self.atee.link(aenc)
		aenc.link(flvmux)

		self.vtee.link(venc)
		venc.link(flvmux)

		flvmux.link(filesink)

	def attach_display(self):
		aout = AudioDisplay()
		vout = VideoDisplay()

		self.add(aout)
		self.add(vout)

		self.atee.link(aout)
		self.vtee.link(vout)

pipeline = DeckLinkPipeline()
pipeline.attach_mic()
pipeline.attach_flv_muxer()
pipeline.attach_display()

pipeline.set_state(Gst.State.PLAYING)
loop = GObject.MainLoop()
loop.run()
