from gi.repository import Gst

encoder_registry = {}

def make_encoder(name):
	enc = encoder_registry[name]
	if enc:
		return enc()
	return None

class LameEncoder(Gst.Bin):
	def __init__(self):
		super(LameEncoder, self).__init__()
		enc = Gst.ElementFactory.make('lamemp3enc', None)
		parse = Gst.ElementFactory.make('mpegaudioparse', None)
		queue = Gst.ElementFactory.make('queue', 'lamequeue')

		enc.set_property('target', 'bitrate')

		self.add(enc)
		self.add(parse)
		self.add(queue)

		enc.link(parse)
		parse.link(queue)

		self.set_property = enc.set_property

		self.add_pad(Gst.GhostPad.new('sink', enc.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('src', queue.get_static_pad('src')))

class FlacEncoder(Gst.Bin):
	def __init__(self):
		super(FlacEncoder, self).__init__()
		enc = Gst.ElementFactory.make('flacenc', None)
		queue = Gst.ElementFactory.make('queue', 'flacqueue')

		self.add(enc)
		self.add(queue)

		enc.link(queue)

		self.set_property = enc.set_property

		self.add_pad(Gst.GhostPad.new('sink', enc.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('src', queue.get_static_pad('src')))

class X264Encoder(Gst.Bin):
	def __init__(self):
		super(X264Encoder, self).__init__()
		convert = Gst.ElementFactory.make('videoconvert', None)
		enc = Gst.ElementFactory.make('x264enc', None)
		parse = Gst.ElementFactory.make('h264parse', None)
		queue = Gst.ElementFactory.make('queue', 'x264queue')

		enc.set_property('threads', 4)
		enc.set_property('speed-preset', 'faster')
		enc.set_property('tune', 'zerolatency')

		self.add(convert)
		self.add(enc)
		self.add(parse)
		self.add(queue)

		convert.link(enc)
		enc.link(parse)
		parse.link(queue)

		self.set_property = enc.set_property

		self.add_pad(Gst.GhostPad.new('sink', convert.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('src', queue.get_static_pad('src')))

encoder_registry['raw'] = None
encoder_registry['flac'] = FlacEncoder
encoder_registry['mp3'] = LameEncoder
encoder_registry['h264'] = X264Encoder
