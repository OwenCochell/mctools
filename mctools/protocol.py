"""
Low-level protocol stuff for RCON, Query and Server List Ping.
"""

import struct
import socket

from typing import Tuple, Any

from mctools.packet import RCONPacket, QUERYPacket, PINGPacket
from mctools.encoding import PINGEncoder
from mctools.errors import RCONLengthError, ProtoConnectionClosed

# Default timeout:
DEFAULT_TIMEOUT = 60


class BaseProtocol(object):
    """
    Parent Class for protocol implementations.
    Every protocol instance should inherit this class!
    """

    def __init__(self) -> None:
        self.sock: socket.socket  # Socket to utilize

        self.timeout: int = DEFAULT_TIMEOUT  # Defines and sets the timeout value
        self.connected: bool = False  # Value determining if we are connected

    def start(self):
        """
        Method to start the connection to remote entity.

        We simply set the connected value,
        and configure the timeout.
        """

        # Set connected to true:

        self.connected = True

        # Set timeout value:

        self.set_timeout(self.timeout)

    def stop(self):
        """
        Method to stop the connection to remote entity.

        We simply set the connected value.
        """

        self.connected = False

    def send(self, pack: Any):
        """
        Method to send data to remote entity, data type is arbitrary.
        This raises a NotImplementedErrorException, as it should be overridden in the child class.

        :param data: Some data in some format.
        """

        raise NotImplementedError("Override this method in child class!")

    def read(self) -> Any:
        """
        Method to receive data from remote entity
        This raises a NotImplementedErrorException, as it should be overridden in the child class.

        :return: Data received, data type is arbitrary
        """

        raise NotImplementedError("Override this method in child class!")

    def read_tcp(self, length: int) -> bytes:
        """
        Reads data over the TCP protocol.

        :param length: Amount of data to read
        :type length: int
        :return: Read bytes
        :rtype: bytes
        """

        byts = b''

        # We have to read in parts, as our buffsize may not be big enough:

        while len(byts) < length:

            last = self.sock.recv(length - len(byts))

            byts = byts + last

            if last == b'':

                # We received nothing, lets close this connection:

                self.stop()

                # Raise the 'ConnectionClosed' exception:

                raise ProtoConnectionClosed(
                    "Connection closed by remote host!")

        return byts

    def write_tcp(self, byts: bytes):
        """
        Writes data over the TCP protocol.

        :param byts: Bytes to send
        :type byts: bytes
        """

        self.sock.sendall(byts)

    def read_udp(self) -> Tuple[bytes, str]:
        """
        Reads data over the UDP protocol.

        :return: Bytes read and address
        :rtype: Tuple[bytes, str]
        """

        return self.sock.recvfrom(1024)

    def write_udp(self, byts: bytes, host: str, port: int):
        """
        Writes data over the UPD protocol.

        :param byts: Bytes to write
        :type byts: bytes
        :param host: Hostanme of remote host
        :type host: str
        :param port: Portname of remote host
        :type port: int
        """

        self.sock.sendto(byts, (host, port))

    def set_timeout(self, timeout: int):
        """
        Sets the timeout value for the underlying socket object.

        :param timeout: Value in seconds to set the timeout to
        :type timeout: int

        .. versionadded:: 1.1.0

        This method now works before the protocol object is started
        """

        # First, set the timeout value:

        self.timeout = timeout

        # Next, determine if we should set the socket timeout:

        if self.connected:

            # Set the timeout:

            self.sock.settimeout(timeout)

    def __del__(self):
        """
        Attempts to close the socket:
        """

        try:

            self.sock.close()

        except Exception:

            pass


