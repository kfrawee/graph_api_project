from enum import Enum


class TASK_STATUSES(Enum):
    """
    Constants representing various statuses.
    """

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples for use in model field choices.
        """
        return [(status.value, status.name) for status in cls]
