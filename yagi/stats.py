"""Implements a basic statsd driver"""

# NOTE(cerberus): Implemented this way because we don't need other
# implementations at the moment, and I didn't want to introduce a
# new dependency at this time.

import socket

import yagi.config
import yagi.log


LOG = yagi.log.logger

DRIVER = None


class StatsD(object):
    def ping(self, data):
        LOG.debug("Sending stat: %s" % data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conf = yagi.config.config_with("stats")
        host = conf("host")
        port = int(conf("port"))
        try:
            sock.connect((host, port))
            sock.sendall(data)
        except socket.error:
            LOG.exception()

    def failure_message(self):
        return yagi.config.get("stats", "failure", default="yagi.failure")

    def elapsed_message(self):
        return yagi.config.get("stats", "elapsed", default="yagi.time_elapsed")

    def messages_sent(self):
        return yagi.config.get("stats", "messages_sent",
                                default="yagi.messages_sent")


class NoDriver(object):
    def ping(self, data):
        LOG.info(data)

    def failure_message(self):
        return "failure"

    def elapsed_message(self):
        return "time_elapsed"

    def messages_sent(self):
        return "messages_sent"


def time_stat(metric, value):
    """Format execution time."""
    DRIVER.ping("%s:%s|ms" % (metric, value * 1000.0))


def increment_stat(metric, value=1):
    """Format increment/decrement."""
    DRIVER.ping("%s:%s|c" % (metric, value))


def messages_sent():
    return DRIVER.messages_sent()


def elapsed_message():
    return DRIVER.elapsed_message()


def failure_message():
    return DRIVER.failure_message()


if (yagi.config.has_section("stats") and
    yagi.config.get("stats", "enabled").lower() == "true"):
    DRIVER = StatsD()
else:
    DRIVER = NoDriver()
