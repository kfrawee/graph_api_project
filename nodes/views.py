from datetime import datetime

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Node
from .serializers import (
    ConnectNodesSerializer,
    CreateNodeSerializer,
    FindPathSerializer,
    NodeSerializer,
    TaskResultSerializer,
)
from .services import GraphService
from .tasks import slow_find_path_task


@api_view(["POST"])
def create_node(request):
    """
    Create a new node.

    Accepts a single parameter: name
    Creates and stores a node with the given name.

    Request body:
    {
        "name": "node_name"
    }

    Returns:
    - 201: Node created successfully
    - 400: Invalid input data
    """
    serializer = CreateNodeSerializer(data=request.data)
    if serializer.is_valid():
        node = serializer.save()
        response_serializer = NodeSerializer(node)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def connect_nodes(request):
    """
    Connect two nodes.

    Accepts two parameters: from_node and to_node
    Connects the from_node to the to_node.

    Request body:
    {
        "from_node": "source_node_name",
        "to_node": "target_node_name"
    }

    Returns:
    - 201: Connection created successfully
    - 400: Invalid input data or nodes don't exist
    """
    serializer = ConnectNodesSerializer(data=request.data)

    if serializer.is_valid():
        connection = serializer.save()
        return Response(
            {
                "id": connection.id,
                "message": f"Successfully connected '{connection.from_node.name}' to '{connection.to_node.name}'",
                "from_node": connection.from_node.name,
                "to_node": connection.to_node.name,
                "created_at": connection.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def find_path(request):
    """
    Find a path between two nodes.

    Accepts two parameters: from_node and to_node
    Returns a list of node names representing the path or None if no path exists.

    Request body:
    {
        "from_node": "source_node_name",
        "to_node": "target_node_name"
    }

    Returns:
    - 200: Path found or no path exists (both are successful responses)
    - 400: Invalid input data or nodes don't exist
    """
    serializer = FindPathSerializer(data=request.data)

    if serializer.is_valid():
        from_node = serializer.validated_data["from_node"]
        to_node = serializer.validated_data["to_node"]

        path = GraphService.find_path(from_node, to_node)

        return Response(
            {
                "path": path,
                "from_node": from_node.name,
                "to_node": to_node.name,
                "path_exists": path is not None,
            },  # status=status.HTTP_200_OK if path is not None else status.HTTP_404_NOT_FOUND
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def slow_find_path(request):
    """
    Initiate a slow path-finding operation using Celery.

    This endpoint enqueues a Celery task that sleeps for 5 seconds
    and then calls the path-finding logic.

    Request body:
    {
        "from_node": "source_node_name",
        "to_node": "target_node_name"
    }

    Returns:
    - 202: Task queued successfully
    - 400: Invalid input data or nodes don't exist
    """
    serializer = FindPathSerializer(data=request.data)

    if serializer.is_valid():
        from_node = serializer.validated_data["from_node"]
        to_node = serializer.validated_data["to_node"]

        # Start the Celery task
        task = slow_find_path_task.delay(from_node.name, to_node.name)

        return Response(
            {
                "task_id": task.id,
                "status": task.state,
                "message": "Path finding task started",
                "from_node": from_node.name,
                "to_node": to_node.name,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_slow_path_result(request, task_id):
    """
    Get the result of a slow path-finding task.

    Accepts a task_id parameter and returns the result of the path-finding task
    if it's complete, otherwise returns a PENDING status.

    URL parameter:
    - task_id: The ID of the Celery task

    Returns:
    - 200: Task result (either completed or pending)
    - 404: Task not found
    - 500: Internal server error if something goes wrong
    """
    try:
        task_result = AsyncResult(task_id)
        task_meta = task_result.backend.get_task_meta(task_id)

        if task_meta["status"] == "PENDING" and task_meta.get("result") is None:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Somehow this is not working
        if task_result.ready():
            _dict = task_result.info or {}

            response = TaskResultSerializer(
                {
                    "task_id": task_result.id,
                    "status": _dict.get("status"),
                    "path": _dict.get("path"),
                    "message": _dict.get("message"),
                    "error": _dict.get("error"),
                }
            )
            return Response(response.data)
        else:  # Task is still processing
            response = TaskResultSerializer(
                {
                    "task_id": task_result.id,
                    "status": "PENDING",
                    "message": "Task is still processing",
                    "path": None,
                    "error": None,
                }
            )

            return Response(response.data)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def list_nodes(request):
    """
    List all nodes in the system.

    Returns:
    - 200: List of all nodes
    """
    # TODO: Implement pagination
    nodes = Node.objects.all()

    serializer = NodeSerializer(nodes, many=True)
    return Response(
        {
            "nodes": serializer.data,
            "count": nodes.count(),
        }
    )


@api_view(["GET"])
def health_check(request):
    """
    Health check endpoint to verify the API is running.

    Returns:
    - 200: API is healthy
    """
    return Response(
        {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
        }
    )
