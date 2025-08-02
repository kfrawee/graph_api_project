from enum import Enum


class TASK_STATUSES(Enum):
    """
    Constants representing various statuses.
    """

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"

    CHOICES = (
        (PENDING, PENDING),
        (SUCCESS, SUCCESS),
        (FAILURE, FAILURE),
        (RETRY, RETRY),
    )
