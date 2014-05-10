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

pipeline = Gst.Pipeline()

src = Gst.ElementFactory.make('decklinksrc', None)
src.set_property('connection', 1)
src.set_property('mode', 18)
pipeline.add(src)

aqueue = Gst.ElementFactory.make('queue', None)
pipeline.add(aqueue)

vqueue = Gst.ElementFactory.make('queue', None)
pipeline.add(vqueue)

ars = AudioResampler()
pipeline.add(ars)

asink = Gst.ElementFactory.make('autoaudiosink', None)
asink.set_property('sync', False)
#pipeline.add(asink)

vsink = Gst.ElementFactory.make('autovideosink', None)
vsink.set_property('sync', False)
#pipeline.add(vsink)

src.link(aqueue)
src.link(vqueue)

mkvmux = Gst.ElementFactory.make ('matroskamux', None)
pipeline.add(mkvmux)

aqueue.link(ars)
ars.link(mkvmux)
vqueue.link(mkvmux)

filesink = Gst.ElementFactory.make('filesink', None)
filesink.set_property('location', 'test.mkv')
pipeline.add(filesink)

mkvmux.link(filesink)

pipeline.set_state(Gst.State.PLAYING)
loop = GObject.MainLoop()
loop.run()
