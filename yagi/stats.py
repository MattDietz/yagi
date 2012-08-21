"""Implements a basic statsd driver"""

# NOTE(cerberus): Implemented this way because we don't need other
# implementations at the moment, and I didn't want to introduce a
# new dependency at this time.

import socket

import yagi.config
import yagi.log


LOG = yagi.log.logger


def _statsd_ping(data):
    enabled = yagi.config.get("stats", "enabled")
    LOG.debug("Sending stat: %s" % data)
    if enabled.lower() == "True":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conf = yagi.config.config_with("stats")
        host = conf("host")
        port = int(conf("port"))
        try:
            sock.connect((host, port))
            sock.sendall(data)
        except socket.error:
            LOG.exception()
    else:
        LOG.info(data)


def time_stat(metric, value):
    """Format execution time."""
    _statsd_ping("%s:%s|ms" % (metric, value * 1000.0))


def increment_stat(metric, value=1):
    """Format increment/decrement."""
    _statsd_ping("%s:%s|c" % (metric, value))
