import yagi.handler
import yagi.notifier.api

class PubSubHubBubHandler(yagi.handler.BaseHandler):
    def __call__(self, messages):
        result = None
        if self.app:
            result = self.app(messages)
        yagi.notifier.api.notify(messages)
        return result
         
