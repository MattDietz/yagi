import yagi.handler
import yagi.notifier.atompub


class AtomPub(yagi.handler.BaseHandler):
    def __call__(self, messages):
        result = None
        if self.app:
            result = self.app(messages)
        yagi.notifier.atompub.notify(messages)
        return result
