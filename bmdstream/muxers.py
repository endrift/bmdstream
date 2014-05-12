from gi.repository import Gst

from .encoders import LameEncoder, X264Encoder

class FLVMuxer(Gst.Bin):
	def __init__(self):
		super(FLVMuxer, self).__init__()
		aenc = LameEncoder()
		venc = X264Encoder()

		flvmux = Gst.ElementFactory.make ('flvmux', None)
		flvmux.set_property('streamable', True)

		filesink = Gst.ElementFactory.make('filesink', None)
		filesink.set_property('location', 'test.flv')

		self.add(aenc)
		self.add(venc)
		self.add(flvmux)
		self.add(filesink)

		venc.link(flvmux)
		aenc.link(flvmux)

		flvmux.link(filesink)

		self.add_pad(Gst.GhostPad.new('audio', aenc.get_static_pad('sink')))
		self.add_pad(Gst.GhostPad.new('video', venc.get_static_pad('sink')))

