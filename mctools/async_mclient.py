"""
Main Minecraft Connection Async Clients - Easy to use API for the underlying modules
Combines the following:
- Async Protocol Implementations
- Packet implementations
- Formatting tools
"""

from __future__ import annotations

import time
import asyncio

from typing import Union, Any, Tuple

from mctools.async_protocol import AsyncRCONProtocol, AsyncQUERYProtocol, AsyncPINGProtocol, DEFAULT_TIMEOUT
from mctools.packet import RCONPacket, QUERYPacket, PINGPacket
from mctools.formattertools import FormatterCollection, DefaultFormatter, QUERYFormatter, PINGFormatter
from mctools.errors import RCONAuthenticationError, RCONMalformedPacketError


class AsyncBaseClient:
    """
    Parent class for Async Minecraft Client implementations.
    This class has the following formatting constants, which every client inherits:

      - AsyncBaseClient.RAW - Tells the client to not format any content.
      - AsyncBaseClient.REPLACE - Tells the client to replace format characters.
      - AsyncBaseClient.REMOVE - Tells the client to remove format characters.
      - AsyncBaseClient.DEFAULT - Chooses the global default

    You can use these constants in the 'format_method' parameter in each client.
    """

    # Formatting codes

    RAW = 0
    REPLACE = 1
    REMOVE = 2
    DEFAULT = -1

    def __init__(self) -> None:

        self.proto: Any  # Protocol instance in use by client
        self.formatters: FormatterCollection = FormatterCollection()  # Formatter collection to utilize

    def gen_reqid(self) -> int:
        """
        Generates a request ID using system time.

        :return: System time as an integer
        :rtype: int
        """

        return int(time.time())

    def set_timeout(self, timeout: int):
        """
        Sets the timeout for the underlying protocol.

        :param timeout: Value in seconds to set the timeout to
        :type timeout: int
        """

        # Have the protocol object set the timeout:

        self.proto.set_timeout(timeout)

    async def start(self):
        """
        Starts the client, and any protocol objects/formatters in use.
        (Good idea to put a call to Protocol.start() here).
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :raises:
            NotImplementedError: If function is called.
        """

        raise NotImplementedError("Override this method in child class!")

    async def stop(self):
        """
        Stops the client, and any protocol objects/formatters in use.
        (Again, good idea to put a call to Protocol.stop() here).
        This raises a 'NotImplementedError' exception,
        as this function should be overridden in the child class.

        :raises:
            NotImplementedError: If function is called.
        """

        raise NotImplementedError("Override this method in child class!")

    def is_connected(self) -> bool:
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

    def get_formatter(self) -> FormatterCollection:
        """
        Returns the formatter used by this instance,
        Allows the user to change formatter operations.

        :return: FormatterCollection used by the client.
        :rtype: FormatterCollection
        """

        return self.formatters

    async def __aenter__(self) -> Any:
        """
        All clients MUST have async context manager support!

        We simply return ourselves once in a context manager.
        """

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        All clients MUST have async context manager support!
        (Recommend showing exceptions, AKA returning False)

        :param exc_type: Exception info
        :param exc_val: Exception info
        :param exc_tb: Exception inf
        :return: False(Can be something else)
        """

        # Stopping connection:

        await self.stop()

        return False


class AsyncRCONClient(AsyncBaseClient):
    """
    Async RCON client, allows for user to interact with the Minecraft server via the RCON protocol.

    :param host: Hostname of the Minecraft server
        (Can be an IP address or domain name, anything your computer can resolve)
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as '-1' to generate an ID based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :param format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    """

    def __init__(self, host: str, port: int = 25575, reqid: int = -1, format_method: int = AsyncBaseClient.REPLACE, timeout: int = DEFAULT_TIMEOUT):
        super().__init__()

        # AsyncRCONProtocol, used for communicating asynchronously with RCON server
        self.proto: AsyncRCONProtocol = AsyncRCONProtocol(host, port, timeout)
        self.auth: bool = False  # Value determining if we are authenticated
        self.format: int = format_method  # Value determining how to format output

        self.reqid: int = self.gen_reqid() if reqid == -1 else int(reqid)  # Generating a request ID

        # Adding the relevant formatters:

        self.formatters.add(DefaultFormatter(), '', ignore=[
                            self.formatters.PING, self.formatters.QUERY])
        self._lock = asyncio.Lock()

    async def start(self):
        """
        Starts the connection to the RCON server.
        This is called automatically where appropriate,
        so you shouldn't have to worry about calling this.
        """

        # Start the protocol instance:

        if not self.is_connected():

            await self.proto.start()

    async def stop(self):
        """
        Stops the connection to the RCON server.
        This function should always be called when ceasing network communications,
        as not doing so could cause problems server-side.
        """

        # Stop the protocol instance

        if self.is_connected():

            self.auth = False

            await self.proto.stop()

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

    async def raw_send(self, reqtype: int, payload: str, frag_check: bool = True, length_check: bool = True) -> RCONPacket:
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

        .. warning:: Disabling length checks could lead to instability! Do so at your own risk!

        :return: RCONPacket containing response from server
        :rtype: RCONPacket
        :raises:
            RCONAuthenticationError: If the server refuses to server us and we are not authenticated.
            RCONMalformedPacketError: If the request ID's do not match of the packet is otherwise malformed.
        """
        async with self._lock:
            if not self.is_connected():

                # Connection not started, user obviously wants to connect, so start it

                await self.start()

            # Sending packet:
            await self.proto.send(RCONPacket(self.reqid, reqtype, payload),
                            length_check=length_check)

            # Receiving response packet:

            pack = await self.proto.read()

            # Check if our stuff is valid:

            if pack.reqid != self.reqid and self.is_authenticated() and reqtype != RCONPacket.LOGIN:

                # Client/server ID's do not match!

                raise RCONMalformedPacketError(
                    "Client and server request ID's do not match!")

            elif pack.reqid != self.reqid and reqtype != RCONPacket.LOGIN:

                # Authentication issue!

                raise RCONAuthenticationError(
                    "Client and server request ID's do not match! We are not authenticated!")

            # Check if the packet is fragmented(And if we even care about fragmentation):

            if frag_check and pack.length >= RCONPacket.MAX_SIZE:

                # Send a junk packet:
                await self.proto.send(RCONPacket(self.reqid, 0, ''))

                # Read until we get a valid response:

                while True:

                    # Get a packet from the server:

                    temp_pack = await self.proto.read()

                    if temp_pack.reqtype == RCONPacket.RESPONSE and temp_pack.payload == 'Unknown request 0':

                        # Break, we are done here

                        break

                    if temp_pack.reqid != self.reqid:

                        # Client/server ID's do not match!

                        raise RCONMalformedPacketError(
                            "Client and server request ID's do not match!")

                    # Add the packet content to the master pack:

                    pack.payload = pack.payload + temp_pack.payload

            # Return our junk:

            return pack

    async def login(self, password: str) -> bool:
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

        pack = await self.raw_send(RCONPacket.LOGIN, password)

        # Checking login packet

        if pack.reqid != self.reqid:

            # Login failed, request IDs do not match

            return False

        # Request ID matches!

        self.auth = True

        return True

    async def authenticate(self, password: str) -> bool:
        """
        Convenience function, does the same thing that 'login' does, authenticates you with the RCON server.

        :param password: Password to authenticate with
        :type password: str
        :return: True if successful, False if failure
        :rtype: bool
        """

        return await self.login(password)

    async def command(self, com: str, check_auth: bool = True, format_method: int = -1, return_packet: bool = False, frag_check: bool = True, length_check: bool = True) -> Union[RCONPacket, str]:
        """
        Sends a command to the RCON server and gets a response.

        .. note::

            Be sure to authenticate before sending commands to the server!
            Most servers will simply refuse to talk to you if you do not authenticate.

        :param com: Command to send
        :type com: str
        :param check_auth: Value determining if we should check authentication status before sending our command
        :type check_auth: bool
        :param format_method: Determines the format method we should use. If '-1', then we use the global value
            You should use the Client constants to define this.
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :param frag_check: Determines if we should check and handle packet fragmentation

            .. warning::

                Disabling fragmentation checks could lead to instability!
                Do so at your own risk!

        :type frag_check: bool
        :param length_check: Determines if we should check and handle outgoing packet length

            .. warning::

                Disabling length checks could lead to instability!
                Do so at your own risk!

        :type length_check: bool
        :return: Response text from server
        :rtype: str, RCONPacket
        :raises:
            RCONAuthenticationError: If we are not authenticated to the RCON server,
            and authentication checking is enabled. We also raise this if the server refuses to serve us,
            regardless of weather auth checking is enabled.
            RCONMalformedPacketError: If the packet we received is broken or is not the correct packet.
            RCONLengthError: If the outgoing packet is larger than 1460 bytes
        """

        # Checking authentication status:

        if check_auth and not self.is_authenticated():

            # Not authenticated, let the user know this:

            raise RCONAuthenticationError(
                "Not authenticated to the RCON server!")

        # Sending command packet:

        pack = await self.raw_send(RCONPacket.COMMAND, com,
                             frag_check=frag_check, length_check=length_check)

        # Get the formatted content:

        pack = self._format(pack, com, format_method=format_method)

        if return_packet:

            # Return the entire packet:

            return pack

        # Return just the payload

        return pack.payload

    def _format(self, pack: RCONPacket, com: str, format_method: int = -1) -> RCONPacket:
        """
        Sends incoming data to the formatter.

        :param pack: Packet to format
        :type pack: RCONPacket
        :param com: Command issued
        :type com: str
        :param format_method: Determines the format method we should use. If '-1', then we use the global value.
        You should use the Client constants to define this.
        :type format_method: int
        :return: Formatted content
        :rtype: RCONPacket
        """

        if format_method == -1:

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

    async def __aenter__(self) -> AsyncRCONClient:
        """
        In an async context manager.

        :return: This instance
        """

        return self


