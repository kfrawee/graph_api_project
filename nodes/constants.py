from enum import Enum


class TASK_STATUSES(Enum):
    """
    Constants representing various statuses.
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
