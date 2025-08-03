import time
from typing import List, Optional

from celery import shared_task
from celery.exceptions import Ignore
from django.core.exceptions import ObjectDoesNotExist


from .constants import TASK_STATUSES
from .models import Node
from .services import GraphService


@shared_task(bind=True, name="graph_api.slow_find_path")
def slow_find_path_task(
    self, from_node_name: str, to_node_name: str
) -> Optional[List[str]]:
    """
    Celery task to find a path between two nodes.

    This task simulates a slow path-finding operation by sleeping for 5 seconds
    before calling the actual path-finding logic.

    Args:
        from_node_name: The name of the source node
        to_node_name: The name of the target node

    Returns:
        A list of node names representing the path, or None if no path exists

    Raises:
        Exception: If either node doesn't exist or other errors occur
    """
    try:
        self.update_state(
            meta={
                "message": f"Processing path finding from {from_node_name} to {to_node_name}."
            },
        )

        # Simulate a slow operation
        time.sleep(5)

        try:
            from_node = Node.objects.get(name=from_node_name)
            to_node = Node.objects.get(name=to_node_name)
        except ObjectDoesNotExist as e:
            _dict = dict(
                status=TASK_STATUSES.FAILURE.value,
                path=None,
                message="Node not found.",
                error=str(e),
            )
            self.update_state(
                meta=_dict,
            )
            return _dict

        path = GraphService.find_path(from_node, to_node)

        if path is None:
            _dict = dict(
                status=TASK_STATUSES.FAILURE.value,
                path=None,
                message=f"No path found from {from_node_name} to {to_node_name}",
            )
            self.update_state(
                meta=_dict,
            )
            return _dict

        _dict = dict(
            status=TASK_STATUSES.SUCCESS.value,
            path=path,
            message=f"Path found from {from_node_name} to {to_node_name}",
        )
        self.update_state(
            meta=_dict,
        )
        return _dict

    except Exception as e:
        _dict = dict(
            status=TASK_STATUSES.FAILURE.value,
            path=None,
            message=f"An error occurred.",
            error=str(e),
        )
        self.update_state(
            meta=_dict,
        )
        raise Ignore() from e
