import argparse
import sys
from mctools.mclient import RCONClient, QUERYClient, PINGClient
from mctools.formattertools import FormatterCollection, DefaultFormatter, QUERYFormatter, PINGFormatter
import json

"""
A command line interface for interacting/querying Minecraft servers
"""

RCON_PORT = 25575
QUERY_PORT = 25565
MINECRAFT_PORT = 25565

SEP = '§9+========================================================================+'


class _HelpAction(argparse._HelpAction):

    """
    Custom HelpAction, so we can display all subparser help output
    """

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        # retrieve subparsers from parser

        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]

        # there will probably only be one subparser_action,
        # but better save than sorry

        for subparsers_action in subparsers_actions:

            # get all subparsers and print help

            for choice, subparser in subparsers_action.choices.items():

                print("Option: '{}'".format(choice))
                print(subparser.format_help())

        print("For more information, please check the GitHub page: https://github.com/Owen-Cochell/mctools")

        parser.exit()


class Output:

    """
    Class for outputting values to terminal, as well as writing output to files, if necessary
    We use the mclient formattertools to handle the formatting for us,
    As the user probably doesn't want a bunch of ASCII values in their output file.
    """

    def __init__(self, args):

        self.quiet = args.quiet  # Boolean determining if we are in quite mode
        self.color = args.no_color  # Boolean determining if we can use color in output
        self.show_chars = args.raw  # Boolean determining if we display format chars
        self.output_path = args.output  # File path to write, None if not writing
        self.output_chars = args.output_raw  # Boolean determining if we should output format chars into file
        self.output_replace = args.output_color  # Boolean determining if we should replace chars with ASCII values
        self.formatters = FormatterCollection()  # FormatterCollection method, used for formatting text

        # Adding base formater:

        self.formatters.add(DefaultFormatter, '', ignore=[self.formatters.QUERY, self.formatters.PING])

        try:

            self.output_favicon = args.show_favicon  # Boolean determining if we should output the favicon

        except Exception:

            self.output_favicon = False

    def output(self, text, command='', relevant=False):

        """
        Outputs text with whatever formatting chars we need,
        Writes text to file if necessary.

        :param text: Text to output
        :param command: Command issued when text was generated
        :param relevant: Value determining if we are working with relevant text(Response from server)
        :return:
        """

        # Formatting text for terminal output:

        if not self.quiet:

            if relevant and type(text) != str:

                self.recursive_print(self.format_print(text, command, relevant))

            else:

                print(self.format_print(text, command, relevant))

        # Formatting text for file output

        if relevant and self.output_path is not None:

            file = open(self.output_path, 'a')

            if type(text) == dict:

                file.write(json.dumps(self.format_file(text, command)))

            else:

                file.write(self.format_file(text, command))

            file.close()

    def format_print(self, text, command, relevant):

        """
        Formats text to be printed to the terminal.

        :param text: Text to be formatted.
        :param command: Command issued when text was generated.
        :param relevant: If text is relevant(Response from server).
        :return: Formatted text.
        """

        if self.quiet:

            # We are in quiet mode, should not print anything!

            return ''

        if not self.output_favicon and 'favicon' in text and relevant and type(text) == dict:

            # Removing favicon entry:

            del text['favicon']

        if not relevant and self.color:

            # Color is enabled, display

            return self.formatters.format(text, command)

        elif not relevant:

            return self.formatters.clean(text, command)

        # Working with relevant text here:

        if self.show_chars:

            # Show formatting chars:

            return text

        if not self.color:

            # No color for relevant text:

            return self.formatters.clean(text, command)

        return self.formatters.format(text, command)

    def format_file(self, text, command):

        """
        Formats text for outputting into file.

        :param text: Text to output
        :param command: Command issued
        :return:
        """

        if self.output_chars:

            # Show chars in output file

            return text

        if self.output_replace:

            # Replace chars with ASCII values

            return self.formatters.format(text, command)

        # Just remove output chars

        return self.formatters.clean(text, command)

    def recursive_print(self, data, depth=0):

        """
        Recursively traverses data presented.
        Formats the data so it is a certain width,
        and prints each value on a new line.

        :param data: Data to be traversed.
        :param depth: Depth we are currently at.
        :return:
        """

        if type(data) in [dict, list]:

            if len(data) == 0:

                print("{}Empty Value".format(' '*3*depth))

                return

            for k, v in (data.items() if type(data) == dict else enumerate(data)):

                # Iterate through the list/dict

                if type(v) in [int, float]:

                    # Working with string/int/float data, output this:

                    print("{}[{}]: {}".format(" " * (depth*3), k, v))

                    continue

                if type(v) == str:

                    # Working with strings, doing some special formatting stuff:

                    spaces = " " * (depth * 3)

                    if '\n' in v:

                        # We want to output this data to the edge of the screen:

                        print("{}[{}]:\n{}".format(spaces, k, v))

                        continue

                    # We replace newline chars with spaces, so we can keep out formatting uniform

                    print("{}[{}]: {}".format(spaces, k, v))

                    continue

                # Found something we can't work with, move it down

                print("{}[{}]:".format(" " * (depth*3), k))

                self.recursive_print(data[k], depth=depth+1)

        # Done traversing the data for this level

        return


