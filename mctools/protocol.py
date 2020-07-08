import struct
import socket
from mctools.packet import RCONPacket, QUERYPacket, PINGPacket
from mctools.encoding import PINGEncoder

"""
Low-level protocol stuff for RCON, Query and Server List Ping.
"""


class BaseProtocol(object):

    """
    Parent Class for protocol implementations,
    """

    def start(self):

        """
        Method to start the connection to remote entity.
        This raises a NotImplementedErrorException, as it should be overridden in the child class.
        """

        raise NotImplementedError("Override this method in child class!")

    def stop(self):

        """
        Method to stop the connection to remote entity.
        This raises a NotImplementedErrorException, as it should be overridden in the child class.
        """

        raise NotImplementedError("Override this method in child class!")

    def send(self, data):

        """
        Method to send data to remote entity, data type is arbitrary.
        This raises a NotImplementedErrorException, as it should be overridden in the child class.

        :param data: Some data in some format.
        """

        raise NotImplementedError("Override this method in child class!")

    def read(self):

        """
        Method to receive data from remote entity
        This raises a NotImplementedErrorException, as it should be overridden in the child class.

        :return: Data received, data type is arbitrary
        """

        raise NotImplementedError("Override this method in child class!")

    def read_tcp(self, length):

        """
        Reads data over the TCP protocol.

        :param length: Amount of data to read
        :type length: int
        :return: Read bytes
        """

        byts = b''

        # We have to read in parts, as our buffsize may not be big enough:

        while len(byts) < length:

            last = self.sock.recv(length - len(byts))

            if len(last) == 0:

                raise Exception("Server sent no information!")

            byts = byts + last

        return byts

    def write_tcp(self, byts):

        """
        Writes data over the TCP protocol.

        :param byts: Bytes to send
        :return: Data read
        """

        return self.sock.sendall(byts)

    def read_udp(self):

        """
        Reads data over the UDP protocol.

        :return: Bytes read
        """

        return self.sock.recvfrom(1024)

    def write_udp(self, byts, host, port):

        """
        Writes data over the UPD protocol.

        :param byts: Bytes to write
        :param host: Hostanme of remote host
        :param port: Portname of remote host
        :return:
        """

        self.sock.sendto(byts, (host, port))


class RCONProtocol(BaseProtocol):

    """
    Protocol implementation fot RCON - Uses TCP sockets.

    :param host: Hostname of RCON server
    :type host: str
    :param port: Port number of the RCON server
    :type port: int
    :param timeout: Timeout value for socket operations.
    :type timeout: int
    """

    def __init__(self, host, port, timeout):

        self.host = host  # Host of the RCON server
        self.port = int(port)  # Port of the RCON server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a ip4 TCP socket
        self.LOGIN = 3  # Packet type used for logging in
        self.COMMAND = 2  # Packet type for issuing a command
        self.RESPONSE = 0  # Packet type for response
        self.connected = False  # Value determining if we are connected

        self.sock.settimeout(timeout)  # Setting timeout value for socket

    def start(self):

        """
        Starts the connection to the RCON server.
        """

        if self.connected:

            # Already started

            return

        self.sock.connect((self.host, self.port))

        self.connected = True

    def stop(self):

        """
        Stops the connection to the RCON server.
        """

        self.sock.close()

        self.connected = False

    def send(self, pack):

        """
        Sends a packet to the RCON server.

        :param pack: RCON Packet
        :type pack: RCONPacket
        """

        # Getting encoded packet data:

        data = bytes(pack)

        # Sending packet:

        self.write_tcp(data)

    def read(self):

        """
        Gets an RCON packet from the RCON server.
        Supports packet fragmenting.

        :return: RCONPacket contaning payload
        :rtype: RCONPacket
        """

        # Getting first 4 bytes to determine length of packet:

        length_data = self.read_tcp(4)

        assert len(length_data) >= 4

        # Unpacking length data:

        length = struct.unpack("<i", length_data)[0]

        # Reading the rest of the packet:

        byts = self.read_tcp(length)

        # Generating packet:

        pack = RCONPacket.from_bytes(byts)

        return pack

    def __del__(self):

        """
        Attempts to close the socket
        """

        try:

            self.sock.close()

        except:

            pass


class QUERYProtocol(BaseProtocol):

    """
    Protocol implementation for Query - Uses UDP sockets.

    :param host: The hostname of the Query server.
    :type host: str
    :param port: Port number of the Query server
    :type port: int
    :param timeout: Timeout value for socket operations
    :type timeout: int

    """

    def __init__(self, host, port, timeout):

        self.host = host  # Host of the Query server
        self.port = int(port)  # Port of the Query server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creating a ip4 UDP socket
        self.started = False  # Determining if we have started communicating with the Query server

        self.sock.settimeout(timeout)  # Setting timeout value for socket

    def start(self):

        """
        Sets the protocol object as ready to communicate.
        """

        self.started = True

    def stop(self):

        """
        Sets the protocol object as not ready to communicate.
        """

        self.started = False

    def send(self, pack):

        """
        Sends a packet to the Query server.

        :param pack: Packet to send
        :type pack: QUERYPacket
        """

        # Converting packet into bytes:

        byts = bytes(pack)

        # Sending packet:

        self.write_udp(byts, self.host, self.port)

    def read(self):

        """
        Gets a Query packet from the Query server.

        :return: QUERYPacket
        :rtype: QUERYPacket
        """

        # Getting packet:

        byts, address = self.read_udp()

        # Converting bytes to packet:

        pack = QUERYPacket.from_bytes(byts)

        return pack

    def __del__(self):

        """
        Attempts to close the socket
        """

        try:

            self.sock.close()

        except:

            pass


class PINGProtocol(BaseProtocol):

    """
    Protocol implementation for server list ping - uses TCP sockets.

    :param host: Hostname of the Minecraft server
    :type host: str
    :param port: Port number of the Minecraft server
    :type port: int
    :param timeout: Timeout value used for socket operations
    :type timeout: int
    """

    def __init__(self, host, port, timeout):

        self.host = host  # Host of the Minecraft server
        self.port = int(port)  # Port of the Minecraft server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating an ip4 TCP socket
        self.connected = False  # Value determining if we are connected

        self.sock.settimeout(timeout)  # Setting timeout value for socket

    def start(self):

        """
        Starts the connection to the Minecraft server.
        """

        # Starting connection

        self.sock.connect((self.host, self.port))

        # Setting protocol state

        self.connected = True

    def stop(self):

        """
        Stopping the connection to the Minecraft server.
        """

        # Closing connection

        self.sock.close()

        # Setting protocol state

        self.connected = False

    def send(self, pack):

        """
        Sends a ping packet to the Minecraft server.

        :param pack: PINGPacket
        :type pack: PINGPacket
        """

        # Converting packet to bytes:

        byts = bytes(pack)

        # Sending bytes:

        self.write_tcp(byts)

    def read(self):

        """
        Read data from the Minecraft server and convert it into a PINGPacket.

        :return: PINGPacket
        :rtype: PINGPacket
        """

        # Reading length data:

        # Getting length of ALL data:

        length = PINGEncoder.decode_sock(self.sock)

        # Reading the rest of the data:

        byts = self.read_tcp(length)

        # Creating packet:

        pack = PINGPacket.from_bytes(byts)

        return pack

    def __del__(self):

        """
        Attempts to close the socket:
        """

        try:

            self.sock.close()

        except:

            pass
