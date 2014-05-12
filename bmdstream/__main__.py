from gi.repository import Gst, GObject

from . import AudioInput, Configuration, DeckLinkPipeline
from .displays import Display
from .muxers import FLVMuxer

if __name__ == '__main__':
	config = Configuration()
	config.add_config_file()

	pipeline = DeckLinkPipeline(config.getint('connection'), config.getint('mode'))
	pipeline.attach_audio_input(AudioInput())

	if config.getboolean('save'):
		pipeline.attach_output(FLVMuxer())
	if config.getboolean('display'):
		pipeline.attach_output(Display())

	pipeline.set_state(Gst.State.PLAYING)
	loop = GObject.MainLoop()
	loop.run()