class RCONProtocol(BaseProtocol):
    """
    Protocol implementation for RCON - Uses TCP sockets.

    :param host: Hostname of RCON server
    :type host: str
    :param port: Port number of the RCON server
    :type port: int
    :param timeout: Timeout value for socket operations.
    :type timeout: int

    .. versionchanged:: 1.3.0

    Moved packet types to RCONPacket
    """

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__()

        self.host: str = host  # Host of the RCON server
        self.port: int = int(port)  # Port of the RCON server

        # Finally, set the timeout:

        self.set_timeout(timeout)

    def start(self):
        """
        Starts the connection to the RCON server.
        """

        if self.connected:

            # Already started

            return

        # Create an ip4 tcp socket:

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Preform generic start operations:

        super().start()

        # Create the connection:

        self.sock.connect((self.host, self.port))

    def stop(self):
        """
        Stops the connection to the RCON server.
        """

        # Close the socket:

        self.sock.close()

        # Preform generic stop operations:

        super().stop()

    def send(self, pack: RCONPacket, length_check: bool = False):
        """
        Sends a packet to the RCON server.

        :param pack: RCON Packet
        :type pack: RCONPacket
        :param length_check: Boolean determining if we should check packet length
        :type length_check: bool

        .. versionadded:: 1.1.2

        The 'length_check' parameter
        """

        # Getting encoded packet data:

        data = bytes(pack)

        # Check if data is too big:

        if length_check and len(data) >= 1460:

            # Too big, raise an exception!

            raise RCONLengthError("Packet type is too big!", len(data))

        # Sending packet:

        self.write_tcp(data)

    def read(self) -> RCONPacket:
        """
        Gets a RCON packet from the RCON server.

        :return: RCONPacket containing payload
        :rtype: RCONPacket
        """

        # Getting first 4 bytes to determine length of packet:

        length_data = self.read_tcp(4)

        # Unpacking length data:

        length = struct.unpack("<i", length_data)[0]

        # Reading the rest of the packet:

        byts = self.read_tcp(length)

        # Generating packet:

        pack = RCONPacket.from_bytes(byts)

        return pack


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

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__()

        self.host: str = host  # Host of the Query server
        self.port: int = int(port)  # Port of the Query server

        # Finally, set the timeout:

        self.set_timeout(timeout)

    def start(self):
        """
        Sets the protocol object as ready to communicate.
        """

        # Create an ip4 UPD socket:

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Preform generic start operations:

        super().start()

    def stop(self):
        """
        Sets the protocol object as not ready to communicate.
        """

        # Preform generic stop operations:

        super().stop()

    def send(self, pack: QUERYPacket):
        """
        Sends a packet to the Query server.

        :param pack: Packet to send
        :type pack: QUERYPacket
        """

        # Converting packet into bytes:

        byts = bytes(pack)

        # Sending packet:

        self.write_udp(byts, self.host, self.port)

    def read(self) -> QUERYPacket:
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

    def __init__(self, host: str, port: int, timeout: int):

        # Init super class
        super().__init__()

        self.host: str = host  # Host of the Minecraft server
        self.port: int = int(port)  # Port of the Minecraft server

        # Finally, set the timeout:

        self.set_timeout(timeout)

    def start(self):
        """
        Starts the connection to the Minecraft server.
        """

        # Create an ip4 TCP socket:

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Preform generic start tasks:

        super().start()

        # Starting connection

        self.sock.connect((self.host, self.port))

    def stop(self):
        """
        Stopping the connection to the Minecraft server.
        """

        # Closing connection

        self.sock.close()

        # Preform generic stop tasks:

        super().stop()

    def send(self, pack: PINGPacket):
        """
        Sends a ping packet to the Minecraft server.

        :param pack: PINGPacket
        :type pack: PINGPacket
        """

        # Converting packet to bytes:

        byts = bytes(pack)

        # Sending bytes:

        self.write_tcp(byts)

    def read(self) -> PINGPacket:
        """
        Read data from the Minecraft server and convert it into a PINGPacket.

        :return: PINGPacket
        :rtype: PINGPacket
        """

        # Getting length of ALL data:

        length = PINGEncoder.decode_sock(self.sock)

        # Reading the rest of the data:

        byts = self.read_tcp(length)

        # Creating packet:

        pack = PINGPacket.from_bytes(byts)

        return pack
