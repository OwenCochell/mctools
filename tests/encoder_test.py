"""
Tests for encoding components.

We test to ensure each encoding component behaves the way we expect.
We keep testing data inputs and outputs for various scenarios,
and use this to ensure properly functionality.
"""

import unittest
import random
import string

from mctools.encoding import RCONEncoder, QUERYEncoder, PINGEncoder


class RCONEncoderTest(unittest.TestCase):
    """
    Ensures the RCONEncoder behaves correctly.
    """

    KNOWN_ENCODE_IN = (1, 2, 'encode')
    KNOWN_ENCODE_OUT = b'\x10\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00encode\x00\x00'

    KNOWN_DECODE_IN = b'\x10\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00decode\x00\x00'
    KNOWN_DECODE_OUT = (3, 4, 'decode')

    def setUp(self) -> None:

        self.encoder = RCONEncoder()

    def test_initial(self):
        """
        Ensures initial values and constants are valid
        """

        self.assertEqual(self.encoder.PAD, b'\x00\x00')

    def test_encode(self):
        """
        Ensures out known values encode correctly
        """

        # Encode the test values:

        out = self.encoder.encode(*self.KNOWN_ENCODE_IN)

        # Ensure output matches expected:

        self.assertEqual(out, self.KNOWN_ENCODE_OUT)

    def test_decode(self):
        """
        Ensures in known values encode correctly
        """

        # Decode the test values:

        out = self.encoder.decode(self.KNOWN_DECODE_IN[4:])

        # Ensure values are valid:

        self.assertTupleEqual(out, self.KNOWN_DECODE_OUT)

    def test_random(self):
        """
        Generates random values, encodes them, then decodes them
        and compares results.
        """

        # Get max long value:

        max_long = 0xFFFF

        # Determine request id:

        reqid = random.randrange(-max_long, max_long)

        # Determine request type:

        reqtype = random.randrange(0, max_long)

        # Get random string:

        payload = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=random.randrange(1, 300)))

        # Encode the data:

        enc = self.encoder.encode(reqid, reqtype, payload)

        # Send the data through the decoder:

        dec = self.encoder.decode(enc[4:])

        # Ensure the values are identical:

        self.assertEqual(reqid, dec[0])
        self.assertEqual(reqtype, dec[1])
        self.assertEqual(payload, dec[2])