parser = argparse.ArgumentParser(description="Minecraft RCON/Query/Ping Server List client", add_help=False)

# Specifying hostname and port number:

parser.add_argument('host', type=str, help='Hostname of the Minecraft server. '
                                           'You may also specify a port using the \':\' character.')
subparser = parser.add_subparsers(title="Connection Options", help="Connection Options",
                                  dest='connection')
subparser.required = True  # Workaround for previous python 3 versions

parser.add_argument('-h', '--help', help='Show this help message and exit', action=_HelpAction)

# Splitting RCON/Query/Server List Ping into separate sup-parsers

# RCON:

rcon_parser = subparser.add_parser('rcon', help='Establish a RCON connection and send commands.')
rcon_parser.add_argument('password', help='RCON password')
rcon_parser.add_argument('-c', '--command', action='append', nargs='+',
                         help='Command to send to the RCON server. May specify multiple.', required=False)
rcon_parser.add_argument('-i', '--interactive', help="Starts an interactive session with the RCON server.",
                         action="store_true")

# QUERY:

query_parser = subparser.add_parser('query', help='Retrieve server statistics via the Query protocol.')
query_parser.add_argument('-f', '--full', help='Retrieve full stats.', action='store_true')

# PING:

ping_parser = subparser.add_parser('ping', help='Retrieve server statistics via the Server List Ping interface.')
ping_parser.add_argument('-sf', '--show-favicon', help='Output favicon data to the terminal.',
                         action='store_true')
ping_parser.add_argument('-p', '--proto-num', help='Sets the protocol number to use. Use this to emulate different '
                                                   'client versions.',
                         type=int, default=0, metavar='PROTOCOL_NUMBER')

# Output Options:

output = parser.add_argument_group('Output Options')
format_options = output.add_mutually_exclusive_group()
output.add_argument('-o', '--output', help="Saves the output to a file in JSON format(Only saves relevant content, "
                                           "such as server responses and errors).", metavar="PATH")
format_options.add_argument('-oc', '--output-color',
                            help='Replaces format chars with ascii color codes in the output file. '
                                 'Default action is to remove them.',
                            action='store_true')
format_options.add_argument('-or', '--output-raw', help='Leaves formatting chars when outputting to output file. '
                                                        'Default action is to remove them.',
                            action="store_true")

# Normal Options

parser.add_argument('-nc', '--no-color', help='Disables color output, removes format chars', action='store_false')
parser.add_argument('-r', '--raw',
                    help='Shows format chars, does not remove them', action='store_true')
parser.add_argument('-t', '--timeout', help='Timeout value for socket operations', default=60, type=int)
parser.add_argument('-ri', '--reqid', help='Sets a custom request id, instead of randomly generating one.')
parser.add_argument('-q', '--quiet', help="Program will not output anything to the terminal", action="store_true")

# Checking for no arguments:


