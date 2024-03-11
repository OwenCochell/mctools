"""
Packet classes to hold RCON and Query data
"""

from __future__ import annotations

from typing import Any, Union

from mctools.encoding import RCONEncoder, QUERYEncoder, PINGEncoder


class BasePacket(object):
    """
    Parent class for packet implementations.
    """

    @classmethod
    def from_bytes(cls, byts: bytes) -> Any:
        """
        Classmethod to create a packet from bytes.
        Rises an NotImplementedError exception, as this function should be overridden in the child class.

        :param byts: Bytes from remote entity
        :type byts: bytes
        :return: Packet object
        """

        raise NotImplementedError("Override this method in child class!")

    def __repr__(self) -> str:
        """
        Show packet type and values

        :return: Formal string
        :rtype: str
        """

        raise NotImplementedError("Override this method in child class!")

    def __str__(self) -> str:
        """
        Allow for packets to represented in string format, pretty print

        :return: Informal string
        :rtype: str
        """

        raise NotImplementedError("Override this method in child class!")

    def __bytes__(self) -> bytes:
        """
        Returns a byte-string representation of the packet

        :return: Bytestring of object
        :rtype: bytes
        """

        raise NotImplementedError("Override this method in child class!")


class RCONPacket(BasePacket):
    """
    Class representing a RCON packet.

    :param reqid: Request ID of the RCON packet
    :type reqid: int
    :param reqtype: Request type of the RCON packet
    :type reqtype: int
    :param payload: Payload of the RCON packet
    :type payload: str

    .. versionchanged:: 1.3.0

    Packet types are now defined here, instead of RCONProtocol
    """

    LOGIN: int = 3  # Packet type used for logging in
    COMMAND: int = 2  # Packet type for issuing a command
    RESPONSE: int = 0  # Packet type for response
    MAX_SIZE: int = 4096  # Maximum packet size

    def __init__(self, reqid: int, reqtype: int, payload: str, length: int = 0):

        self.reqid: int = reqid  # Request ID of the RCON packet
        self.reqtype: int = reqtype  # Request type of the RCON packet
        self.payload: str = payload  # Payload of the RCON packet
        self.length: int = length  # Length of the packet, helps determine if we are fragmented
        self.type:str = 'rcon'  # Determining what type of packet we are

    @classmethod
    def from_bytes(cls, byts: bytes) -> RCONPacket:
        """
        Creates a RCON packet from bytes.

        :param byts: Bytes from RCON server
        :type byts: bytes
        :return: RCONPacket created from bytes
        :rtype: RCONPacket
        """

        reqid, reqtype, payload = RCONEncoder.decode(byts)

        return cls(reqid, reqtype, payload, length=len(byts))

    def __repr__(self) -> str:
        """
        Shows packet type and values - formal way.

        :return: Formal string
        :rtype: str
        """

        return "packet.RCONPacket({}, {}, {})".format(self.reqid, self.reqtype, self.payload)

    def __str__(self) -> str:
        """
        Shows the packet contents in an easy to read format - informal way.

        :return: Informal string
        :rtype: str
        """

        return "RCON Packet:\n - Request ID: {}\n - Request Type: {}\n - Payload: {}".format(self.reqid,
                                                                                             self.reqtype,
                                                                                             self.payload)

    def __bytes__(self) -> bytes:
        """
        Converts packet into byte format.

        :return: Byte string.
        :rtype: bytes
        """

        return RCONEncoder.encode(self.reqid, self.reqtype, self.payload)


