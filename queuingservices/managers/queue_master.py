from queuingservices.managers.queue_lifecycle_manager import QueueLifecycleManager
from queuingservices.managers.queue_publisher_manager import QueuePublisherManager
from queuingservices.managers.queue_subscriber_manager import QueueSubscriberManager


class QueueMaster(QueueSubscriberManager, QueuePublisherManager, QueueLifecycleManager):
    """

    This class interfaces all types of queue objects that you might want.

    """
    pass
