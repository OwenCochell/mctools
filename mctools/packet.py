"""
Packet classes to hold RCON and Query data
"""

from typing import Union

from mctools.encoding import RCONEncoder, QUERYEncoder, PINGEncoder


class BasePacket(object):

    """
    Parent class for packet implementations.
    """

    @classmethod
    def from_bytes(cls, byts):

        """
        Classmethod to create a packet from bytes.
        Rises an NotImplementedError excpetion, as this function should be overidden in the child class.

        :param byts: Bytes from remote entity
        :return: Packet object
        """

        raise NotImplementedError("Override this method in child class!")

    def __repr__(self):

        """
        Show packet type and values
        """

        raise NotImplementedError("Override this method in child class!")

    def __str__(self):

        """
        Allow for packets to represented in string format, pretty print
        """

        raise NotImplementedError("Override this method in child class!")

    def __bytes__(self):

        """
        Returns a byte-string representation of the packet

        :return: Bytestring of object
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
    """

    def __init__(self, reqid, reqtype, payload, length=0):

        self.reqid = reqid  # Request ID of the RCON packet
        self.reqtype = reqtype  # Request type of the RCON packet
        self.payload = payload  # Payload of the RCON packet
        self.length = length  # Length of the packet, helps determine if we are fragmented
        self.type = 'rcon'  # Determining what type of packet we are

    @classmethod
    def from_bytes(cls, byts):

        """
        Creates a RCON packet from bytes.

        :param byts: Bytes from RCON server
        :return: RCONPacket
        """

        reqid, reqtype, payload = RCONEncoder.decode(byts)

        return cls(reqid, reqtype, payload, length=len(byts))

    def __repr__(self):

        """
        Shows packet type and values - formal way.

        :return: String
        """

        return "packet.RCONPacket({}, {}, {})".format(self.reqid, self.reqtype, self.payload)

    def __str__(self):

        """
        Shows the packet contents in an easy to read format - informal way.

        :return: String.
        """

        return "RCON Packet:\n - Request ID: {}\n - Request Type: {}\n - Payload: {}".format(self.reqid,
                                                                                             self.reqtype,
                                                                                             self.payload)

    def __bytes__(self):

        """
        Converts packet into byte format.

        :return: Byte string.
        """

        return RCONEncoder.encode((self.reqid, self.reqtype, self.payload))


class QUERYPacket(BasePacket):

    """
    Class representing a Query Packet.

    :param reqtype: Type of Query packet
    :type reqtype: int
    :param reqid: Request ID of the Query packet
    :type reqid: int
    :param chall: Challenge token from Query server
    :type chall: str, None
    :param data_type: What type of data we contain
    :type data_type: str
    :param data: Data from the Query server
    :type data: dict
    """

    def __init__(self, reqtype, reqid, chall, data_type, data: dict=None):

        self.reqtype = reqtype  # Type of Query packet
        self.reqid = reqid  # Request ID of the Query packet
        self.chall = chall  # Challenge token from the Query server
        self.data: dict = data if data is not None else {}  # Data from the Query server
        self.data_type = data_type  # Determining what kind of data we contain

    @classmethod
    def from_bytes(cls, byts):

        """
        Creates a Query packet from bytes.

        :param byts: Bytes from Query server
        :return: QUERYPacket.
        """

        # Decoding bytes:

        reqtype, reqid, chall, data, data_type = QUERYEncoder.decode(byts)

        # Creating packet:

        pack = cls(reqtype, reqid, chall, data_type, data=data)

        return pack

    def __repr__(self):

        """
        Shows packet types and values - Formal way.

        :return: String
        """

        return "packet.QUERYPacket({}, {}, chall={}, data={}, data_type={})".format(self.reqtype,
                                                                                    self.reqid,
                                                                                    self.chall,
                                                                                    self.data,
                                                                                    self.data_type)

    def __str__(self):

        """
        Shows packet in easy to read format - informal way.

        :return: String.
        """

        return "Query Packet:\nRequest Type: {}\nRequest ID: " \
               "{}\nChallenge Token: {}\nData: {}\nData Type: {}".format(self.reqtype,
                                                                         self.reqid,
                                                                         self.chall,
                                                                         self.data,
                                                                         self.data_type)

    def __bytes__(self):

        """
        Converts the Query packet to bytes.

        :return: Bytes
        """

        return QUERYEncoder.encode((self.reqtype, self.reqid, self.chall, self.data_type))


class PINGPacket(BasePacket):

    """
    Class representing a Server List Ping Packet(Or ping for short).

    :param pingnum: Number to use for ping operations
    :type pingnum: int
    :param packet_type: Type of packet we are working with
    :type packet_type: str
    :param data: Ping data from Minecraft server
    :type data: dict, None
    :param proto: Protocol Version used
    :type proto: str, None
    :param host: Hostname of the Minecraft server
    :type host: str, None
    :param port: Port number of the Minecraft server
    :type port: int
    """

    def __init__(self, pingnum, packet_type, data: dict=None, proto=None, host=None, port=0):

        self.proto = proto  # Protocol version
        self.hostname = host  # Hostname of the Minecraft server
        self.port = port  # Port of the Minecraft server
        self.data: dict = data if data is not None else {}  # Ping data from Minecraft server
        self.pingnum = pingnum  # Number to use for ping operations
        self.packet_type = packet_type  # Type of packet we are working with

    @classmethod
    def from_bytes(cls, byts):

        """
        Creates a PINGPacket from bytes.

        :param byts: Bytes to decode
        :return: PINGPacket
        """

        data, pingnum, packet_type = PINGEncoder.decode(byts)

        return cls(pingnum, packet_type, data=data)

    def __repr__(self):

        """
        Show packet types and values - formal way.

        :return: String
        """

        return "packet.PINGPacket({}, {}, {}, {}, {}, {}".format(self.data,
                                                                 self.pingnum,
                                                                 self.packet_type,
                                                                 self.proto,
                                                                 self.hostname,
                                                                 self.port)

    def __str__(self):

        """
        Show packet in easy to read format - informal way.

        :return: String
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

        return PINGEncoder.encode((self.data, self.pingnum, self.packet_type, self.proto, self.hostname, self.port))
