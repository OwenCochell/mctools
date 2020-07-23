import time
from mctools.protocol import RCONProtocol, QUERYProtocol, PINGProtocol
from mctools.packet import RCONPacket, QUERYPacket, PINGPacket
from mctools.formattertools import FormatterCollection, DefaultFormatter, QUERYFormatter, PINGFormatter

"""
Main Minecraft Connection Clients - Easy to use API for the underlying modules
Combines the following:
    - Protocol Implementations
    - Packet implementations
    - Formatting tools
"""


class BaseClient(object):

    """
    Parent class for Minecraft Client implementations.
    This class has the following formatting constants, which every client inherits:

      - BaseClient.RAW - Tells the client to not format any content.
      - BaseClient.REPLACE - Tells the client to replace format characters.
      - BaseClient.Remove - Tells the client to remove format characters.

    You can use these constants in the 'format_method' parameter in each client.
    """

    # Formatting codes

    RAW = 0
    REPLACE = 1
    REMOVE = 2

    def gen_reqid(self):

        """
        Generates a request ID using system time.

        :return: System time as an integer
        """

        return int(time.time())

    def start(self):

        """
        Starts the client, and any modules in use.
        (Good idea to put a call to Protocol.start() here).
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.
        """

        raise NotImplementedError("Override this method in child class!")

    def stop(self):

        """
        Stops the client, and any modules in use.
        (Again, good idea to put a call to Protocol.stop() here).
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.
        """

        raise NotImplementedError("Override this method in child class!")

    def is_connected(self):

        """
        Determine if we are connected to the remote entity.
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :return: True if connected, False if not.
        """

        raise NotImplementedError("Override this method in child class!")

    def raw_send(self, *args):

        """
        For sending packets with user defined values, instead of the wrappers from client.
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :param args: Arguments specified, varies from client to client.
        """

        raise NotImplementedError("Override this method in child class!")

    def get_formatter(self):

        """
        Returns the formatter used by this instance,
        Allows the user to change formatter operations.

        :return: FormatterCollection used by the client.
        :rtype: FormatterCollection
        """

        return self.formatters

    def __enter__(self):

        """
        All clients MUST have context manager support!

        :return:
        """

        raise NotImplementedError("Override this method in child class!")

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        All clients MUST have context manager support!
        (Recommend showing exceptions, AKA returning False)

        :param exc_type: Exception info
        :param exc_val: Exception info
        :param exc_tb: Exception inf
        :return: False(Can be something else)
        """

        raise NotImplementedError("Override this method in child class!")


class RCONClient(BaseClient):

    """
    RCON client, allows for user to interact with the Minecraft server via the RCON protocol.

    :param host: Hostname of the Minecraft server
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as 'None' to generate one based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :param format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    """

    def __init__(self, host, port=25575, reqid=None, format_method=BaseClient.REPLACE, timeout=60):

        self.proto = RCONProtocol(host, port, timeout)  # RCONProtocol, used for communicating with RCON server
        self.formatters = FormatterCollection()  # Formatters instance, formats text from server
        self.auth = False  # Value determining if we are authenticated
        self.format = format_method  # Value determining how to format output

        self.reqid = self.gen_reqid() if reqid is None else int(reqid)  # Generating a request ID

        # Adding the relevant formatters:

        self.formatters.add(DefaultFormatter, '', ignore=[self.formatters.PING, self.formatters.QUERY])

    def start(self):

        """
        Starts the connection to the RCON server.
        This is called automatically where appropriate,
        so you shouldn't have to worry about calling this.
        """

        # Start the protocol instance:

        if not self.is_connected():

            self.proto.start()

    def stop(self):

        """
        Stops the connection to the RCON server.
        This function should always be called when ceasing network communications,
        as not doing so could cause problems server-side.
        """

        # Stop the protocol instance

        if self.is_connected():

            self.auth = False

            self.proto.stop()

    def is_connected(self):

        """
        Determines if we are connected.

        :return: True if connected, False if not.
        :rtype: bool
        """

        return self.proto.connected

    def is_authenticated(self):

        """
        Determines if we are authenticated.

        :return: True if authenticated, False if not.
        :rtype: bool
        """

        return self.auth

    def raw_send(self, reqtype, payload):

        """
        Creates a RCON packet based off the following parameters and sends it.

        :param reqtype: Request type
        :type reqtype: int
        :param payload: Payload to send
        :type payload: str
        :return: RCONPacket containing response from server
        :rtype: RCONPacket
        """

        if not self.is_connected():

            # Connection not started, user obviously wants to connect, so start it

            self.start()

        # Sending packet:

        self.proto.send(RCONPacket(self.reqid, reqtype, payload))

        # Receiving response packet:

        pack = self.proto.read()

        return pack

    def login(self, password):

        """
        Authenticates with the RCON server using the given password.
        If we are already authenticated, then we simply return True.

        :param password: RCON Password
        :type password: str
        :return: True if successful, False if failure
        :rtype: bool
        """

        # Checking if we are logged in.

        if self.is_authenticated():

            # Already authenticated, no need to do it again.

            return True

        # Sending login packet:

        pack = self.raw_send(self.proto.LOGIN, password)

        # Checking login packet

        if pack.reqid != self.reqid:

            # Login failed, request IDs do not match

            return False

        # Request ID matches!

        self.auth = True

        return True

    def authenticate(self, password):

        """
        Convience function, does the same thing that 'login' does, authenticates you with the RCON server.

        :param password: Password to authenticate with
        :return: True if successful, False if failure
        :rtype: bool
        """

        return self.login(password)

    def command(self, com, no_auth=False):

        """
        Sends a command to the RCON server and gets a response.

        :param com: Command to send
        :type com: str
        :param no_auth: Value determining if we should check authentication status.
        :type no_auth: False
        :return: Response text from server
        :rtype: str
        """

        # Getting command packet:

        self.proto.send(RCONPacket(self.reqid, 2, com))

        # Getting response packet:

        pack = self.proto.read()

        if pack.reqid != self.reqid:

            # We are not logged in!

            raise Exception("Client is not authenticated!")

        # Formatting text:

        if self.format == 'replace' or self.format == 1:

            # Replacing format chars

            pack.payload = self.formatters.format(pack.payload, com)

        elif self.format == 'clean' or self.format == 2:

            # Removing format chars

            pack.payload = self.formatters.clean(pack.payload, com)

        return pack.payload

    def __enter__(self):

        """
        In a context manager.

        :return: This instance
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        Exit the context manager, show any necessary errors as they are important.

        :param exc_type: Error info
        :param exc_val:  Error info
        :param exc_tb:  Error info
        :return: False
        """

        # Stopping connection:

        self.stop()

        return False


class QUERYClient(BaseClient):

    """
    Query client, allows for user to interact with the Minecraft server via the Query protocol.

    :param host: Hostname of the Minecraft server
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as 'None' to generate one based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :type format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    """

    def __init__(self, host, port=25565, reqid=None, format_method=BaseClient.REPLACE, timeout=60):

        self.proto = QUERYProtocol(host, port, timeout)  # Query protocol instance
        self.formatters = FormatterCollection()  # Formatters instance
        self.format = format_method  # Format type to use

        self.reqid = self.gen_reqid() if reqid is None else int(reqid)

        # Adding the relevant formatters

        self.formatters.add(QUERYFormatter, self.formatters.QUERY)

    def start(self):

        """
        Starts the Query object. This is called automatically where appropriate,
        so you shouldn't have to worry about calling this.
        """

        if not self.is_connected():

            self.proto.start()

    def stop(self):

        """
        Stops the connection to the Query server.
        In this case, it is not strictly necessary to stop the connection,
        as QueryClient uses the UDP protocol. It is still recommended to stop the instance any way,
        so you can be explicit in your code as to when you are going to stop communicating over the network.
        """

        if self.is_connected():

            self.proto.stop()

    def is_connected(self):

        """
        Determines if we are connected.
        (UPD doesn't really work that way, so we simply return if we have been started).

        :return: True if started, False for otherwise.
        :rtype: bool
        """

        return self.proto.started

    def raw_send(self, reqtype, chall, packet_type):

        """
        Creates a packet from the given arguments and sends it.
        Returns a response.

        :param reqtype: Request type
        :type reqtype: int
        :param chall: Challenge Token
        :type chall: str, None
        :param packet_type: Packet type(chall, short, full)
        :type packet_type: str
        :return: QUERYPacket containing response
        :rtype: QUERYPacket
        """

        # Sending packet:

        self.proto.send(QUERYPacket(reqtype, self.reqid, chall, packet_type))

        # Receiving response packet:

        pack = self.proto.read()

        return pack

    def get_challenge(self):

        """
        Gets the challenge token from the Query server.
        It is necessary to get a token before every operation,
        as the Query tokens change every 30 seconds.

        :return: QueryPacket containing challenge token.
        :rtype: QUERYPacket
        """

        # Sending initial packet:

        pack = self.raw_send(9, None, "chall")

        # Returning pack:

        return pack

    def get_basic_stats(self):

        """
        Gets basic stats from the Query server.

        :return: Dictionary of basic stats.
        :rtype: dict
        """

        # Getting challenge response:

        chall = self.get_challenge().chall

        # Requesting short stats:

        pack = self.raw_send(0, chall, "basic")

        # Formatting the packet:

        data = self._format(pack)

        return data

    def get_full_stats(self):

        """
        Gets full stats from the Query server.

        :return: Dictionary of full stats.
        :rtype: dict
        """

        # Getting challenge response:

        chall = self.get_challenge().chall

        # Requesting full stats:

        pack = self.raw_send(0, chall, "full")

        # Formatting the packet:

        data = self._format(pack)

        return data

    def _format(self, data):

        """
        Sends the incoming data to the formatter.

        :param data: Data to be formatted
        :type data: QUERYPacket
        :return: Formatted data
        """

        # Extracting data from packet:

        data = data.data

        if self.format == "replace" or self.format == 1:

            # Replace format codes with desired values:

            data = self.formatters.format(data, "QUERY_PROTOCOL")

        elif self.format in ['clean', 'remove'] or self.format == 2:

            # Remove format codes:

            data = self.formatters.clean(data, "QUERY_PROTOCOL")

        return data

    def __enter__(self):

        """
        In a context manager.

        :return: This instance.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        Exit the context manager, show any errors as they are important.

        :param exc_type: Error info.
        :param exc_val: Error info.
        :param exc_tb: Error info.
        :return: False.
        """

        # Stopping

        self.stop()

        return False


class PINGClient(BaseClient):

    """
    Ping client, allows for user to interact with the Minecraft server via the Server List Ping protocol.

    :param host: Hostname of the Minecraft server
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as 'None' to generate one based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :type format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    :param proto_num: Protocol number to use, can specify which version we are emulating.
                      Defaults to 0, which is the latest.
    :type proto_num: int
    """

    def __init__(self, host, port=25565, reqid=None, format_method=BaseClient.REPLACE, timeout=60, proto_num=0):

        self.proto = PINGProtocol(host, port, timeout)
        self.host = host  # Host of the Minecraft server
        self.port = int(port)  # Port of the Minecraft server
        self.formatters = FormatterCollection()  # Formatters method
        self.format = format_method  # Formatting method to use
        self.protonum = proto_num  # Protocol number we are using - 0 means we are using the latest

        self.reqid = self.gen_reqid() if reqid is None else int(reqid)

        # Adding the relevant formatters

        self.formatters.add(PINGFormatter, self.formatters.PING)

    def start(self):

        """
        Starts the connection to the Minecraft server. This is called automatically where appropriate,
        so you shouldn't have to worry about calling this.
        """

        if not self.is_connected():

            self.proto.start()

    def stop(self):

        """
        Stops the connection to the Minecraft server.
        This function should always be called when ceasing network communications,
        as not doing so could cause problems server-side.
        """

        if self.is_connected():

            self.proto.stop()

    def is_connected(self):

        """
        Determines if we are connected.

        :return: True if connected, False if otherwise.
        :rtype: bool
        """

        return self.proto.connected

    def raw_send(self, pingnum, packet_type, proto=None, host=None, port=0, noread=False):

        if proto is None:

            proto = self.proto

        """
        Creates a PingPacket and sends it to the Minecraft server

        :param pingnum: Pingnumber of the packet(For ping packets only)
        :type pingnum: int, None
        :param packet_type: Type of packet we are working with
        :type packet_type: str
        :param proto: Protocol number of the Minecraft server(For handshake only)
        :type proto: int
        :param host: Hostname of the Minecraft server(For handshake only)
        :type host: str
        :param port: Port of the Minecraft server(For handshake only)
        :type port: int
        :param noread:  Determining if we are expecting a response
        :type noread: bool
        :return: PINGPacket
        :rtype: PINGPacket
        """

        if not self.is_connected():

            # We are not connected, obviously the user wants to connect, so start it

            self.start()

        # Sending packet:

        self.proto.send(PINGPacket(pingnum, packet_type, proto=proto, host=host, port=port))

        pack = None

        if not noread:

            # Receiving packet:

            pack = self.proto.read()

        return pack

    def _send_handshake(self):

        """
        Sends a handshake packet to the server - Starts the conversation.
        """

        # Sending packet:

        self.raw_send(None, "handshake", proto=self.protonum, host=self.host, port=self.port, noread=True)

    def _send_ping(self):

        """
        Sends a ping packet to the server.
        We send this after we query stats, so the server doesn't have to wait.
        We also use this to calculate the latency, in nanoseconds.

        :return: PINGPacket, time.
        """

        # Getting start time here:

        timestart = time.perf_counter()

        # Sending packet:

        pack = self.raw_send(self.reqid, "ping")

        # Calculating time elapsed, and converting that to milliseconds

        total = (time.perf_counter() - timestart) * 1000

        return pack, total

    def ping(self):

        """
        Pings the Minecraft server and calculates the latency.

        :return: Time elapsed(in milliseconds).
        :rtype: float
        """

        # Sending handshake packet:

        self._send_handshake()

        # Sending request packet:

        self.raw_send(None, 'req')

        # Sending ping packet and getting time elapsed

        ping, time_elapsed = self._send_ping()

        return time_elapsed

    def get_stats(self):

        """
        Gets stats from the Minecraft server.

        :return: Dictionary containing stats.
        :rtype: dict
        """

        # Sending handshake packet:

        self._send_handshake()

        # Sending request packet:

        pack = self.raw_send(None, "req")

        # Sending ping packet - trying to be nice so server doesn't have to wait:

        ping, time_elapsed = self._send_ping()

        # Getting stop time, and adding it to the dictionary:

        pack.data["time"] = time_elapsed

        # Formatting the packet:

        data = self._format(pack)

        return data

    def _format(self, pack):

        """
        Sends the incoming data to the formatter.

        :param pack: Packet to be formatted
        :type pack: PINGPacket
        :return: Formatted data.
        """

        # Extracting the data from the packet:

        data = pack.data

        if self.format == "replace" or self.format == 1:

            # Replace format codes with desired values:

            data = self.formatters.format(data, "PING_PROTOCOL")

        elif self.format in ['clean', 'remove'] or self.format == 2:

            # Remove format codes:

            data = self.formatters.clean(data, "PING_PROTOCOL")

        return data

    def __enter__(self):

        """
        Enter the context manager.

        :return: This instance.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        Exit the context manager.

        :param exc_type: Error info.
        :param exc_val: Error info.
        :param exc_tb: Error info.
        :return: False.
        """

        # Stop the connection:

        self.stop()

        return False
