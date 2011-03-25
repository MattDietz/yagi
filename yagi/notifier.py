import pubsubhububub_publisher

def notify(hub, *urls):
    try:
        pubsubhubbub_publisher.publish(hub, urls)
    except pubsubhubbub_pubslisher.PublishError, e:
        pass
