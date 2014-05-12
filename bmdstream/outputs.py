from gi.repository import Gst

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

class Display(Gst.Bin):
	def __init__(self):
		super(Display, self).__init__()
		aout = AudioDisplay()
		vout = VideoDisplay()

		self.add(aout)
		self.add(vout)

		self.add_pad(Gst.GhostPad.new('audio', aout.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('video', vout.get_static_pad('sink')))

def filesink_make():
	return Gst.ElementFactory.make('filesink')

output_registry['display'] = Display
output_registry['file'] = filesink_make