class AsyncQUERYClient(AsyncBaseClient):
    """
    Async query client, allows for user to interact with the Minecraft server via the Query protocol.

    :param host: Hostname of the Minecraft server
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as '-1' to generate one based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :type format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    """

    def __init__(self, host: str, port: int = 25565, reqid: int = -1, format_method: int = AsyncBaseClient.REPLACE, timeout: int = DEFAULT_TIMEOUT):
        super().__init__()

        self.proto: AsyncQUERYProtocol = AsyncQUERYProtocol(
            host, port, timeout)  # Query protocol instance
        self.format: int = format_method  # Format type to use

        self.reqid: int = self.gen_reqid() if reqid == -1 else int(reqid)

        # Adding the relevant formatters

        self.formatters.add(QUERYFormatter(), self.formatters.QUERY)

    async def start(self):
        """
        Starts the Query object. This is called automatically where appropriate,
        so you shouldn't have to worry about calling this.
        """

        if not self.is_connected():

            await self.proto.start()

    async def stop(self):
        """
        Stops the connection to the Query server.
        In this case, it is not strictly necessary to stop the connection,
        as AsyncQueryClient uses the UDP protocol. It is still recommended to stop the instance any way,
        so you can be explicit in your code as to when you are going to stop communicating over the network.
        """

        if self.is_connected():

            await self.proto.stop()

    def is_connected(self) -> bool:
        """
        Determines if we are connected.
        (UPD doesn't really work that way, so we simply return if we have been started).

        :return: True if started, False for otherwise.
        :rtype: bool
        """

        return self.proto.connected

    async def raw_send(self, packet_type: int, chall: int, reqtype: int = -1) -> QUERYPacket:
        """
        Creates a packet from the given arguments and sends it.
        Returns a response.

        :param reqtype: Type of packet to send
        :type reqtype: int
        :param chall: Challenge Token, ignored if not relevant
        :type chall: int
        :param reqtype: Request type to utilize
        :type reqtype: int
        :return: QUERYPacket containing response
        :rtype: QUERYPacket
        """

        # Check if we are connected:

        if not self.is_connected():

            # Start ourselves:

            await self.start()

        # Sending packet:

        self.proto.send(QUERYPacket(packet_type, self.reqid, chall, reqtype=reqtype))

        # Receiving response packet:

        pack = await self.proto.read()

        return pack

    async def get_challenge(self) -> QUERYPacket:
        """
        Gets the challenge token from the Query server.
        It is necessary to get a token before every operation,
        as the Query tokens change every 30 seconds.

        :return: QueryPacket containing challenge token.
        :rtype: QUERYPacket
        """

        # Sending initial packet:

        pack = await self.raw_send(QUERYPacket.HANDSHAKE_REQUEST, -1)

        # Returning pack:

        return pack

    async def get_basic_stats(self, format_method: int = -1, return_packet: bool = False) -> Union[dict, QUERYPacket]:
        """
        Gets basic stats from the Query server.

        :param format_method: Determines the format method we should use. If '-1', then we use the global value.
            You should use the Client constants to define this
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :return: Dictionary of basic stats, or QUERYPacket, depending on 'return_packet'.
        :rtype: dict, QUERYPacket
        """

        # Getting challenge response:

        chall = (await self.get_challenge()).chall

        # Requesting short stats:

        pack = await self.raw_send(QUERYPacket.BASIC_REQUEST, chall)

        # Formatting the packet:

        pack.data = self._format(pack, format_method=format_method)

        if return_packet:

            # Return just the packet:

            return pack

        # Return the payload

        return pack.data

    async def get_full_stats(self, format_method: int = -1, return_packet: bool = False) -> Union[dict, QUERYPacket]:
        """
        Gets full stats from the Query server.

        :param format_method: Determines the format method we should use. If '-1', then we use the global value.
            You should use the Client constants to define this.
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :return: Dictionary of full stats, or QUERYPacket, depending on 'return_packet'.
        :rtype: dict
        """

        # Getting challenge response:

        chall = await self.get_challenge().chall

        # Requesting full stats:

        pack = await self.raw_send(QUERYPacket.FULL_REQUEST, chall)

        # Formatting the packet:

        pack.data = self._format(pack, format_method=format_method)

        if return_packet:

            # Return the packet:

            return pack

        # Return the payload

        return pack.data

    def _format(self, data, format_method: int = -1):
        """
        Sends the incoming data to the formatter.

        :param data: Data to be formatted
        :type data: QUERYPacket
        :param format_method: Format method to use. If '-1', then we use the global value.
        :type format_method: int
        :return: Formatted data
        """

        # Check what format type we are using:

        format_type = format_method

        if format_method == -1:

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

    async def __aenter__(self) -> AsyncQUERYClient:
        """
        In a context manager.

        :return: This instance.
        """

        return self


