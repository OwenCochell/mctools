
"""
Exception objects for mctools.
"""


class MCToolsError(Exception):

    """
    Base class for mctools exceptions.
    """

    pass


class ProtocolError(MCToolsError):

    """
    Base class for protocol errors.

    A protocol error is raised when an issue arises with the python socket object.
    These exceptions will be raised for ALL clients, 
    as they all use the same backend.
    """


class ProtoConnectionClosed(ProtocolError):

    """
    Exception raised when the connection is closed by the socket we are connected to.

    This occurs when we receive empty bytes from 'recv()',
    as this means that the remote socket is done writing,
    meaning that our connection is closed.
    """

    def __init__(self, message) -> None:
        
        self.message = message  # Explanation of the error


# --== RCON Errors: ==--


class RCONError(MCToolsError):

    """
    Base class for RCON errors.
    """

    pass


class RCONAuthenticationError(RCONError):

    """
    Exception raised when user is not authenticated to the RCON server.
    This is raised when a user tries to send a RCON command,
    and the server refuses to communicate.

    :param message: Explanation of the error
    :type message: str
    :param server_id: ID given to us by the server
    :type server_id:
    """

    def __init__(self, message):

        self.message = message  # Explanation of the error


class RCONMalformedPacketError(RCONError):

    """
    Exception raised if the packet we received is malformed/broken,
    or not what we were expecting.

    :param message: Explanation of the error
    :type message: str
    """

    def __init__(self, message):

        self.message = message  # Explanation of the error


class RCONCommunicationError(RCONError):

    """
    Exception raised if the client has trouble communicating with the RCON server.
    For example, if we don't receive any information when we want a packet.

    :param message: Explanation of the error
    :type message: str
    """

    def __init__(self, message):

        self.message = message  # Explanation of the error


class RCONLengthError(RCONError):

    """
    Exception raised if the client attempts to send a packet that is too big, greater than length 1460.
    """

    def __init__(self, message, length):

        self.message = message  # Explanation of error
        self.length = length  # Length of data


# --== PING Errors: ==--


class PINGError(MCToolsError):

    """
    Base class for PING errors
    """


class PINGMalformedPacketError(PINGError):

    """
    Exception raised if the ping packet received is malformed/broken,
    or not what we were expecting.
    """

    def __init__(self, message) -> None:
        
        self.message = message
