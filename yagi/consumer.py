import time

import yagi.config
import yagi.filters
import yagi.log
import yagi.stats
import yagi.utils

LOG = yagi.log.logger


class Consumer(object):
    def __init__(self, queue_name, app=None, config=None):
        self.filters = []
        self.queue_name = queue_name
        self.config = yagi.config.config_with("consumer:%s" % queue_name)
        apps = [a.strip() for a in self.config("apps").split(",")]
        prev_app = None
        for a in apps:
            prev_app = yagi.utils.import_class(a)(prev_app,
                                                queue_name=self.queue_name)
        self.app = prev_app
        self.max_messages = int(self.config("max_messages"))

        filter_names = self.config("filters")
        if filter_names:
            filters = (f.strip() for f in filter_names.split(","))
            for f in filters:
                section = yagi.config.config_with("filter:%s" % f)
                map_file = section("map_file")
                method = section("method")
                filter_class = yagi.filters.get_filter(method, map_file, LOG)
                if not filter_class:
                    # Since these should go away, I don't know that it's a big
                    # deal if we can't find one
                    continue
                self.filters.append(filter_class)

    def connect(self, connection, consumer):
        self.connection = connection
        self.consumer = consumer

    def fetched_messages(self, messages):
        def next_message():
            for message in messages:
                self.message = message
                payload = message.payload
                for f in self.filters:
                    payload = f(payload)
                yield payload
                message.ack()

        try:
            start_time = time.time()
            self.app(next_message)
            yagi.stats.time_stat(yagi.config.get("stats", "elapsed"),
                                 time.time() - start_time)
        except Exception, e:
            # If we get all the way back out here, that's bad juju
            LOG.exception("Error in fetched_messages: \n%s" % e)

        yagi.stats.increment_stat(yagi.config.get("stats", "messages_sent"),
                                  len(messages))
