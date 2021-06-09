"""
Main Minecraft Connection Clients - Easy to use API for the underlying modules
Combines the following:
- Protocol Implementations
- Packet implementations
- Formatting tools
"""


import time

from typing import Union

from mctools.protocol import BaseProtocol, RCONProtocol, QUERYProtocol, PINGProtocol
from mctools.packet import RCONPacket, QUERYPacket, PINGPacket
from mctools.formattertools import BaseFormatter, FormatterCollection, DefaultFormatter, QUERYFormatter, PINGFormatter
from mctools.errors import RCONAuthenticationError, RCONMalformedPacketError


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

    def __init__(self) -> None:
        
        # Dummy init method

        self.proto: BaseProtocol
        self.formatters: BaseFormatter

    def gen_reqid(self):

        """
        Generates a request ID using system time.

        :return: System time as an integer
        """

        return int(time.time())

    def set_timeout(self, timeout):

        """
        Sets the timeout for the underlying socket object.

        :param timeout: Value in seconds to set the timeout to
        :type timeout: int
        """

        # Have the protocol object set the timeout:

        self.proto.set_timeout(timeout)

    def start(self):

        """
        Starts the client, and any protocol objects/formatters in use.
        (Good idea to put a call to Protocol.start() here).
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :raises:
            NotImplementedError: If function is called.
        """

        raise NotImplementedError("Override this method in child class!")

    def stop(self):

        """
        Stops the client, and any protocol objects/formatters in use.
        (Again, good idea to put a call to Protocol.stop() here).
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :raises:
            NotImplementedError: If function is called.
        """

        raise NotImplementedError("Override this method in child class!")

    def is_connected(self):

        """
        Determine if we are connected to the remote entity,
        whatever that may be.
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :return: True if connected, False if not.
        :raises:
            NotImplementedError: If function is called.
        """

        raise NotImplementedError("Override this method in child class!")

    def raw_send(self, *args):

        """
        For sending packets with user defined values, instead of the wrappers from client.
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :param args: Arguments specified, varies from client to client.
        :raises:
            NotImplementedError: If function is called.
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
        (Can be an IP address or domain name, anything your computer can resolve)
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as 'None' to generate an ID based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :param format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    """

    def __init__(self, host, port=25575, reqid=None, format_method=BaseClient.REPLACE, timeout=60):

        self.proto: RCONProtocol = RCONProtocol(host, port, timeout)  # RCONProtocol, used for communicating with RCON server
        self.formatters: FormatterCollection = FormatterCollection()  # Formatters instance, formats text from server
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

    def is_connected(self) -> bool:

        """
        Determines if we are connected.

        :return: True if connected, False if not.
        :rtype: bool
        """

        return self.proto.connected

    def is_authenticated(self) -> bool:

        """
        Determines if we are authenticated.

        :return: True if authenticated, False if not.
        :rtype: bool
        """

        return self.auth

    def raw_send(self, reqtype: int, payload: str, frag_check: bool=True, length_check: bool=True) -> RCONPacket:

        """
        Creates a RCON packet based off the following parameters and sends it.
        This function is used for all networking operations.

        We automatically check if a packet is fragmented(We check it's length).
        If this is the case, then we send a junk packet, and we keep reading packets until the server
        acknowledges the junk packet. This operation can take some time depending on network speed,
        so we offer the option to disable this feature, with the risk that their might be stability issues.

        We also check if the packet being sent is too big, and raise an exception of this is the case.
        This can be disabled by passing False to the 'length_check' parameter,
        although this is not recommended.

        .. warning:: Use this function at you own risk! You should really call the high level functions,
            as not doing so could mess up the state/connection of the client.

        :param reqtype: Request type
        :type reqtype: int
        :param payload: Payload to send
        :type payload: str
        :param frag_check: Determines if we should check and handle packet fragmentation.
        :type frag_check: bool

        .. warning:: Disabling fragmentation checks could lead to instability! Do so at your own risk!

        :param length_check: Determines if we should check for outgoing packet length
        :type length_check: bool

        .. warning:: Disabling legnth checks could lead to instability! Do so at your own risk!

        :return: RCONPacket containing response from server
        :rtype: RCONPacket
        :raises:
            RCONAuthenticationError: If the server refuses to server us and we are not authenticated.
            RCONMalformedPacketError: If the request ID's do not match of the packet is otherwise malformed.

        .. versionadded:: 1.1.0

        The 'frag_check' parameter

        .. versionadded:: 1.1.2

        The 'length_check' parameter
        """

        if not self.is_connected():

            # Connection not started, user obviously wants to connect, so start it

            self.start()

        # Sending packet:

        self.proto.send(RCONPacket(self.reqid, reqtype, payload), length_check=length_check)

        # Receiving response packet:

        pack = self.proto.read()

        # Check if our stuff is valid:

        if pack.reqid != self.reqid and self.is_authenticated() and reqtype != self.proto.LOGIN:

            # Client/server ID's do not match!

            raise RCONMalformedPacketError("Client and server request ID's do not match!")

        elif pack.reqid != self.reqid and reqtype != self.proto.LOGIN:

            # Authentication issue!

            raise RCONAuthenticationError("Client and server request ID's do not match! We are not authenticated!")

        # Check if the packet is fragmented(And if we even care about fragmentation):

        if frag_check and pack.length >= self.proto.MAX_SIZE:

            # Send a junk packet:

            self.proto.send(RCONPacket(self.reqid, 0, ''))

            # Read until we get a valid response:

            while True:

                # Get a packet from the server:

                temp_pack = self.proto.read()

                if temp_pack.reqtype == self.proto.RESPONSE and temp_pack.payload == 'Unknown request 0':

                    # Break, we are done here

                    break

                if temp_pack.reqid != self.reqid:

                    # Client/server ID's do not match!

                    raise RCONMalformedPacketError("Client and server request ID's do not match!")

                # Add the packet content to the master pack:

                pack.payload = pack.payload + temp_pack.payload

        # Return our junk:

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
        Convenience function, does the same thing that 'login' does, authenticates you with the RCON server.

        :param password: Password to authenticate with
        :type password: str
        :return: True if successful, False if failure
        :rtype: bool
        """

        return self.login(password)

    def command(self, com: str, check_auth: bool=True, format_method: int=None, return_packet: bool=False, frag_check: bool=True, length_check: bool=True) -> Union[RCONPacket, str]:

        """
        Sends a command to the RCON server and gets a response.

        .. note::

            Be sure to authenticate before sending commands to the server!
            Most servers will simply refuse to talk to you if you do not authenticate.

        :param com: Command to send
        :type com: str
        :param check_auth: Value determining if we should check authentication status before sending our command
        :type check_auth: bool
        :param format_method: Determines the format method we should use. If 'None', then we use the global value
            You should use the Client constants to define this.
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :param frag_check: Determines if we should check and handle packet fragmentation

            .. warning::

                Disabling fragmentation checks could lead to instability!
                Do so at your own risk!

        :type frag_check: bool
        :param length_check: Determines if we should check and handel outgoing packet length

            .. warning::

                Disabling length checks could lead to instability!
                Do so at your own risk!
    
        :type legnth_check: bool
        :return: Response text from server
        :rtype: str, RCONPacket
        :raises:
            RCONAuthenticationError: If we are not authenticated to the RCON server,
            and authentication checking is enabled. We also raise this if the server refuses to serve us,
            regardless of weather auth checking is enabled.
            RCONMalformedPacketError: If the packet we received is broken or is not the correct packet.
            RCONLengthError: If the outgoing packet is larger than 1460 bytes

        .. versionadded:: 1.1.0

        The 'check_auth', 'format_method', 'return_packet', and 'frag_check' parameters

        .. versionadded:: 1.1.2

        The 'length_check' parameter
        """

        # Checking authentication status:

        if check_auth and not self.is_authenticated():

            # Not authenticated, let the user know this:

            raise RCONAuthenticationError("Not authenticated to the RCON server!")

        # Sending command packet:

        pack = self.raw_send(self.proto.COMMAND, com, frag_check=frag_check)

        # Get the formatted content:

        pack = self._format(pack, com, format_method=format_method)

        if return_packet:

            # Return the entire packet:

            return pack

        # Return just the payload

        return pack.payload

    def _format(self, pack, com, format_method=None):

        """
        Sends incoming data to the formatter.

        :param pack: Packet to format
        :type pack: RCONPacket
        :param com: Command issued
        :type com: str
        :param format_method: Determines the format method we should use. If 'None', then we use the global value.
        You should use the Client constants to define this.
        :type format_method: int
        :return: Formatted content
        :rtype: RCONPacket
        """

        if format_method is None:

            # Use the global format method

            format_method = self.format

        # Formatting text:

        if format_method == 'replace' or format_method == 1:

            # Replacing format chars

            pack.payload = self.formatters.format(pack.payload, com)

        elif format_method == 'clean' or format_method == 2:

            # Removing format chars

            pack.payload = self.formatters.clean(pack.payload, com)

        return pack

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

    def __init__(self, host: str, port: int=25565, reqid: int=None, format_method: int=BaseClient.REPLACE, timeout: int=60):

        self.proto: QUERYProtocol = QUERYProtocol(host, port, timeout)  # Query protocol instance
        self.formatters: FormatterCollection = FormatterCollection()  # Formatters instance
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

    def is_connected(self) -> bool:

        """
        Determines if we are connected.
        (UPD doesn't really work that way, so we simply return if we have been started).

        :return: True if started, False for otherwise.
        :rtype: bool
        """

        return self.proto.started

    def raw_send(self, reqtype: int, chall: Union[str, None], packet_type: str) -> QUERYPacket:

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

    def get_challenge(self) -> QUERYPacket:

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

    def get_basic_stats(self, format_method: int=None, return_packet: bool=False) -> Union[dict, QUERYPacket]:

        """
        Gets basic stats from the Query server.

        :param format_method: Determines the format method we should use. If 'None', then we use the global value.
            You should use the Client constants to define this
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :return: Dictionary of basic stats, or QUERYPacket, depending on 'return_packet'.
        :rtype: dict, QUERYPacket

        .. versionadded:: 1.1.0

        The 'format_method' and 'return_packet' parameters
        """

        # Getting challenge response:

        chall = self.get_challenge().chall

        # Requesting short stats:

        pack = self.raw_send(0, chall, "basic")

        # Formatting the packet:

        pack.data = self._format(pack, format_method=format_method)

        if return_packet:

            # Return just the packet:

            return pack

        # Return the payload

        return pack.data

    def get_full_stats(self, format_method: int=None, return_packet: bool=False) -> Union[dict, QUERYPacket]:

        """
        Gets full stats from the Query server.

        :param format_method: Determines the format method we should use. If 'None', then we use the global value.
            You should use the Client constants to define this.
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :return: Dictionary of full stats, or QUERYPacket, depending on 'return_packet'.
        :rtype: dict

        .. versionadded:: 1.1.0

        The 'format_method' and 'return_packet' parameters
        """

        # Getting challenge response:

        chall = self.get_challenge().chall

        # Requesting full stats:

        pack = self.raw_send(0, chall, "full")

        # Formatting the packet:

        pack.data = self._format(pack, format_method=format_method)

        if return_packet:

            # Return the packet:

            return pack

        # Return the payload

        return pack.data

    def _format(self, data, format_method=None):

        """
        Sends the incoming data to the formatter.

        :param data: Data to be formatted
        :type data: QUERYPacket
        :param format_method: Format method to use. If 'None', then we use the global value.
        :type format_method: int
        :return: Formatted data
        """

        # Check what format type we are using:

        format_type = format_method

        if format_method is None:

            # Use the global format method

            format_type = self.format

        # Extracting data from packet:

        data = data.data

        if format_type == "replace" or format_type == 1:

            # Replace format codes with desired values:

            data = self.formatters.format(data, "QUERY_PROTOCOL")

        elif format_type in ['clean', 'remove'] or format_type == 2:

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

    def __init__(self, host: str, port: int=25565, reqid: int=None, format_method: int=BaseClient.REPLACE, timeout: int=60, proto_num: int=0):

        self.proto: PINGProtocol = PINGProtocol(host, port, timeout)
        self.host = host  # Host of the Minecraft server
        self.port = int(port)  # Port of the Minecraft server
        self.formatters: FormatterCollection = FormatterCollection()  # Formatters method
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

    def is_connected(self) -> bool:

        """
        Determines if we are connected.

        :return: True if connected, False if otherwise.
        :rtype: bool
        """

        return self.proto.connected

    def raw_send(self, pingnum: Union[int, None], packet_type: str, proto: int=None, host: str=None, port: int=0, noread: bool=False) -> PINGPacket:

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
        :param noread: Determining if we are expecting a response
        :type noread: bool
        :return: PINGPacket if noread if False, otherwise None
        :rtype: PINGPacket, None
        """

        if proto is None:

            proto = self.protonum

        if not self.is_connected():

            # We are not connected, obviously the user wants to connect, so start it

            self.start()

        # Sending packet:

        self.proto.send(PINGPacket(pingnum, packet_type, proto=proto, host=host, port=port))

        pack = PINGPacket(0, 0, None, 0)

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

    def ping(self) -> float:

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

    def get_stats(self, format_method: int=None, return_packet: bool=False) -> Union[dict, PINGPacket]:

        """
        Gets stats from the Minecraft server.

        :param format_method: Determines the format method we should use. If 'None', then we use the global value.
            You should use the Client constants to define this.
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :return: Dictionary containing stats, or PINGPacket depending on 'return_packet'
        :rtype: dict, PINGPacket

        .. versionadded:: 1.1.0

        The 'format_method' and 'return_packet' parameters
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

        pack.data = self._format(pack, format_method=format_method)

        if return_packet:

            # Return the packet:

            return pack

        # Return just the payload

        return pack.data

    def _format(self, pack, format_method=None):

        """
        Sends the incoming data to the formatter.

        :param pack: Packet to be formatted
        :type pack: PINGPacket
        :param format_method: Determines the format method we should use. If 'None', then we use the global value.
        You should use the Client constants to define this.
        :type format_method: int
        :return: Formatted data.
        """

        # Figure out what format method we are using:

        format_type = format_method

        if format_method is None:

            # Use the global value:

            format_type = self.format

        # Extracting the data from the packet:

        data = pack.data

        if format_type == "replace" or format_type == 1:

            # Replace format codes with desired values:

            data = self.formatters.format(data, "PING_PROTOCOL")

        elif format_type in ['clean', 'remove'] or format_type == 2:

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
