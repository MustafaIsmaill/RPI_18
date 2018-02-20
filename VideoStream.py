import threading
import time
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst


class VideoStream():
    def __init__(self, ip, port, port2):
        Gst.init(None)
        self._ip = ip
        self._port = port
        self._port2 = port2
        # self._ip = "10.0.1.54"
        # self._port = "5000"
        self._ip = ip
        self._port = port
        self._pipeline = Gst.parse_launch(
            "v4l2src device=/dev/video0 ! image/jpeg, width=1280, height=720, framerate=60/1 ! rtpjpegpay ! multiudpsink clients=" + self._ip + ":" + self._port + "," + ip + ":" + self._port2 + "sync=false")
        self._thread = None

    def start(self):
        ret = self._pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            raise Exception("Error starting the pipeline")
        self._running = True
        if (self._thread is None) or (not self._thread.isAlive()):
            self._thread = threading.Thread(target=self._run, args=())
            self._thread.start()

    def _run(self):
        bus = self._pipeline.get_bus()

        while True:
            if not self._running:
                break
            message = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE,
                                             Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if message.type == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print("Debugging information: %s" % debug, file=sys.stderr)
                raise Exception("Error received from element %s: %s" % (message.src.get_name(), err), file=sys.stderr)
            elif message.type == Gst.MessageType.EOS:
                #print("End-Of-Stream reached.")
                break
            elif message.type == Gst.MessageType.STATE_CHANGED:
                if isinstance(message.src, Gst.Pipeline):
                    old_state, new_state, pending_state = message.parse_state_changed()
                    #print("Pipeline state changed from %s to %s." % (old_state.value_nick, new_state.value_nick))
            else:
                raise Exception("Unexpected message received.")

    def pause(self):
        self._pipeline.set_state(Gst.State.PAUSED)

    def close(self):
        self._running = False
        self._pipeline.set_state(Gst.State.NULL)
