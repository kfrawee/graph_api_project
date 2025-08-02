import time
from typing import List, Optional

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist


from .constants import TASK_STATUSES
from .models import Node
from .services import GraphService


@shared_task(bind=True, name='graph_api.slow_find_path')
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
            state=TASK_STATUSES.PROCESSING.value,
            meta={"message": "Starting path finding operation..."},
        )

        # Simulate a slow operation
        time.sleep(5)

        # Get the nodes
        try:
            from_node = Node.objects.get(name=from_node_name)
            to_node = Node.objects.get(name=to_node_name)
        except ObjectDoesNotExist as e:
            self.update_state(
                state=TASK_STATUSES.FAILURE.value,
                meta={"message": f"Node not found: {str(e)}"},
            )
            raise Exception(f"Node not found: {str(e)}")

        # Find the path using the service
        path = GraphService.find_path(from_node, to_node)

        if path is None:
            self.update_state(
                state=TASK_STATUSES.FAILURE.value,
                meta={
                    "message": f"No path found from {from_node_name} to {to_node_name}"
                },
            )
            return None

        # Update task state
        self.update_state(
            state=TASK_STATUSES.SUCCESS.value,
            meta={
                "path": path,
                "message": f"Path found from {from_node_name} to {to_node_name}",
            },
        )

        return {
            "path": path,
            "message": f"Path finding completed from {from_node_name} to {to_node_name}",
        }

    except Exception as exc:
        if self.request.retries < 3:
            self.update_state(
                state=TASK_STATUSES.RETRY.value,
                meta={"message": "Retrying due to an error...", "error": str(exc)},
            )
            self.retry(exc=exc, countdown=10, max_retries=3)
        else:
            self.update_state(
                state=TASK_STATUSES.FAILURE.value,
                meta={
                    "message": "Max retries reached. Task failed.",
                    "error": str(exc),
                },
            )