class QUERYPacket(BasePacket):
    """
    Class representing a Query Packet.

    QUERYPackets have the following types:

    - BASIC_REQUEST - Client is requesting basic data
    - BASIC_RESPONSE - Server is responding with basic data
    - FULL_REQUEST - Client is requesting full data
    - FULL_RESPONSE - Server is responding with basic data
    - HANDSHAKE_REQUEST - Client is requesting to handshake
    - HANDSHAKE_RESPONSE - Server has acknowledged the handshake

    The lifecyle of a ping connection is as follows:

    1. Client requests to handshake, and the server acknowledges and provides a challenge token
    2. Once handshake has completed, clients may preform one of the two actions using provided challenge token:
        a. Client may request basic server stats
        b. Client may request full server stats
    3. Finally, server responds with stats at the requested level, be it basic or full

    This packet has some optional parameters, namely 'reqtype'.
    This parameter, if unspecified (has a value of -1), will be auto-determined at runtime.
    Users may set this parameter, and decoded packets will have this parameter set,
    but it is recommended to utilize 'packet_type' to identify packets instead.

    :param packet_type: Type of this Query packet
    :type packet_type: int
    :param reqid: Request ID of the Query packet
    :type reqid: int
    :param chall: Challenge token from Query server, -1 if N/A
    :type chall: int
    :param data: Data from the Query server
    :type data: dict
    :param reqtype: Type of request, this will be auto-determined at runtime
    :type reqtype: int

    .. versionchanged:: 1.3.0

    Removed the 'data_type' attribute, and internally it is no longer used.
    We provide the compatibility property of the same name
    that behaves the same as the 'data_type' attribute.

    Packets now use 'packet_type' to identify themselves instead of 'reqtype'
    """

    BASIC_REQUEST: int = QUERYEncoder.BASIC_REQUEST  # Basic data request
    BASIC_RESPONSE: int = QUERYEncoder.BASIC_RESPONSE  # Basic data response
    FULL_REQUEST: int = QUERYEncoder.FULL_REQUEST  # Full data request
    FULL_RESPONSE: int = QUERYEncoder.FULL_RESPONSE  # Full data response
    HANDSHAKE_REQUEST: int = QUERYEncoder.HANDSHAKE_REQUEST  # Challenge request packet
    HANDSHAKE_RESPONSE: int = QUERYEncoder.HANDSHAKE_RESPONSE  # Challenge response packet

    def __init__(self, packet_type: int, reqid: int, chall: int, data: Union[dict, None] = None, reqtype: int = -1):

        self.packet_type: int = packet_type
        self.reqtype: int = reqtype  # Type of Query packet
        self.reqid: int = reqid  # Request ID of the Query packet
        self.chall: int = chall  # Challenge token from the Query server
        self.data: dict = data if data is not None else {}  # Data from the Query server

    @property
    def data_type(self) -> str:
        """
        Determines the data type using the request type.

        This property is here to provide compatibility
        with components that may utilize this value, as it was removed.

        :return: 'basic' for basic data, 'full' for full data, blank string for neither
        :rtype: str
        """

        # Determine if we are basic:

        if self.is_basic():

            return "basic"
        
        # Determine if we are full:

        if self.is_full():

            return "full"
        
        # Otherwise, return nothing:

        return ""

    @classmethod
    def from_bytes(cls, byts: bytes) -> QUERYPacket:
        """
        Creates a Query packet from bytes.

        :param byts: Bytes from Query server
        :type byts: bytes
        :return: Created QUERYPacket
        :rtype: QUERYPacket
        """

        # Decoding bytes:

        packet_type, reqid, chall, data, reqtype = QUERYEncoder.decode(byts)

        # Creating packet:

        pack = cls(packet_type, reqid, chall, data=data, reqtype=reqtype)

        return pack

    def is_basic(self) -> bool:
        """
        Determines if this packet contains (or is asking for)
        basic server information.

        :return: True if basic, False if not
        :rtype: bool

        .. versionadded:: 1.3.0

        Convenience method for identifying basic packets  
        """

        return self.reqtype == QUERYPacket.BASIC_REQUEST or self.reqtype == QUERYPacket.BASIC_RESPONSE

    def is_full(self) -> bool:
        """
        Determines if this packet contains (or is asking for)
        full server information.

        :return: True if full, False if not
        :rtype: bool

        .. versionadded:: 1.3.0

        Convenience method for identifying full packets 
        """

        return self.reqtype == QUERYPacket.FULL_REQUEST or self.reqtype == QUERYPacket.FULL_RESPONSE

    def __repr__(self) -> str:
        """
        Shows packet types and values - Formal way.

        :return: Formal string
        :rtype: str
        """

        return "packet.QUERYPacket({}, {}, chall={}, data={}, data_type={})".format(self.reqtype,
                                                                                    self.reqid,
                                                                                    self.chall,
                                                                                    self.data,
                                                                                    self.data_type)

    def __str__(self) -> str:
        """
        Shows packet in easy to read format - informal way.

        :return: Informal string
        :rtype: str
        """

        return "Query Packet:\nRequest Type: {}\nRequest ID: " \
               "{}\nChallenge Token: {}\nData: {}\nData Type: {}".format(self.reqtype,
                                                                         self.reqid,
                                                                         self.chall,
                                                                         self.data,
                                                                         self.data_type)

    def __bytes__(self) -> bytes:
        """
        Converts the Query packet to bytes.

        :return: Bytes from packet
        :rtype: bytes
        """

        return QUERYEncoder.encode(self.packet_type, self.reqtype, self.reqid, self.chall)


