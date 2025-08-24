"""
Encoding/Decoding components for RCON and Query.
"""

import struct
import json
import asyncio

from typing import Tuple, List

from mctools.errors import RCONMalformedPacketError, PINGMalformedPacketError

MAP = {''}


class RCONEncoder:
    """
    RCON Encoder/Decoder.
    """

    PAD = b'\x00\x00'

    @staticmethod
    def encode(reqid: int, reqtype: int, payload: str) -> bytes:
        """
        Encodes a RCON packet.

        :param reqid: Request ID of RCON packet
        :type reqid: int
        :param reqtype: Request type of RCON packet
        :type reqtype: int
        :param payload: Payload of RCON packet
        :type payload: str
        :return: Bytestring of encoded data
        :rtype: bytes
        """

        # Encoding the request ID and Request type:

        byts = struct.pack("<ii", reqid, reqtype)

        # Encoding payload and padding:

        byts += payload.encode("utf8") + RCONEncoder.PAD

        # Encoding length:

        byts = struct.pack("<i", len(byts)) + byts

        return byts

    @staticmethod
    def decode(byts: bytes) -> Tuple[int, int, str]:
        """
        Decodes raw bytestring packet from the RCON server.
        NOTE: DOES NOT DECODE LENGTH! The 'length' value is omitted, as it is interpreted by the RCONProtocol.
        If your bytestring contains the encoded length, simply remove the first 4 bytes.

        :param byts: Bytestring to decode
        :type byts: bytes
        :return: Tuple containing values, request ID, request type, payload
        :rtype: Tuple[int, int, str]
        """

        # Getting request ID and request type

        reqid, reqtype = struct.unpack("<ii", byts[:8])

        # Getting payload

        payload = byts[8:len(byts)-2]

        # Checking padding:

        if not byts[len(byts) - 2:] == RCONEncoder.PAD:

            # No padding detected, something is wrong:

            raise RCONMalformedPacketError("Missing or malformed padding!")

        # Returning values:

        return reqid, reqtype, payload.decode("utf8")


