from time import sleep
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

Gst.init(None)

pipeline = Gst.Pipeline()
# bin = Gst.parse_bin_from_description("v4l2src device=/dev/video0 ! image/jpeg,framerate=30/1,width=1280,height=720 ! jpegdec ! autovideosink", False)
bin = Gst.parse_bin_from_description("v4l2src device=/dev/video0 ! image/jpeg, width=1280, height=720, framerate=60/1 ! rtpjpegpay ! multiudpsink clients=10.0.1.54:1234,10.0.1.54:5678 sync=false", False)
# bin = Gst.parse_bin_from_description("v4l2src device=/dev/video1 ! image/jpeg,framerate=30/1,width=1280,height=720 ! rtpjpegpay ! application/x-rtp,encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec ! autovideosink", False)
pipeline.add(bin)
pipeline.set_state(Gst.State.PLAYING)
loop = GObject.MainLoop()
loop.run()
