import datetime
import dateutil.parser
import json


class FilterMessage(object):
    def __init__(self, map_file, logger):
        self.log = logger
        with open(map_file, 'r') as f:
            self.transform_dict = json.load(f)

    def transform(self, mapping, message):
        for k, v in mapping.iteritems():
            if isinstance(message, dict) and message.get(k):
                if isinstance(message[k], dict):
                    self.transform(v, message[k])
                else:
                    message[k] = v
        return message

    def __call__(self, message):
        return self.transform(self.transform_dict, message)


class FilterMessageMatch(FilterMessage):
    def transform(self, mapping, message):
        for k, v in mapping.iteritems():
            if isinstance(message, dict) and message.get(k):
                if isinstance(v, dict):
                    message[k] = self.transform(v, message[k])
                elif isinstance(v, list):
                    for match_dict in v:
                        if match_dict.get(unicode(message[k])):
                            message[k] = match_dict[unicode(message[k])]
                            break
            else:
                if unicode(k) == message:
                    return v
        return message


class FilterMessageTimestamp(FilterMessage):
    def transform(self, mapping, message):
        for k, v in mapping.iteritems():
            if isinstance(message, dict) and message.get(k):
                if isinstance(message[k], dict):
                    self.transform(v, message[k])
                else:
                    try:
                        audit = dateutil.parser.parse(message[k])
                        delta = datetime.timedelta(hours=int(v))
                        message[k] = str(audit + delta)
                    except Exception, e:
                        # log the exception, but there still could be other
                        # keys to convert
                        self.log.exception(e)
        return message
