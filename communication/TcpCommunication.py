# TcpCommunicator.py
import socket, sys, selectors


class UdpCommunicator:
    def __init__(self, targetIp, port):
        self._targetIp = targetIp
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self._socket.bind(("0.0.0.0",self._port))
        self._socket.bind((targetIp,self._port))

    def send(self, message):
        if self._socket != None:
            message = message.encode(encoding="UTF-8")
            self._socket.sendto(message, (self._targetIp, self._port))


class TcpCommunicator:
    def __init__(self, ip, port, timeout=None, closingword="close connection", bind=False):  # timeout is in seconds
        self._videoStreamingEnable = False
        self._ip = ip
        self._port = port
        self._connectionClosingKeyWord = closingword
        self._keepaliveduration = 1
        self._keepaliveinterval = 1
        self._createMyCustomizedSocket()
        self._selector = selectors.DefaultSelector()
        self._udpSocket = None
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

    def _accept(self):
        if self._conn is not None:
            return
        conn, addr = self._socket.accept()
        #udp_ip = "12.0.0.102"
        #udp_ip = "127.0.0.1"

        #udp_ip = addr[0]
        #self._udpSocket = UdpCommunicator(udp_ip, 8004)
        if "win" in sys.platform:
            self._socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, self._keepaliveduration, self._keepaliveinterval))
        else:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
        conn.setblocking(False)
       # print(addr, "Connected!")
        self._conn = conn
        self._selector.register(self._conn, selectors.EVENT_READ, self._recv)
        if self._videoStreamingEnable:
            import VideoStream
            # self._videoStream = VideoStream.VideoStream(addr[0], "8888")
            self._videoStream = VideoStream.VideoStream("127.0.0.1", "5000")
            self._videoStream.start()

    def _recv(self):
        data = None
        try:
            data = self._conn.recv(self._bufferSize)
            print(data)
        except:
            pass

        if not data:
            self._cleanup()
            return data

        data_map = self._parse(data)

        if self._eventcallback is not None:
            self._eventcallback("TCP", data_map)

    def _parse(self, data):
        data = data.decode(encoding="UTF-8")
        print("parsing", data)
        tokens = data.split(";")

        del tokens[len(
            tokens) - 1]  # delete last element as it will be empty due to the split() which will split the last ; into an empty token

        data_map = {}

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

    def _send(self, data, errorhandler=None):
        if self._udpSocket != None:
            self._udpSocket.send(data)
            # if self._conn is None:
            #     return.
            # try:
            # self._conn.sendall(data.encode(encoding="UTF-8"))
            # except:
            #    self._cleanup()
            # errorhandler("TCP ERROR", {})

    def _cleanup(self):
        # print("closed")
        self._eventcallback("TCP ERROR", {})
        self._selector.unregister(self._conn)
        self._conn.close()
        self._conn = None
        # self._udpSocket._socket.close()
        # self._udpSocket = None

    def mainLoop(self):
        while True:
            events = self._selector.select()
            for key, mask in events:
                callback = key.data
                callback()
            try:
                dataReceived = self._recv()
                # print("data receivedd: ", dataReceived)
                if dataReceived == None:
                      print("received None")
                      # callback("TCP ERROR", {})
                      self._closeAndReopenSocket()
                      self._bindAndListen()
                      continue
            except Exception as e:
                print(e)
                print(type(e).__name__)
                print("socket error caught in receiving")
                callback("TCP ERROR",{})
                self._closeAndReopenSocket()
                self._bindAndListen()
                continue
