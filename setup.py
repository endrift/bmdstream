#!/usr/bin/env python
from setuptools import setup

setup(name='bmdstream',
	version='0.1dev',
	description='GStreamer scripts for streaming from Blackmagic Design devices',
	author='Jeffrey Pfau',
	author_email='jeffrey@endrift.com',
	url='https://github.com/jpfau/bmdstream',
	license='MIT',
	packages=['bmdstream'],
	scripts=['bin/bmdstream'],
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX :: Linux',
		'Topic :: Multimedia :: Video :: Capture'
	]
)
