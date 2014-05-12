from .encoders import make_encoder

from gi.repository import Gst

container_registry = {}

def make_pipe(config, name):
	format_info = config['formats'][name]
	container_info = config['containers'][format_info['container']]
	muxer = container_registry[container_info['format']]()
	aenc = make_encoder(container_info['audio'])
	venc = make_encoder(container_info['video'])
	pipe = Pipe()
	pipe.set_audio_encoder(aenc)
	pipe.set_video_encoder(venc)
	pipe.set_muxer(muxer)
	pipe.finalize()
	return pipe

class Pipe(Gst.Bin):
	def __init__(self):
		super(Pipe, self).__init__()
		self.venc = None
		self.aenc = None
		self.muxer = None

	def set_audio_encoder(self, aenc):
		self.aenc = aenc
		self.add(aenc)
		self.add_pad(Gst.GhostPad.new('audio', aenc.get_static_pad('sink')))

	def set_video_encoder(self, venc):
		self.venc = venc
		self.add(venc)
		self.add_pad(Gst.GhostPad.new('video', venc.get_static_pad('sink')))

	def set_muxer(self, muxer):
		self.muxer = muxer
		self.add(muxer)
		self.add_pad(Gst.GhostPad.new('src', muxer.get_static_pad('src')))

	def finalize(self):
		if self.aenc:
			self.aenc.link(self.muxer)
		else:
			self.add_pad(Gst.GhostPad.new('audio', muxer.get_static_pad('audio')))

		if self.venc:
			self.venc.link(self.muxer)
		else:
			self.add_pad(Gst.GhostPad.new('video', muxer.get_static_pad('video')))

def flv_make():
	flvmux = Gst.ElementFactory.make('flvmux', None)
	flvmux.set_property('streamable', True)
	return flvmux

def mkv_make():
	return Gst.ElementFactory.make('mkvmux', None)

container_registry['flv'] = flv_make
container_registry['mkv'] = mkv_make
