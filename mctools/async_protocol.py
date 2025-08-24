"""
Low-level protocol stuff for RCON, Query and Server List Ping.
"""

import struct
import asyncio

from typing import Tuple, Any

from mctools.packet import RCONPacket, QUERYPacket, PINGPacket
from mctools.encoding import PINGEncoder
from mctools.errors import RCONLengthError, ProtoConnectionClosed

# Default timeout:
DEFAULT_TIMEOUT = 60


class AsyncBaseProtocol(object):
    """
    Parent Class for protocol implementations.
    Every protocol instance should inherit this class!
    """

    def __init__(self) -> None:
        self.timeout: int = DEFAULT_TIMEOUT  # Defines and sets the timeout value
        self.connected: bool = False  # Value determining if we are connected

    async def start(self):
        """
        Method to start the connection to remote entity.

        We simply set the connected value,
        and configure the timeout.
        """

        # Set connected to true:

        self.connected = True

    async def stop(self):
        """
        Method to stop the connection to remote entity.

        We simply set the connected value.
        """

        self.connected = False

    async def send(self, pack: Any):
        """
        Method to send data to remote entity, data type is arbitrary.
        This raises a NotImplementedErrorException, as it should be overridden in the child class.

        :param data: Some data in some format.
        """

        raise NotImplementedError("Override this method in child class!")

    async def read(self) -> Any:
        """
        Method to receive data from remote entity
        This raises a NotImplementedErrorException, as it should be overridden in the child class.

        :return: Data received, data type is arbitrary
        """

        raise NotImplementedError("Override this method in child class!")

    def set_timeout(self, timeout: int):
        """
        Sets the timeout value for the underlying socket object.

        :param timeout: Value in seconds to set the timeout to
        :type timeout: int

        .. versionadded:: 1.1.0

        This method now works before the protocol object is started
        """
        if timeout == 0:
            self.timeout = None
        else:
            self.timeout = timeout


class AsyncTCPProtocol(AsyncBaseProtocol):

    def __init__(self, host, port):
        super().__init__()

        # TCP connection
        self.reader: asyncio.StreamReader
        self.writer: asyncio.StreamWriter

        self.host: str = host
        self.port: int = int(port)

    async def start(self):
        """
        Starts the connection to the TCP server.
        """

        # Preform generic start operations:

        await super().start()

        # Create the connection:

        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def stop(self):
        """
        Stopping the connection to the TCP server.
        """

        # Closing connection

        self.writer.close()
        await self.writer.wait_closed()

        # Preform generic stop tasks:

        await super().stop()

    async def read_tcp(self, length: int) -> bytes:
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

            last = await asyncio.wait_for(self.reader.read(length - len(byts)), self.timeout)

            byts = byts + last

            if last == b'':

                # We received nothing, lets close this connection:

                await self.stop()

                # Raise the 'ConnectionClosed' exception:

                raise ProtoConnectionClosed(
                    "Connection closed by remote host!")

        return byts

    async def write_tcp(self, byts: bytes):
        """
        Writes data over the TCP protocol.

        :param byts: Bytes to send
        :type byts: bytes
        """

        self.writer.write(byts)
        await asyncio.wait_for(self.writer.drain(), self.timeout)

    def __del__(self):
        """
        Attempts to close the socket:
        """

        try:

            self.writer.close()

        except Exception:

            pass


