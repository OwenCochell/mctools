# Changelog

## 1.4.0

This release adds async clients that can be utilized in asyncio event loops.

### Added

- Added async clients for RCON, QUERY, and PING operations
- Added async protocol objects, which should lead to improved performance in asyncio loops
- Documentation changes regarding the async clients

## 1.3.0

This release contains some minor redesigns and bugfixes.

### Bug Fixes

- Removes an unnecessary ping operation when doing a ping request without asking for stats.
- Removed a lot of bug prone behavior from the decoders and clients

### Added

- LOTS of typing additions! These are added using the python typing system, as well as via docstrings.
Most of these changes are applied to internal components, as the high-level
user facing methods were already mostly-typed.

- Added some unit tests for decoders, tests for other components will be added at a later date!

### Changed

- PINGPackets, QUERYPackets, and some RCONPackets now determine state by using ints and globally defined values,
which should be slightly faster and should reduce the risk of bugs where packet
types differ across the codebase.

- Many changes to make the codebase more clear and less bug prone.

- Project now has a pyproject.toml file which is used for tool configuration and building.

- Moved changelog (this file!) from `README.md` to `CHANGELOG.md`

## 1.2.2

Removed some debugging print statements.

## 1.2.1

We now correctly disable length checking in RCONClient if specified by the user.

The 'set_timeout()' method in BaseProtocol will now work correctly even if the protocol object is not started.
This change applies to all clients, as they all use this method.

Added a 'DEFAULT_TIMEOUT' constant and moved some protocol attributes to BaseProtocol to prevent redundancy.
Protocol objects now init the parent BaseProtocol object.

Fixed some spelling errors, added more type hinting, made some more minor changes to the documentation.

## 1.2.0

Clients (of any type!) can now be started after being stopped,
so creating a new client after stopping it is no longer necessary.

The PINGClient will now auto stop itself after each operation.

Fixed a bug where the QUERYClient did not auto-start itself.

The documentation was updated to reflect these changes, and it now explains
stopping/starting clients a lot better.

## 1.1.2

Fixed an issue where RCON command size handling was broken.
Before, the remote server would kill the connection if a command is too large(Bigger than 1460 bytes).
We now raise a new exception, 'RCONLengthError' and refuse to send the packet if the command is too big,
thus keeping the connection alive. You can optionally disable this check, although this is not recommended.

The documentation has also been updated to make this limitation more clear,
as well as correcting some minor errors, mostly correcting examples in the formatting documentation.

We also added some type hinting, as some IDEs were complaining about type mismatches.

## 1.1.1

Fixed an issue where clients hang when the connection is closed by the remote host.

New features mentioned in the previous changelog are still coming, albeit slowly!

## 1.1.0

This update adds some minor features and fixes some major bugs:

### Bug Fixes:

- Fixed RCON packet fragmentation issue, mctools should now properly detect and handle RCON packet fragmentation
- Fixed bug where PINGFormatter was looking for 'dark_grey' instead of 'dark_gray'
- Fixed bug where ChatObjectFormatter did not properly parse ChatObjects
- We now raise an exception if the RCON write data is too big, instead of leaving the connection in a unstable state

### Features Added:

- Users can now specify the format method on a per-call basis
- Users can change the timeout value after the object is instantiated
- The RCON login check feature can be disabled, meaning that you can attempt to send packets
even if you are not authenticated
- Clients can now return raw packets
- RCON now has custom exceptions

This update is a prelude to another update I have working on.
The next update will add numerous features, such as:

- RCON Mixins for easing the process of getting/editing the following info:
- Players connected
- World Seed
- Game Rules
- Target Selectors
- Many more...
- Custom exceptions for Ping and Query
- Even Better error handling
- mcli RCON command/argument autocompletion
- Custom datatypes for all operations
- RCON SSH Forwarding support
(You can technically do this as of now, but I want the library to invoke and handle this process) for a more
secure RCON experience
- Unit tests for mctools

I have some of these complete as of now, but I wanted to push out the big bug fixes and minor stuff before 
I finish creating and refining the features, as they may take me some time to implement.

All of these features will be completely optional, and they will all be backwards compatible.
So if you like the library as it is now, then you can completely ignore these new features.

The documentation has been updated to reflect these changes.
