
from optparse import OptionParser
import sys

def example_function():
    print "Hello world!"

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option(
        "-p", "--port", dest="port", help="port to run on", default=8080)

    parser.add_option(
        "-s", "--server", dest="server",
        help="which http server to use", default="eventlet")

    # Since we did NOT specify a default here, options.action will be None
    # if it is not passed in.
    parser.add_option("-a", "--action", dest="action", help="function to call")

    (options, args) = parser.parse_args(sys.argv)

    # Use your vars like:
    print options.port
    print options.server
    # This could be None if the user doesn't pass since we didn't specify a default
    print options.action

    # However, if we try to print a random option that we did not define above,
    # this WILL generate an exception.

    # The exception will look like:
    # Traceback (most recent call last):
    #   File "opt_parse.py", line XXX, in <module>
    #     print options.blah
    # AttributeError: Values instance has no attribute 'blah'

    # Now, if we simply want the action option to map to a function in this file
    # that we want to call, we can do the following:

    # Make sure action is in the global symbol table, and is callable.
    # Note only imports and names defined in this file will be in this top level
    # dictionary returned from globals().
    if options.action not in globals() or not callable(globals()[options.action]):
        # Error: action was not specified, or was not a valid function in this file
        parser.print_help()
        print "error: action (%s) was not a valid function in this file." % options.action
    else:
        # Success: call the function
        globals()[options.action]()
