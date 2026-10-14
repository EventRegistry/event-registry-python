import logging

__all__ = ["logger"]

# the package logs to the "eventregistry" logger. As a library it does not configure the logging itself - the level
# and the handlers are set by the application, for example:
#     logging.basicConfig(level=logging.INFO)                        # show the logs of all modules
#     logging.getLogger("eventregistry").setLevel(logging.DEBUG)     # more details from this package
# We deliberately don't add any handler (not even a NullHandler): without any logging configuration python then
# still prints the warnings and errors of the package to stderr
logger = logging.getLogger("eventregistry")
