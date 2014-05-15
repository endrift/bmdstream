from gi.repository import Gst

import os
import subprocess

output_registry = {}

def make_output(config, output):
	output_type = output_registry[output['type']]()
	for name, prop in output.items():
		if name in ['type', 'pipe']:
			continue
		output_type.set_property(name, prop)
	return output_type

class AudioDisplay(Gst.Bin):
	def __init__(self):
		super(AudioDisplay, self).__init__()
		queue = Gst.ElementFactory.make('queue', 'daqueue')
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

class Display(Gst.Bin):
	def __init__(self):
		super(Display, self).__init__()
		aout = AudioDisplay()
		vout = VideoDisplay()

		self.add(aout)
		self.add(vout)

		self.add_pad(Gst.GhostPad.new('audio', aout.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('video', vout.get_static_pad('sink')))

class FFMpeg(Gst.Bin):
	def __init__(self):
		super(FFMpeg, self).__init__()
		aqueue = Gst.ElementFactory.make('queue', 'ffaqueue')
		vqueue = Gst.ElementFactory.make('queue', 'ffvqueue')

		aout = Gst.ElementFactory.make('fdsink', None)
		vout = Gst.ElementFactory.make('fdsink', None)

		self.afin, self.afout = os.pipe()
		self.vfin, self.vfout = os.pipe()

		aout.set_property('fd', self.afout)
		aout.set_property('sync', False)
		vout.set_property('fd', self.vfout)
		vout.set_property('sync', False)

		self.ffmpeg = subprocess.Popen([
			'/usr/bin/ffmpeg',
			'-v', 'warning',
			'-f', 'rawvideo',
			'-r', '60',
			'-s', '1280x720',
			'-pix_fmt', 'uyvy422',
			'-i', 'pipe:' + str(self.vfin),
			'-f', 's16le',
			'-channel_layout', 'stereo',
			'-probesize', '1024',
			'-ac', '2',
			'-i', 'pipe:' + str(self.afin),
			'-c:a', 'flac',
			'-c:v', 'ffv1',
			'-y',
			'ffv1.mkv'
		])

		self.add(aqueue)
		self.add(vqueue)
		self.add(aout)
		self.add(vout)

		aqueue.link(aout)
		vqueue.link(vout)

		self.add_pad(Gst.GhostPad.new('audio', aqueue.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('video', vqueue.get_static_pad('sink')))

def filesink_make():
	return Gst.ElementFactory.make('filesink')

output_registry['display'] = Display
output_registry['file'] = filesink_make
output_registry['ffmpeg'] = FFMpeg