class AsyncPINGClient(AsyncBaseClient):
    """
    Async ping client, allows for user to interact with the Minecraft server via the Server List Ping protocol.

    :param host: Hostname of the Minecraft server
    :type host: str
    :param port: Port of the Minecraft server
    :type port: int
    :param reqid: Request ID to use, leave as '-1' to generate one based on system time
    :type reqid: int
    :param format_method: Format method to use. You should specify this using the Client constants
    :type format_method: int
    :param timeout: Sets the timeout value for socket operations
    :type timeout: int
    :param proto_num: Protocol number to use, can specify which version we are emulating.
                      Defaults to 0, which is the latest.
    :type proto_num: int
    """

    def __init__(self, host: str, port: int = 25565, reqid: int = -1, format_method: int = AsyncBaseClient.REPLACE, timeout: int = DEFAULT_TIMEOUT, proto_num: int = 0):
        super().__init__()

        self.proto: AsyncPINGProtocol = AsyncPINGProtocol(host, port, timeout)
        self.host: str = host  # Host of the Minecraft server
        self.port = int(port)  # Port of the Minecraft server
        self.format: int = format_method  # Formatting method to use
        # Protocol number we are using - 0 means we are using the latest
        self.protonum: int = proto_num

        self.reqid = self.gen_reqid() if reqid == -1 else int(reqid)

        # Adding the relevant formatters

        self.formatters.add(PINGFormatter(), self.formatters.PING)

    async def start(self):
        """
        Starts the connection to the Minecraft server. This is called automatically where appropriate,
        so you shouldn't have to worry about calling this.
        """

        if not self.is_connected():

            await self.proto.start()

    async def stop(self):
        """
        Stops the connection to the Minecraft server.
        This function should always be called when ceasing network communications,
        as not doing so could cause problems server-side.
        """

        if self.is_connected():

            await self.proto.stop()

    def is_connected(self) -> bool:
        """
        Determines if we are connected.

        :return: True if connected, False if otherwise.
        :rtype: bool
        """

        return self.proto.connected

    async def raw_send(self, pingnum: int, packet_type: int, proto: int = -1, host: str = '', port: int = 0, noread: bool = False) -> PINGPacket:
        """
        Creates a PingPacket and sends it to the Minecraft server

        :param pingnum: Pingnumber of the packet(For ping packets only)
        :type pingnum: int
        :param packet_type: Type of packet we are working with
        :type packet_type: int
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

        if proto == -1:

            proto = self.protonum

        if not self.is_connected():

            # We are not connected, obviously the user wants to connect, so start it

            await self.start()

        # Sending packet:

        await self.proto.send(PINGPacket(pingnum, packet_type,
                        proto=proto, host=host, port=port))

        pack = PINGPacket(0, 0, None, 0)

        if not noread:

            # Receiving packet:

            pack = await self.proto.read()

        return pack

    async def ping(self) -> float:
        """
        Pings the Minecraft server and calculates the latency.

        :return: Time elapsed(in milliseconds).
        :rtype: float
        """

        # Sending handshake packet:

        await self._send_handshake()

        # Sending ping packet and getting time elapsed

        ping, time_elapsed = await self._send_ping()

        # Stop ourselves:

        await self.stop()

        return time_elapsed

    async def get_stats(self, format_method: int = -1, return_packet: bool = False) -> Union[dict, PINGPacket]:
        """
        Gets stats from the Minecraft server, and preforms a ping operation.

        :param format_method: Determines the format method we should use. If '-1', then we use the global value.
            You should use the Client constants to define this.
        :type format_method: int
        :param return_packet: Determines if we should return the entire packet. If not, return the payload
        :type return_packet: bool
        :return: Dictionary containing stats, or PINGPacket depending on 'return_packet'
        :rtype: dict, PINGPacket
        """

        # Sending handshake packet:

        await self._send_handshake()

        # Sending request packet:

        pack = await self.raw_send(-1, PINGPacket.STATUS_REQUEST)

        # Sending ping packet - trying to be nice so server doesn't have to wait:

        ping, time_elapsed = await self._send_ping()

        # Getting stop time, and adding it to the dictionary:

        pack.data["time"] = time_elapsed

        # Formatting the packet:

        pack.data = self._format(pack, format_method=format_method)

        if return_packet:

            # Return the packet:

            return pack

        # Stop ourselves:

        await self.stop()

        # Return just the payload

        return pack.data

    async def _send_handshake(self):
        """
        Sends a handshake packet to the server - Starts the conversation.
        """

        # Sending packet:

        await self.raw_send(-1, PINGPacket.HANDSHAKE, proto=self.protonum,
                      host=self.host, port=self.port, noread=True)

    async def _send_ping(self) -> Tuple[PINGPacket, float]:
        """
        Sends a ping packet to the server.
        We send this after we query stats, so the server doesn't have to wait.
        We also use this to calculate the latency, in milliseconds.

        :return: PINGPacket, time.
        :rtype: Tuple[PINGPacket, float]
        """

        # Getting start time here:

        timestart = time.perf_counter()

        # Sending packet:

        pack = await self.raw_send(self.reqid, PINGPacket.PING_REQUEST)

        # Calculating time elapsed, and converting that to milliseconds

        total = (time.perf_counter() - timestart) * 1000

        return pack, total

    def _format(self, pack: PINGPacket, format_method: int = -1) -> dict:
        """
        Sends the incoming data to the formatter.

        :param pack: Packet to be formatted
        :type pack: PINGPacket
        :param format_method: Determines the format method we should use. If '-1', then we use the global value.
        You should use the Client constants to define this.
        :type format_method: int
        :return: Formatted data.
        """

        # Figure out what format method we are using:

        format_type = format_method

        if format_method == -1:

            # Use the global value:

            format_type = self.format

        # Extracting the data from the packet:

        data = pack.data

        if format_type == "replace" or format_type == AsyncBaseClient.REPLACE:

            # Replace format codes with desired values:

            data = self.formatters.format(data, "PING_PROTOCOL")

        elif format_type in ['clean', 'remove', AsyncBaseClient.REMOVE]:

            # Remove format codes:

            data = self.formatters.clean(data, "PING_PROTOCOL")

        return data

    async def __aenter__(self) -> AsyncPINGClient:
        """
        Enter the context manager.

        :return: This instance.
        :rtype: PINGClient
        """

        return self
