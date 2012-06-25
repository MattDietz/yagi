import json


class FilterMessage(object):
    # I tried really hard not to make this a class, but I need state
    def __init__(self, map_file):
        with open(map_file, 'r') as f:
            self.transform_dict = json.load(f)

    def transform(self, mapping, message):
        for k, v in mapping.iteritems():
            if isinstance(message, dict) and message.get(k):
                if isinstance(v, dict):
                    message[k] = self.transform(v, message[k])
            else:
                if unicode(k) == message:
                    return v

        return message

    def __call__(self, message):
        return self.transform(self.transform_dict, message)