class PINGPacket(BasePacket):
    """
    Class representing a Server List Ping Packet(Or ping for short).

    PINGPackets have the following types:

    - HANDSHAKE - Initial handshake with server, this is always the first operation!
    - STATUS_REQUEST - Client is asking server for status information
    - STATUS_RESPONSE - Server responds to status request with status response, which contains server info
    - PING_REQUEST - Client is asking server to respond with a pong packet, useful for determining latency
    - PONG_RESPONSE - Server responds to ping request with pong response

    The lifecycle of a ping connection is as follows:

    1. Handshake is initiated by client, which MUST be preformed before any operations!
    2. Client may request server status information, server responds. Optionally, clients may skip this step
    3. Client makes a ping request, server responds with pong response, connection is closed

    :param pingnum: Number to use for ping operations
    :type pingnum: int
    :param packet_type: Type of packet we are working with
    :type packet_type: int
    :param data: Ping data from Minecraft server
    :type data: dict, None
    :param proto: Protocol Version used
    :type proto: str, None
    :param host: Hostname of the Minecraft server
    :type host: str, None
    :param port: Port number of the Minecraft server
    :type port: int
    """

    HANDSHAKE: int = PINGEncoder.HANDSHAKE  # Handshake packet, used for initiating connection
    STATUS_REQUEST: int = PINGEncoder.STATUS_REQUEST  # Client asks for server status
    STATUS_RESPONSE: int = PINGEncoder.STATUS_RESPONSE  # Response packet containing server status
    PING_REQUEST: int = PINGEncoder.PING_REQUEST  # Client asks for PING operation to measure latency
    PONG_RESPONSE: int = PINGEncoder.PONG_RESPONSE  # PONG response packet

    def __init__(self, pingnum: int, packet_type: int, data: Union[dict, None] = None, proto: int = 0, host: str = '', port: int = 0):

        self.proto: int = proto  # Protocol version
        self.hostname: str = host  # Hostname of the Minecraft server
        self.port: int = port  # Port of the Minecraft server
        # Ping data from Minecraft server
        self.data: dict = data if data is not None else {}
        self.pingnum: int = pingnum  # Number to use for ping operations
        self.packet_type: int = packet_type  # Type of packet we are working with

    @classmethod
    def from_bytes(cls, byts: bytes) -> PINGPacket:
        """
        Creates a PINGPacket from bytes.

        :param byts: Bytes to decode
        :type byts: bytes
        :return: PINGPacket decoded from bytes
        :rtype: PINGPacket
        """

        data, packet_type = PINGEncoder.decode(byts)

        return cls(0, packet_type, data=data)

    def __repr__(self) -> str:
        """
        Show packet types and values - formal way.

        :return: Formal string
        :rtype: str
        """

        return "packet.PINGPacket({}, {}, {}, {}, {}, {}".format(self.data,
                                                                 self.pingnum,
                                                                 self.packet_type,
                                                                 self.proto,
                                                                 self.hostname,
                                                                 self.port)

    def __str__(self) -> str:
        """
        Show packet in easy to read format - informal way.

        :return: Informal string
        :rtype: str
        """

        return "PINGPacket:\nPacket Data: {}\nPing Number: " \
               "{}\nPacket Type: {}\nProtocol: {}\nHostname: {}\nPort: {}".format(self.data,
                                                                                  self.pingnum,
                                                                                  self.packet_type,
                                                                                  self.proto,
                                                                                  self.hostname,
                                                                                  self.port)

    def __bytes__(self):
        """
        Convert the PINGPacket into bytes.

        :return: Bytes
        """

        return PINGEncoder.encode(self.data, self.pingnum, self.packet_type, self.proto, self.hostname, self.port)