class QUERYEncoderTest(unittest.TestCase):
    """
    Ensures the QUERYEncoder behaves correctly
    """

    KNOWN_HANDSHAKE_ENCODE_AUTO_IN = (
        QUERYEncoder.HANDSHAKE_REQUEST, -1, 1, -1)
    KNOWN_HANDSHAKE_ENCODE_AUTO_OUT = b'\xfe\xfd\t\x00\x00\x00\x01'

    KNOWN_HANDSHAKE_ENCODE_MAN_IN = (QUERYEncoder.HANDSHAKE_REQUEST, 4, 2, -1)
    KNOWN_HANDSHAKE_ENCODE_MAN_OUT = b'\xfe\xfd\x04\x00\x00\x00\x02'

    KNOWN_BASIC_ENCODE_AUTO_IN = (QUERYEncoder.BASIC_REQUEST, -1, 5, 55)
    KNOWN_BASIC_ENCODE_AUTO_OUT = b'\xfe\xfd\x00\x00\x00\x00\x05\x00\x00\x007'

    KNOWN_BASIC_ENCODE_MAN_IN = (QUERYEncoder.BASIC_REQUEST, 33, 6, 66)
    KNOWN_BASIC_ENCODE_MAN_OUT = b'\xfe\xfd!\x00\x00\x00\x06\x00\x00\x00B'

    KNOWN_FULL_ENCODE_AUTO_IN = (QUERYEncoder.FULL_REQUEST, -1, 7, 77)
    KNOWN_FULL_ENCODE_AUTO_OUT = b'\xfe\xfd\x00\x00\x00\x00\x07\x00\x00\x00M\x00\x00\x00\x00'

    KNOWN_FULL_ENCODE_MAN_IN = (QUERYEncoder.FULL_REQUEST, 44, 8, 88)
    KNOWN_FULL_ENCODE_MAN_OUT = b'\xfe\xfd,\x00\x00\x00\x08\x00\x00\x00X\x00\x00\x00\x00'

    KNOWN_HANDSHAKE_DECODE_IN = b'\x09\x00\x00\x00\x031234'
    KNOWN_HANDSHAKE_DECODE_OUT = (
        QUERYEncoder.HANDSHAKE_RESPONSE, 3, 1234, {}, QUERYEncoder.HANDSHAKE_TYPE)

    KNOWN_BASIC_DECODE_IN = b'\x00\x05\x0e\x08\x07A Minecraft Server\x00SMP\x00world\x000\x0020\x00\xddc127.0.0.1\x00'
    KNOWN_BASIC_DECODE_OUT = (QUERYEncoder.BASIC_RESPONSE, 84805639, -1, {'gametype': 'SMP',
                                                                          'hostip': '127.0.0.1',
                                                                          'hostport': '25565',
                                                                          'map': 'world',
                                                                          'maxplayers': '20',
                                                                          'motd': 'A Minecraft Server',
                                                                          'numplayers': '0'}, QUERYEncoder.STAT_TYPE)

    KNOWN_FULL_DECODE_IN = b'\x00\x05\x0e\x08\x07splitnum\x00\x80\x00hostname\x00A Minecraft Server\x00gametype\x00SMP\x00game_id\x00MINECRAFT\x00version\x001.8.8\x00plugins\x00CraftBukkit on Bukkit 1.8.8-R0.1-SNAPSHOT\x00map\x00world\x00numplayers\x000\x00maxplayers\x0020\x00hostport\x0025565\x00hostip\x00127.0.0.1\x00\x00\x01player_\x00\x00\x00'
    KNOWN_FULL_DECODE_OUT = (QUERYEncoder.FULL_RESPONSE, 84805639, -1, {'game_id': 'MINECRAFT',
                                                                        'gametype': 'SMP',
                                                                        'hostip': '127.0.0.1',
                                                                        'hostport': '25565',
                                                                        'map': 'world',
                                                                        'maxplayers': '20',
                                                                        'motd': 'A Minecraft Server',
                                                                        'numplayers': '0',
                                                                        'players': [''],
                                                                        'plugins': 'CraftBukkit on Bukkit 1.8.8-R0.1-SNAPSHOT',
                                                                        'version': '1.8.8'}, QUERYEncoder.STAT_TYPE)

    def setUp(self) -> None:
        self.encoder = QUERYEncoder()

    def test_initial(self):
        """
        Ensures initial defaults and values are accurate
        """

        self.assertEqual(QUERYEncoder.IDENT, b'\xfe\xfd')

        self.assertListEqual(QUERYEncoder.KEYS, ['motd', 'gametype', 'map', 'numplayers', 'maxplayers',
                                                 'hostport', 'hostip'])

        self.assertEqual(QUERYEncoder.BASIC_REQUEST, 0)
        self.assertEqual(QUERYEncoder.BASIC_RESPONSE, 1)  # Basic data response
        self.assertEqual(QUERYEncoder.FULL_REQUEST, 2)  # Full data request
        self.assertEqual(QUERYEncoder.FULL_RESPONSE, 3)  # Full data response
        self.assertEqual(QUERYEncoder.HANDSHAKE_REQUEST,
                         5)  # Challenge request packet
        self.assertEqual(QUERYEncoder.HANDSHAKE_RESPONSE,
                         6)  # Challenge response packet

        # QUERY type for getting stats
        self.assertEqual(QUERYEncoder.STAT_TYPE, 0)
        # QUERY type for preforming handshake
        self.assertEqual(QUERYEncoder.HANDSHAKE_TYPE, 9)

    def test_encode_handshake(self):
        """
        Ensures the handshake can be encoded
        """

        # Test with packet types:

        out = self.encoder.encode(*self.KNOWN_HANDSHAKE_ENCODE_AUTO_IN)

        self.assertEqual(out, self.KNOWN_HANDSHAKE_ENCODE_AUTO_OUT)

        # Test with manual request type:

        out = self.encoder.encode(*self.KNOWN_HANDSHAKE_ENCODE_MAN_IN)

        self.assertEqual(out, self.KNOWN_HANDSHAKE_ENCODE_MAN_OUT)

    def test_encode_basic(self):
        """
        Ensures basic data can be encoded
        """

        # Test with packet type:

        out = self.encoder.encode(*self.KNOWN_BASIC_ENCODE_AUTO_IN)

        self.assertEqual(out, self.KNOWN_BASIC_ENCODE_AUTO_OUT)

        # Test with manual request type:

        out = self.encoder.encode(*self.KNOWN_BASIC_ENCODE_MAN_IN)

        self.assertEqual(out, self.KNOWN_BASIC_ENCODE_MAN_OUT)

    def test_encode_full(self):
        """
        Ensures full data can be encoded
        """

        # Test with packet type:

        out = self.encoder.encode(*self.KNOWN_FULL_ENCODE_AUTO_IN)

        self.assertEqual(out, self.KNOWN_FULL_ENCODE_AUTO_OUT)

        # Test with manual type:

        out = self.encoder.encode(*self.KNOWN_FULL_ENCODE_MAN_IN)

        self.assertEqual(out, self.KNOWN_FULL_ENCODE_MAN_OUT)

    def test_decode_handshake(self):
        """
        Ensures handshake data can be decoded
        """

        # Decode handshake data:

        out = self.encoder.decode(self.KNOWN_HANDSHAKE_DECODE_IN)

        self.assertTupleEqual(out, self.KNOWN_HANDSHAKE_DECODE_OUT)

    def test_decode_basic(self):
        """
        Ensures basic data can be decoded
        """

        # Ensure we can decide basic responses

        out = self.encoder.decode(self.KNOWN_BASIC_DECODE_IN)

        self.assertTupleEqual(out, self.KNOWN_BASIC_DECODE_OUT)

    def test_decode_full(self):
        """
        Ensures full data can be decoded
        """

        # Ensure we can decode full responses:

        out = self.encoder.decode(self.KNOWN_FULL_DECODE_IN)

        self.assertTupleEqual(out, self.KNOWN_FULL_DECODE_OUT)


