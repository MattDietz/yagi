import yagi.handler
import yagi.notifier.pubsubhubbub


class PubSubHubBubHandler(yagi.handler.BaseHandler):
    def __call__(self, messages):
        result = None
        if self.app:
            result = self.app(messages)
        yagi.notifier.pubsubhubbub.notify(messages)
        return result