class AwaitableDatagramProtocol(asyncio.Protocol):
    def __init__(self):
        self.queue = asyncio.Queue()
        self.shutdown = asyncio.Event()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # Put received data into the queue
        self.queue.put_nowait((data, addr))

    def connection_lost(self, exc):
        # The socket has been closed
        self.shutdown.set()

    async def read_datagram(self):
        read_queue_task = asyncio.create_task(self.queue.get())
        shutdown_monitor_task = asyncio.create_task(self.shutdown.wait())

        done, pending = await asyncio.wait([read_queue_task, shutdown_monitor_task], return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        if read_queue_task in done:
            return await read_queue_task
        else:  # Connection was lost
            return b"", (None, None)


class AsyncUDPProtocol(AsyncBaseProtocol, asyncio.Protocol):

    def __init__(self, host, port):
        super().__init__()

        # UDP connection
        self.transport: asyncio.DatagramTransport
        self.protocol: asyncio.DatagramProtocol
        self.queue = asyncio.Queue()

        self.host: str = host
        self.port: int = int(port)

    async def start(self):
        await super().start()

        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(AwaitableDatagramProtocol, remote_addr=(self.host, self.port))

    async def stop(self):
        self.transport.close()

        await super().stop()

    async def read_udp(self) -> Tuple[bytes, str]:
        """
        Reads data over the UDP protocol.

        :return: Bytes read and address
        :rtype: Tuple[bytes, str]
        """

        return await self.protocol.read_datagram()

    def write_udp(self, byts: bytes):
        """
        Writes data over the UPD protocol.

        :param byts: Bytes to write
        :type byts: bytes
        :param host: Hostanme of remote host
        :type host: str
        :param port: Portname of remote host
        :type port: int
        """

        self.transport.sendto(byts)

    def __del__(self):
        """
        Attempts to close the socket:
        """

        try:

            self.transport.close()

        except Exception:

            pass

class AsyncRCONProtocol(AsyncTCPProtocol):
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
        super().__init__(host, port)

        # Finally, set the timeout:

        self.set_timeout(timeout)

    def start(self):
        """
        Starts the connection to the RCON server.
        """

        if self.connected:

            # Already started

            return

        # Preform generic start operations:

        super().start()

    async def send(self, pack: RCONPacket, length_check: bool = False):
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

        await self.write_tcp(data)

    async def read(self) -> RCONPacket:
        """
        Gets a RCON packet from the RCON server.

        :return: RCONPacket containing payload
        :rtype: RCONPacket
        """

        # Getting first 4 bytes to determine length of packet:

        length_data = await self.read_tcp(4)

        # Unpacking length data:

        length = struct.unpack("<i", length_data)[0]

        # Reading the rest of the packet:

        byts = await self.read_tcp(length)

        # Generating packet:

        pack = RCONPacket.from_bytes(byts)

        return pack


class AsyncQUERYProtocol(AsyncUDPProtocol):
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
        super().__init__(host, port)

        # Finally, set the timeout:

        self.set_timeout(timeout)

    def send(self, pack: QUERYPacket):
        """
        Sends a packet to the Query server.

        :param pack: Packet to send
        :type pack: QUERYPacket
        """

        # Converting packet into bytes:

        byts = bytes(pack)

        # Sending packet:

        self.write_udp(byts)

    async def read(self) -> QUERYPacket:
        """
        Gets a Query packet from the Query server.

        :return: QUERYPacket
        :rtype: QUERYPacket
        """

        # Getting packet:

        byts, address = await self.read_udp()

        # Converting bytes to packet:

        pack = QUERYPacket.from_bytes(byts)

        return pack


class AsyncPINGProtocol(AsyncTCPProtocol):
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
        super().__init__(host, port)

        # Finally, set the timeout:

        self.set_timeout(timeout)

    async def send(self, pack: PINGPacket):
        """
        Sends a ping packet to the Minecraft server.

        :param pack: PINGPacket
        :type pack: PINGPacket
        """

        # Converting packet to bytes:

        byts = bytes(pack)

        # Sending bytes:

        await self.write_tcp(byts)

    async def read(self) -> PINGPacket:
        """
        Read data from the Minecraft server and convert it into a PINGPacket.

        :return: PINGPacket
        :rtype: PINGPacket
        """

        # Getting length of ALL data:

        length = await PINGEncoder.adecode_sock(self.reader, timeout=self.timeout)

        # Reading the rest of the data:

        byts = await self.read_tcp(length)

        # Creating packet:

        pack = PINGPacket.from_bytes(byts)

        return pack