class PINGEncoderTest(unittest.TestCase):
    """
    Ensures the PINGEncoder behaves correctly
    """

    KNOWN_HANDSHAKE_ENCODE_IN = (
        {}, -1, PINGEncoder.HANDSHAKE, 0, 'localhost', 25565)
    KNOWN_HANDSHAKE_ENCODE_OUT = b'\x0f\x00\x00\tlocalhostc\xdd\x01'

    KNOWN_STATUS_ENCODE_IN = (
        {}, -1, PINGEncoder.STATUS_REQUEST, 0, 'localhost', 25565)
    KNOWN_STATUS_ENCODE_OUT = b'\x01\x00'

    KNOWN_PING_ENCODE_IN = (
        {}, 55, PINGEncoder.PING_REQUEST, 0, 'localhost', 25565)
    KNOWN_PING_ENCODE_OUT = b'\t\x01\x00\x00\x00\x00\x00\x00\x007'

    KNOWN_STATUS_DECODE_IN = b'\x00y{"description":"A Minecraft Server","players":{"max":20,"online":0},"version":{"name":"PaperSpigot 1.8.8","protocol":47}}'
    KNOWN_STATUS_DECODE_OUT = ({'description': 'A Minecraft Server',
                                'players': {'max': 20, 'online': 0},
                                'version': {'name': 'PaperSpigot 1.8.8', 'protocol': 47}}, PINGEncoder.STATUS_RESPONSE)

    KNOWN_PING_DECODE_IN = b'\x01\x00\x00\x00\x00e\xee?\xe2'
    KNOWN_PING_DECODE_OUT = ({}, PINGEncoder.PONG_RESPONSE)

    def setUp(self) -> None:
        self.encoder = PINGEncoder()

    def test_initial(self):
        """
        Ensures the initial values and constants are valid
        """

        self.assertEqual(PINGEncoder.ID, b'\x00')
        self.assertEqual(PINGEncoder.PINGID, b'\x01')

        self.assertEqual(PINGEncoder.HANDSHAKE, 0)
        self.assertEqual(PINGEncoder.STATUS_REQUEST, 1)
        self.assertEqual(PINGEncoder.STATUS_RESPONSE, 2)
        self.assertEqual(PINGEncoder.PING_REQUEST, 3)
        self.assertEqual(PINGEncoder.PONG_RESPONSE, 4)

    def test_encode_handshake(self):
        """
        Ensures we can properly encode the handshake
        """

        # Encode and check handshake

        out = self.encoder.encode(*self.KNOWN_HANDSHAKE_ENCODE_IN)

        self.assertEqual(out, self.KNOWN_HANDSHAKE_ENCODE_OUT)

    def test_encode_status(self):
        """
        Ensures we can properly encode the status request
        """

        # Encode and check status request

        out = self.encoder.encode(*self.KNOWN_STATUS_ENCODE_IN)

        self.assertEqual(out, self.KNOWN_STATUS_ENCODE_OUT)

    def test_encode_ping(self):
        """
        Ensures we can properly encode the ping request
        """

        # Encode and check ping request

        out = self.encoder.encode(*self.KNOWN_PING_ENCODE_IN)

        self.assertEqual(out, self.KNOWN_PING_ENCODE_OUT)

    def test_decode_status(self):
        """
        Ensures we can properly decode the status response
        """

        # Decode and check status response

        out = self.encoder.decode(self.KNOWN_STATUS_DECODE_IN)

        self.assertEqual(out, self.KNOWN_STATUS_DECODE_OUT)

    def test_decode_ping(self):
        """
        Ensures we can properly decode the ping response
        """

        # Decode and check ping response

        out = self.encoder.decode(self.KNOWN_PING_DECODE_IN)

        self.assertEqual(out, self.KNOWN_PING_DECODE_OUT)
