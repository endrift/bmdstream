#!/usr/bin/python3
import gi
import threading

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)

pipeline = Gst.Pipeline()

src = Gst.ElementFactory.make("decklinksrc", None)
src.set_property("connection", 1)
src.set_property("mode", 18)
pipeline.add(src)

aqueue = Gst.ElementFactory.make("queue", None)
pipeline.add(aqueue)

vqueue = Gst.ElementFactory.make("queue", None)
pipeline.add(vqueue)

asink = Gst.ElementFactory.make("autoaudiosink", None)
asink.set_property("sync", False)
pipeline.add(asink)

vsink = Gst.ElementFactory.make("autovideosink", None)
vsink.set_property("sync", False)
pipeline.add(vsink)

src.link(aqueue)
src.link(vqueue)

aqueue.link(asink)
vqueue.link(vsink)

pipeline.set_state(Gst.State.PLAYING)
loop = GObject.MainLoop()
loop.run()