def main():

    if len(sys.argv) == 1:

        # No arguments supplied, outputting help menu

        parser.parse_args(['--help'])

        sys.exit()

    args = parser.parse_args()

    # Formatting the hostname provided:

    if ':' in args.host:

        # Defining custom port number:

        index = args.host.index(':')

        # Getting port number:

        port = args.host[index+1:]

        # getting host name:

        host = args.host[:index]

    else:

        # Set the port on a per-connection basis

        port = None

        # Getting hostname

        host = args.host

    # Creating output here:

    out = Output(args)

    if args.connection == 'rcon':

        # User wants a RCON connection:

        if port is None:

            # Set the port to the default RCON port

            port = RCON_PORT

        with RCONClient(host, port, reqid=args.reqid, format_method=RCONClient.RAW, timeout=args.timeout) as rcon:

            # Starting connection to RCON server:

            out.output(SEP)

            out.output("# Starting TCP connection to §2RCON§r server @ §2{}:{}§r ...".format(host, port))

            rcon.start()

            out.output("# Started TCP connection to §2RCON§r server @ §2{}:{}§r!".format(host, port))

            # Authenticating to RCON server

            out.output("# Authenticating with §2RCON§r server ...")

            val = rcon.authenticate(args.password)

            if not val:

                # Authentication failed!

                out.output("§c# Authentication with §2RCON§c server failed - Incorrect Password!")

                sys.exit()

            out.output("# Authentication with §2RCON§r server successful!")

            # Running user commands:

            out.output("# Running user commands ...")

            if args.command:

                for com in args.command:

                    # Running user command:

                    out.output("# Executing user command: '§2{}§r' ...".format(' '.join(com)))

                    val = rcon.command(' '.join(com))

                    out.output(val, command=com, relevant=True)

                    out.output("# Done executing command: '§2{}§r'!".format(' '.join(com)))

            if args.interactive:

                # User wants to run an interactive session

                out.output(SEP)
                out.output("§b§nWelcome to the RCON interactive session!")
                out.output("§bConnection Info:\n  Host: §a{}§b\n  Port: §a{}§b".format(host, port))
                out.output("§bType 'q' to quit this session.")
                out.output("§bType 'help' or '?' for info on commands!\n")

                while True:

                    # Getting input from user:

                    inp = input("rcon@{}:{}>>".format(host, port))

                    if inp == 'q':

                        # User is done inputting, exit

                        break

                    # Sending input to server:

                    val = rcon.command(inp)

                    out.output(val, command=inp, relevant=True)

    if args.connection == 'query':

        # User wants to retrieve stats via Query

        if port is None:

            # Set the port to the default Query port

            port = QUERY_PORT

        with QUERYClient(host, port, reqid=args.reqid, format_method=0, timeout=args.timeout) as query:

            out.output(SEP)

            # Adding relevant formatter

            out.formatters.add(QUERYFormatter, FormatterCollection.QUERY)

            if args.full:

                # User wants to retrieve full stats:

                out.output("# Authenticating with Query server @ §a{}:{}§r and retrieving full stats ...".format(host,
                                                                                                                 port))
                val = query.get_full_stats()

                out.output("# Retrieved full stats!:\n")

                out.output(val, command='QUERY_PROTOCOL', relevant=True)

            else:

                # User wants to retrieve basic stats:

                out.output("# Authenticating with Query server @ §a{}:{}§r and retrieving basic stats ...".format(host,
                                                                                                                  port))
                val = query.get_basic_stats()

                out.output("# Retrieved basic stats!:\n")

                out.output(val, command='QUERY_PROTOCOL', relevant=True)

    if args.connection == 'ping':

        # User wants to ping the server, and retrieve some basic stats

        if port is None:

            # Set the port to the default Minecraft port:

            port = MINECRAFT_PORT

        with PINGClient(host, port, reqid=args.reqid, format_method=0, timeout=60, proto_num=args.proto_num) as ping:

            out.output(SEP)

            # Adding relevant formatter

            out.formatters.add(PINGFormatter, FormatterCollection.PING)

            out.output("# Pinging Minecraft server @ §a{}:{}§r and retrieving stats ...".format(host, port))

            val = ping.get_stats()

            out.output("# Retrieved stats! Response time: {} milliseconds".format(val['time']))

            out.output("# Statistics:\n")

            out.output(val, command='PING_PROTOCOL', relevant=True)


if __name__ == "__main__":

    # Run the main function:

    main()
