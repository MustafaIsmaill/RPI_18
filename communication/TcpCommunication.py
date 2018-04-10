# TcpCommunicator.py
import socket, sys, selectors

class UdpCommunicator:
    def __init__(self,targetIp,port):
        self._targetIp=targetIp
        self._port=port
        self._socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self._socket.bind(("0.0.0.0",self._port))
    def send(self,message):
        if self._socket != None:
            message=message.encode(encoding="UTF-8")
            self._socket.sendto(message,(self._targetIp,self._port))

class TcpCommunicator:
    def __init__(self, ip, port, streamingIP, streamingPort1, streamingPort2, streamingPort3, streamingPort4, streaming, timeout=None, closingword="close connection", bind=False):  #timeout is in seconds
        self.NUMBER_OF_TOKENS = 11
        self._videoStreamingEnable = streaming
        self._ip = ip
        self._port = port
        self._streamingIP = streamingIP
        self._streamingPort1 = streamingPort1
        self._streamingPort2 = streamingPort2
        self._streamingPort3 = streamingPort3
        self._streamingPort4 = streamingPort4
        self._connectionClosingKeyWord = closingword
        self._keepaliveduration = 1
        self._keepaliveinterval = 1
        self._createMyCustomizedSocket()
        self._selector = selectors.DefaultSelector()
        self._feedbackUdpSocket = None
        self._liftBagUdpSocket = None
        self._timeout = timeout
        self._bufferSize = 1024
        self._conn = None
        self._eventcallback = None
        if bind is True:
            self._bindAndListen()

    def _createMyCustomizedSocket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if "win" in sys.platform:
            print("Windows")
            self._socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, self._keepaliveduration, 2))
        else:
            print("Linux")
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)

    def _bindAndListen(self):
        self._socket.bind((self._ip, self._port))
        self._socket.listen(1)
        self._socket.setblocking(False)
        self._selector.register(self._socket, selectors.EVENT_READ, self._accept)

    def registerCallBack(self, callback):
        self._eventcallback = callback

    def _accept(self, x=None, y=None):
        if self._conn is not None:
            return
        conn, addr = self._socket.accept()
        # feedback_udp_ip = "127.0.0.1"
        feedback_udp_ip = "10.0.1.54"
        self._feedbackUdpSocket = UdpCommunicator(feedback_udp_ip, 8006)

        # wifi_udp_ip = "127.0.0.1"
        wifi_udp_ip = "192.168.4.1"
        self._liftBagUdpSocket = UdpCommunicator(wifi_udp_ip, 4210)

        if "win" in sys.platform:
            self._socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, self._keepaliveduration, self._keepaliveinterval))
        else:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)

        conn.setblocking(False)

        print(addr, "Connected!")
        self._conn = conn
        self._selector.register(self._conn, selectors.EVENT_READ, self._recv)
        try:
            if self._videoStreamingEnable:
                import VideoStream
                self._pipeline1 = "v4l2src device=/dev/video0 ! image/jpeg, width=1280, height=720, framerate=60/1 ! rtpjpegpay ! multiudpsink clients=" + self._streamingIP + ":" + self._streamingPort1 + "," + self._streamingIP + ":" + self._streamingPort2 +" sync=false"
                self._pipeline2 = "v4l2src device=/dev/video1 ! video/x-raw,framerate=30/1,width=640,height=480 ! x264enc ! multiudpsink clients=" + self._streamingIP + ":" + self._streamingPort3 + "," + self._streamingIP + ":" + self._streamingPort4 +" sync=false"
                self._videoStream = VideoStream.VideoStream(self._pipeline1)
                self._videoStream2 = VideoStream.VideoStream(pipeline2)
                self._videoStream.start()
                self._videoStream2.start()
        except Exception as e:
            print(e)

    def _recv(self,x=None,y=None):
        data = None
        try:
            data = self._conn.recv(self._bufferSize)
            print(data)
        except:
            pass

        if not data:
            self._cleanup()
            return

        data_map = self._parse(data)
        self._eventcallback("TCP", data_map)

        # if self._eventcallback is not None:
            # self._eventcallback("TCP", data_map)

    def _parse(self, data):
        data = data.decode(encoding="UTF-8")
        print("parsing", data)
        tokens = data.split(";")

        del tokens[len(
            tokens) - 1]  # delete last element as it will be empty due to the split() which will split the last ; into an empty token

        data_map = {}

        count = self.NUMBER_OF_TOKENS

        if (len(tokens) is not count):
            print("wrong token")
            tokens_clone = tokens
            tokens = [""]*count
            for i in range(count):
                tokens[i] = tokens_clone[len(tokens_clone)-(count-i)]
            print(tokens)

        for token in tokens:
            try:
                if len(token.split()) is not 2:
                    print("rubbish token")
                    continue
                else:
                    key, value = token.lower().split()
                    data_map[key] = int(value)
            except:
                print("Can't parse token: ", token)

        print("data_map = ", data_map)
        return data_map

    def sendFeedback(self, eventName, data, errorhandler=None):
        if self._feedbackUdpSocket != None:
            self._feedbackUdpSocket.send(data)

    def sendToLiftBag(self, eventName, data, errorhandler=None):
        try:
            if self._liftBagUdpSocket != None:
                self._liftBagUdpSocket.send(data)
        except IOError as e:
            pass

    def _cleanup(self):
        self._eventcallback("TCP ERROR", {})
        if(self._conn != None):
            self._selector.unregister(self._conn)
            self._conn.close()
        self._conn = None
        self._feedbackUdpSocket._socket.close()
        self._feedbackUdpSocket = None
        self._liftBagUdpSocket._socket.close()
        self._liftBagUdpSocket = None


    def mainLoop(self):
        while True:
            events = self._selector.select()
            for key, mask in events:
                callback = key.data
                callback()