class QUERYEncoder:
    """
    Query encoder/decoder
    """

    IDENT: bytes = b'\xfe\xfd'  # Magic bytes to add to the front of the packet
    KEYS: List[str] = ['motd', 'gametype', 'map', 'numplayers', 'maxplayers',
            'hostport', 'hostip']  # For parsing short-stats

    BASIC_REQUEST: int = 0  # Basic data request
    BASIC_RESPONSE: int = 1  # Basic data response
    FULL_REQUEST: int = 2  # Full data request
    FULL_RESPONSE: int = 3  # Full data response
    HANDSHAKE_REQUEST: int = 5  # Challenge request packet
    HANDSHAKE_RESPONSE: int = 6  # Challenge response packet

    STAT_TYPE: int = 0  # QUERY type for getting stats
    HANDSHAKE_TYPE: int = 9  # QUERY type for preforming handshake

    @staticmethod
    def encode(packet_type: int, reqtype: int, reqid: int, chall: int) -> bytes:
        """
        Encodes a Query Packet.

        :param packet_type: Type of query packet
        :type packet_type: int
        :param reqtype: Type of request, will be auto-determined if (-1)
        :type reqtype: int
        :param reqid: Request ID of query packet
        :type reqid: int
        :param chall: Challenge token from query server
        :type chall: int
        :return: Encoded data
        :rtype: bytes

        .. versionchanged: 1.3.0

        We no longer consider the 'data_type', we only do checking using the packet type.

        If reqtype is not provided (-1), we determine the value using the packet_type parameter.

        Input parameters have been changed
        """

        # Determine if we need to figure out request type:

        if reqtype == -1:

            # Are we a handshake request:

            if packet_type == QUERYEncoder.HANDSHAKE_REQUEST:

                # Set request type to handshake:

                reqtype = QUERYEncoder.HANDSHAKE_TYPE

            # Are we a stat request:

            elif packet_type == QUERYEncoder.FULL_REQUEST or packet_type == QUERYEncoder.BASIC_REQUEST:

                # Set request type to stat:

                reqtype = QUERYEncoder.STAT_TYPE

            else:

                # Neither, raise an error:

                raise ValueError("Bad packet type provided!")

        # Converting type to bytes

        byts = reqtype.to_bytes(1, "big")

        # Converting request ID
        # Bitwise operation is necessary, as Minecraft Query only interprets the lower 4 bytes

        byts += struct.pack(">i", reqid & 0x0F0F0F0F)

        # Adding magic bits:

        byts = QUERYEncoder.IDENT + byts

        # Encoding payload - This gets messy, as the payload can be many things

        if packet_type == QUERYEncoder.BASIC_REQUEST or packet_type == QUERYEncoder.FULL_REQUEST:

            # Must supply a challenge token to authenticate

            byts += struct.pack(">i", chall)

        if packet_type == QUERYEncoder.FULL_REQUEST:

            # Must add padding, requesting full stats

            byts += b'\x00\x00\x00\x00'

        return byts

    @staticmethod
    def decode(byts: bytes) -> Tuple[int, int, int, dict, int]:
        """
        Decodes packets from the Query protocol.
        This gets really messy, as the payload can be many different things.
        We also figure out what kind of data we are working with, and return that.

        :param byts: Bytes to decode
        :type byts: bytes
        :return: Tuple containing decoded items - packet_type, reqid, chall, data, reqtype
        :rtype: Tuple[int, int, int, dict, str]

        .. versionchanged:: 1.3.0

        Changed the return values
        """

        # Getting type here:

        reqtype = byts[0]

        # Getting request ID:

        reqid = struct.unpack(">i", byts[1:5])[0]

        # Checking the payload to determine what we are working with:

        # Splitting up payload into parts

        split = byts[5:].rstrip(b'\x00').split(b'\x00')

        if len(split) == 1:

            # Working with challenge token - Getting challenge token:

            # Returning info:

            return QUERYEncoder.HANDSHAKE_RESPONSE, reqid, int(split[0].decode('utf8')), {}, reqtype

        # Working with stats data - This gets messy

        if split[0] != 'splitnum' and len(split) <= 7:

            # Working with short stats here:

            short_dict = {}

            for num, val in enumerate(split):

                # Creating short-stats dictionary

                if num == 5:

                    # Dealing with a short instead of string

                    # Adding short to the dictionary

                    short_dict[QUERYEncoder.KEYS[num]] = str(
                        struct.unpack("<H", val[:2])[0])

                    # Overriding values, so hostip can be properly added

                    val = val[2:]
                    num = num + 1

                short_dict[QUERYEncoder.KEYS[num]] = val.replace(
                    b'\x1b', b'\u001b').decode("ISO-8859-1")

            # Return info:

            return QUERYEncoder.BASIC_RESPONSE, reqid, -1, short_dict, reqtype

        # Working with full stats - This gets even more messy

        # Splitting bytes by b'\x00' - Null bytes

        total = byts[15:].split(b'\x00\x01player_\x00\x00')

        # Replacing some nulls with actual values, and removing leading/trailing nulls
        # (And changing a keyvalue to what it should be)

        total[0] = total[0].replace(b'hostname', b'motd', 1).replace(b'\x00\x00', b'\x00 \x00')\
            .replace(b'\x00', b'', 1).rstrip(b'\x00')

        total[1] = total[1].rstrip(b'\x00')

        # Parsing stats:

        stats_split = total[0].split(b'\x00')
        data_dict = {}

        for num in range(0, len(stats_split), 2):

            # Adding first value and second to dictionary

            data_dict[stats_split[num].decode("utf8")] = stats_split[num + 1].replace(b'\x1b', b'\u001b').\
                decode("ISO-8859-1")

        # Parsing players:

        data_dict['players'] = []

        for val in total[1].split(b'\x00'):

            # Adding player to list

            data_dict['players'].append(val.decode("utf8"))

        # Returning info

        return QUERYEncoder.FULL_RESPONSE, reqid, -1, data_dict, reqtype


