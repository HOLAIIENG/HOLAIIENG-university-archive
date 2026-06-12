from PySide6.QtCore import Signal, Slot, QByteArray, QDataStream, QObject, QIODevice
from PySide6.QtNetwork import QTcpSocket, QAbstractSocket


class HNNKTcpSocketClient(QObject):
    server_connected = Signal()
    server_disconnected = Signal()
    recv_from_server = Signal(QByteArray)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.on_server_connected)
        self.socket.disconnected.connect(self.on_server_disconnected)
        self.socket.readyRead.connect(self.on_recv_from_server)
        self.recv_buffer = QByteArray()

    def connect_server(self, ip, port):
        self.recv_buffer.clear()
        self.socket.connectToHost(ip, port)

    def close_server(self):
        self.recv_buffer.clear()
        self.socket.disconnectFromHost()

    def send_to_server(self, data):
        if self.socket.state() != QAbstractSocket.SocketState.ConnectedState:
            return

        payload = QByteArray(data)

        packet = QByteArray()
        stream = QDataStream(packet, QIODevice.OpenModeFlag.WriteOnly)
        stream.setByteOrder(QDataStream.ByteOrder.BigEndian)

        stream.writeUInt32(payload.size())
        packet.append(payload)

        self.socket.write(packet)

    @Slot()
    def on_server_connected(self):
        self.server_connected.emit()

    @Slot()
    def on_server_disconnected(self):
        self.server_disconnected.emit()

    @Slot()
    def on_recv_from_server(self):
        self.recv_buffer.append(self.socket.readAll())

        while True:
            if self.recv_buffer.size() < 4:
                return

            stream = QDataStream(self.recv_buffer)
            stream.setByteOrder(QDataStream.ByteOrder.BigEndian)
            payload_len = stream.readUInt32()

            total_len = 4 + payload_len
            if self.recv_buffer.size() < total_len:
                return

            payload = self.recv_buffer.mid(4, payload_len)
            self.recv_buffer.remove(0, total_len)

            self.recv_from_server.emit(payload)
