import gi
import os
import sys
import threading

class Configuration:
	def __init__(self):
		if sys.version_info.major >= 3:
			import configparser
		else:
			import ConfigParser as configparser
		self._ns = configparser

		self.config = configparser.SafeConfigParser()
		self.session = None

	def add_config_file(self, config_file=None):

		if config_file is None:
			config_dir = os.environ.get('XDG_CONFIG_HOME') or (os.path.join(os.environ.get('HOME'), '.config'))
			config_file = os.path.join(config_dir, 'bmdstream')
		self.config.read(config_file)

	def getint(self, key, default=0):
		value = None
		if self.session is not None:
			try:
				value = self.config.getint('sessions.' + self.session, key)
			except self._ns.NoOptionError:
				pass
		if value is None:
			try:
				value = self.config.getint('defaults', key)
			except self._ns.NoOptionError:
				pass
		if value is None:
			if default is not None:
				return default
			raise KeyError(key)
		return value

	def getboolean(self, key, default=False):
		value = None
		if self.session is not None:
			try:
				value = self.config.getboolean('sessions.' + self.session, key)
			except self._ns.NoOptionError:
				pass
		if value is None:
			try:
				value = self.config.getboolean('defaults', key)
			except self._ns.NoOptionError:
				pass
		if value is None:
			if default is not None:
				return default
			raise KeyError(key)
		return value

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

class AudioInput(Gst.Bin):
	def __init__(self):
		super(AudioInput, self).__init__()
		mic = Gst.ElementFactory.make('autoaudiosrc')
		mqueue = Gst.ElementFactory.make('queue')
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

	def attach_audio_input(self, input):
		self.add(input)
		input.link(self.adder)

	def attach_output(self, output):
		self.add(output)
		self.atee.link(output)
		self.vtee.link(output)
