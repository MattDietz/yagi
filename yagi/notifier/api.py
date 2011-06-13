import yagi.config


def notify(notifications):
    notifier = yagi.utils.import_module(yagi.config.get('notifier',
            'notifications_driver'))
    notifier.notify(notifications)
