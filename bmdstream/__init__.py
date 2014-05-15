import gi
import os
import sys
import threading
import yaml

class Configuration:
	def __init__(self):
		self.config = {
			'pipeline': {},
			'inputs': {},
			'containers': {},
			'formats': {},
			'outputs': {}
		}

		self.add_config_file(os.path.join(os.path.dirname(__file__), 'defaults.yaml'))

	def add_config_file(self, config_file=None):
		if config_file is None:
			config_dir = os.environ.get('XDG_CONFIG_HOME') or (os.path.join(os.environ.get('HOME'), '.config'))
			config_file = os.path.join(config_dir, 'bmdstream')
		with open(config_file, 'r') as f:
			new_config = yaml.load(f)
			for section, value in new_config.items():
				if section in self.config:
					self.config[section].update(value)

	def __getitem__(self, key):
		return self.config[key]

	def get(self, key, default=None):
		return self.config.get(key, default)

gi.require_version('Gst', '1.0')
from gi.repository import Gst

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

class AudioInput(Gst.Bin):
	def __init__(self):
		super(AudioInput, self).__init__()
		mic = Gst.ElementFactory.make('autoaudiosrc')
		mqueue = Gst.ElementFactory.make('queue', 'iaqueue')
		mrs = AudioResampler()

		self.add(mic)
		self.add(mqueue)
		self.add(mrs)

		mic.link(mqueue)
		mqueue.link(mrs)

		self.add_pad(Gst.GhostPad.new('src', mrs.get_static_pad('src')))

class DeckLinkPipeline(Gst.Pipeline):
	def __init__(self, connection, mode):
		super(DeckLinkPipeline, self).__init__()
		src = Gst.ElementFactory.make('decklinksrc', None)
		src.set_property('connection', connection)
		src.set_property('mode', mode)

		aqueue = Gst.ElementFactory.make('queue', 'aqueue')
		self.atee = Gst.ElementFactory.make('tee', None)
		vqueue = Gst.ElementFactory.make('queue', 'vqueue')
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

		self.pipes = {}

	@staticmethod
	def create_from_configuration(config, preset):
		return DeckLinkPipeline(config['inputs'][preset]['connection'], config['inputs'][preset]['mode'])

	def attach_audio_input(self, input):
		self.add(input)
		input.link(self.adder)

	def attach_pipe(self, name, pipe):
		self.add(pipe)
		self.atee.link(pipe)
		self.vtee.link(pipe)
		self.pipes[name] = pipe

	def attach_output(self, pipe, output):
		self.add(output)
		if pipe is not None:
			self.pipes[pipe].link(output)
		else:
			self.atee.link(output)
			self.vtee.link(output)
