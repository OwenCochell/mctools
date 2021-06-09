"""
Encoding/Decoding Tools for RCON and Query.
"""


import struct
import json

from typing import Tuple, Union

from mctools.errors import RCONMalformedPacketError, PINGMalformedPacketError


MAP = {''}


class BaseEncoder(object):

    """
    Parent class for encoder implementation.
    """

    @staticmethod
    def encode(data):

        """
        Encodes data, and returns it in byte form.
        Raises 'NotImplementedError' exception, as this function should be overridden in the child class.

        :param data: Data to be encoded
        :return: Bytestring
        """

        raise NotImplementedError("Override this method in child class!")

    @staticmethod
    def decode(data):

        """
        Decodes data, and returns it in workable form(Whatever that may be)
        Raises 'NotImplementedError' exception, as this function should be overridden in the child class.

        :param data: Data to be decoded
        :return: Data in workable format
        """

        raise NotImplementedError("Override this method in child class!")


class RCONEncoder(BaseEncoder):

    """
    RCON Encoder/Decoder.
    """

    PAD = b'\x00\x00'

    @staticmethod
    def encode(data):

        """
        Encodes a RCON packet.

        :param data: Tuple containing packet data
        :return: Bytestring of encoded data
        """

        # Encoding the request ID and Request type:

        byts = struct.pack("<ii", data[0], data[1])

        # Encoding payload and padding:

        byts = byts + data[2].encode("utf8") + RCONEncoder.PAD

        # Encoding length:

        byts = struct.pack("<i", len(byts)) + byts

        return byts

    @staticmethod
    def decode(byts):

        """
        Decodes raw bytestring packet from the RCON server.
        NOTE: DOES NOT DECODE LENGTH! The 'length' vale is omitted, as it is interpreted by the RCONProtocol.
        If your bytestring contains the encoded length, simply remove the first 4 bytes.

        :param byts: Bytestring
        :return: Tuple containing values
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


class QUERYEncoder(BaseEncoder):

    """
    Query encoder/decoder
    """

    IDENT = b'\xfe\xfd'  # Magic bytes to add to the front of the packet
    KEYS = ['motd', 'gametype', 'map', 'numplayers', 'maxplayers', 'hostport', 'hostip']  # For parsing short-stats

    @staticmethod
    def encode(data):

        """
        Encodes a Query Packet.

        :param data: Tuple of data to encode
        :return: Encoded data
        """

        # Converting type to bytes

        byts = data[0].to_bytes(1, "big")

        # Converting request ID
        # Bitwise operation is necessary, as Minecraft Query only interprets the lower 4 bytes

        byts = byts + struct.pack(">i", data[1] & 0x0F0F0F0F)

        # Adding magic bits:

        byts = QUERYEncoder.IDENT + byts

        # Encoding payload - This gets messy, as the payload can be many things

        if data[3] == "basic" or data[3] == "full":

            # Must supply a challenge token to authenticate

            byts = byts + struct.pack(">i", data[2])

        if data[3] == "full":

            # Must add padding, requesting full stats

            byts = byts + b'\x00\x00\x00\x00'

        return byts

    @staticmethod
    def decode(byts):

        """
        Decodes packets from the Query protocol.
        This gets really messy, as the payload can be many different things.
        We also figure out what kind of data we are working with, and return that.

        :param byts: Bytes to decode
        :return: Tuple containing decoded items - reqtype, reqid, chall, data, type
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

            return reqtype, reqid, int(split[0].decode('utf8')), None, "chall"

        # Working with stats data - This gets messy

        if split[0] != 'splitnum' and len(split) <= 7:

            # Working with short stats here:

            short_dict = {}

            for num, val in enumerate(split):

                # Creating short-stats dictionary

                if num == 5:

                    # Dealing with a short instead of string

                    # Adding short to the dictionary

                    short_dict[QUERYEncoder.KEYS[num]] = str(struct.unpack("<H", val[:2])[0])

                    # Overriding values, so hostip can be properly added

                    val = val[2:]
                    num = num + 1

                short_dict[QUERYEncoder.KEYS[num]] = val.replace(b'\x1b', b'\u001b').decode("ISO-8859-1")

            # Return info:

            return reqtype, reqid, None, short_dict, "basic"

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

        return reqtype, reqid, None, data_dict, "full"


class PINGEncoder(BaseEncoder):

    """
    Ping encoder/decoder.
    """

    ID = b'\x00'
    PINGID = b'\x01'

    @staticmethod
    def encode(data):

        """
        Encodes a Ping packet.

        :param data: Data to be encoded, in tuple form
        :return: Bytes
        """

        if data[2] == 'ping':

            # Encoding ping packet here

            byts = PINGEncoder.PINGID + struct.pack(">Q", data[1])

            return PINGEncoder.encode_varint(len(byts)) + byts

        if data[2] == 'req':

            # Working with request packet:

            return PINGEncoder.encode_varint(len(PINGEncoder.ID)) + PINGEncoder.ID

        # Working with handshake packet - Starting with the packet ID, always null byte:

        byts = PINGEncoder.ID

        # Encoding Protocol version:

        byts = byts + PINGEncoder.encode_varint(data[3])

        # Encoding server address:

        host_bytes = data[4].encode("utf8")

        byts = byts + PINGEncoder.encode_varint(len(host_bytes)) + host_bytes

        # Encoding server port:

        byts = byts + struct.pack(">H", data[5])

        # Encoding next state:

        byts = byts + PINGEncoder.encode_varint(1)

        # Encoding length:

        byts = PINGEncoder.encode_varint(len(byts)) + byts

        return byts

    @staticmethod
    def decode(byts) -> Tuple[dict, None, str]:

        """
        Decodes a ping packet.
        NOTE: Bytes provided should NOT include the length,
        that is interpreted and used by the PINGProtocol.

        :param byts: Bytes to decode
        :return: Tuple of decoded values
        """

        # Get the packet type:

        pack_type, type_read = PINGEncoder.decode_varint(byts)

        if pack_type == 0:

            # Working with response packet:

            # Getting length varint:

            length, length_read = PINGEncoder.decode_varint(byts[type_read:])

            return json.loads(byts[length_read+type_read:].decode("utf-8", 'ignore'), strict=False), None, "resp"

        elif pack_type == 1:

            # Working with some other packet type:

            return {}, None, "pong"

        raise PINGMalformedPacketError("Invalid packet type! Must be 1 or 0, not {}!".format(pack_type))

    @staticmethod
    def encode_varint(num: int) -> bytes:

        """
        Encodes a number into varint bytes.

        :param num: Number to encode
        :type num: int
        :return: Bytes
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
    def decode_varint(byts) -> Tuple[int, int]:

        """
        Decodes varint bytes into an integer.
        We also return the amount of bytes read.

        :param byts: Bytes to decode
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