class PINGEncoder:
    """
    Ping encoder/decoder.
    """

    ID = b'\x00'
    PINGID = b'\x01'

    HANDSHAKE: int = 0  # Handshake packet, used for initiating connection
    STATUS_REQUEST: int = 1  # Client asks for server status
    STATUS_RESPONSE: int = 2  # Response packet containing server status
    PING_REQUEST: int = 3  # Client asks for PING operation to measure latency
    PONG_RESPONSE: int = 4  # PONG response packet

    @staticmethod
    def encode(data: dict, pingnum: int, packet_type: int, proto: int, hostname: str, port: int) -> bytes:
        """
        Encodes a Ping packet.

        :param data: Ping data from server
        :type data: dict
        :param pingnum: Number for ping operations
        :type pingnum: int
        :param packet_type: Type of packet we are working with
        :type packet_type: int
        :param proto: Protocol version number
        :type proto: int
        :param hostname: Hostname of the minecraft server
        :type hostname
        :param port: Port we are connecting to
        :type port: int
        :return: Encoded data
        :rtype: bytes

        .. versionchanged:: 1.3.0

        We now raise an exception if invalid packet type is provided
        """

        if packet_type == PINGEncoder.PING_REQUEST:

            # Encoding ping request packet here

            byts = PINGEncoder.PINGID + struct.pack(">Q", pingnum)

            return PINGEncoder.encode_varint(len(byts)) + byts

        if packet_type == PINGEncoder.STATUS_REQUEST:

            # Working with status request packet:

            return PINGEncoder.encode_varint(len(PINGEncoder.ID)) + PINGEncoder.ID

        if packet_type == PINGEncoder.HANDSHAKE:

            # Working with handshake packet - Starting with the packet ID, always null byte:

            byts = PINGEncoder.ID

            # Encoding Protocol version:

            byts += PINGEncoder.encode_varint(proto)

            # Encoding server address:

            host_bytes = hostname.encode("utf8")

            byts += PINGEncoder.encode_varint(len(host_bytes)) + host_bytes

            # Encoding server port:

            byts += struct.pack(">H", port)

            # Encoding next state:

            byts += PINGEncoder.encode_varint(1)

            # Encoding length:

            byts = PINGEncoder.encode_varint(len(byts)) + byts

            return byts

        # Otherwise, raise an error as the packet type is bad:

        raise ValueError("Bad PINGPacket type! MUST be set using PINGPacket constants!")

    @staticmethod
    def decode(byts: bytes) -> Tuple[dict, int]:
        """
        Decodes a ping packet.
        NOTE: Bytes provided should NOT include the length,
        that is interpreted and used by the PINGProtocol.

        :param byts: Bytes to decode
        :type byts: bytes
        :return: Tuple of decoded values, data and packet type
        :rtype: Tuple[dict, str]
        """

        # Get the packet type:

        pack_type, type_read = PINGEncoder.decode_varint(byts)

        if pack_type == 0:

            # Working with response packet:

            # Getting length varint:

            length, length_read = PINGEncoder.decode_varint(byts[type_read:])

            return json.loads(byts[length_read+type_read:].decode("utf-8", 'ignore'), strict=False), PINGEncoder.STATUS_RESPONSE

        elif pack_type == 1:

            # Working with some other packet type:

            return {}, PINGEncoder.PONG_RESPONSE

        raise PINGMalformedPacketError(
            "Invalid packet type! Must be 1 or 0, not {}!".format(pack_type))

    @staticmethod
    def encode_varint(num: int) -> bytes:
        """
        Encodes a number into varint bytes.

        :param num: Number to encode
        :type num: int
        :return: Encoded bytes
        :rtype: bytes
        """

        byts: bytes = b''
        remaining = num

        # Iterating over the content, and doing the necessary bitwise stuff

        for b in range(5):

            if remaining & ~0x7F == 0:

                # Found our stuff, exit

                break

            byts = byts + struct.pack("!B", remaining & 0x7F | 0x80)
            remaining >>= 7

        byts = byts + struct.pack("!B", remaining)
        return byts

    @staticmethod
    def decode_varint(byts: bytes) -> Tuple[int, int]:
        """
        Decodes varint bytes into an integer.
        We also return the amount of bytes read.

        :param byts: Bytes to decode
        :type byts: bytes
        :return: result, bytes read
        :rtype: int, int
        """

        result = 0
        b = 0

        # Iterate over the result, and do the necessary bitwise stuff:

        for b in range(5):

            part = byts[b]
            result |= (part & 0x7F) << (7 * b)

            if not part & 0x80:

                # Fond our part, time to exit

                return result, b + 1

        return result, b + 1

    @staticmethod
    def decode_sock(sock) -> int:
        """
        Decodes a var(int/long) of variable length or value.
        We use a socket to continuously pull values until we reach a valid value,
        as the length of these var(int/long)s can be either very long or very short.

        :param sock: Socket object to get bytes from.
        :type sock: socket.socket
        :return: Decoded integer
        :rtype: int
        """

        result = 0  # Outcome of the operation
        read = 0  # Number of times we read

        while True:

            # Getting a byte:

            part = sock.recv(1)

            if len(part) == 0:

                # Can't work with this, must be done.

                break

            # Change into something we can understand:

            byte = ord(part)

            # Do our bitwise operation:

            result |= (byte & 0x7F) << 7 * read

            # Increment the amount of times we read:

            read = read + 1

            if not byte & 0x80:

                # Found the end:

                break

            if read > 10:

                # Varint/long is way too big, throw an error

                raise Exception("Varint/long is greater than 10!")

        return result

    @staticmethod
    async def adecode_sock(reader: asyncio.StreamReader, timeout: int | None) -> int:
        """
        Decodes a var(int/long) of variable length or value.
        We use a socket to continuously pull values until we reach a valid value,
        as the length of these var(int/long)s can be either very long or very short.

        :param sock: Socket object to get bytes from.
        :type sock: socket.socket
        :return: Decoded integer
        :rtype: int
        """

        result = 0  # Outcome of the operation
        read = 0  # Number of times we read

        while True:

            # Getting a byte:

            part = await asyncio.wait_for(reader.read(1), timeout)

            if len(part) == 0:

                # Can't work with this, must be done.

                break

            # Change into something we can understand:

            byte = ord(part)

            # Do our bitwise operation:

            result |= (byte & 0x7F) << 7 * read

            # Increment the amount of times we read:

            read = read + 1

            if not byte & 0x80:

                # Found the end:

                break

            if read > 10:

                # Varint/long is way too big, throw an error

                raise ProtocolError("Varint/long is greater than 10!")

        return result