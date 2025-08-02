from collections import defaultdict, deque
from typing import List, Optional

from .models import Connection, Node


class GraphService:
    """Service class for graph operations."""

    @staticmethod
    def find_path(from_node: Node, to_node: Node) -> Optional[List[str]]:
        """
        Find a path between two nodes using BFS algorithm.

        Args:
            from_node: The starting node
            to_node: The destination node

        Returns:
            A list of node names representing the path, or None if no path exists
        """
        if from_node == to_node:
            return [from_node.name]

        # Build adjacency list for efficient traversal
        graph = defaultdict(list)
        connections = Connection.objects.select_related("from_node", "to_node").all()

        for connection in connections:
            graph[connection.from_node.id].append(connection.to_node.id)

        # BFS to find shortest path
        queue = deque([(from_node.id, [from_node.id])])
        visited = {from_node.id}

        while queue:
            current_node_id, path = queue.popleft()

            for neighbor_id in graph[current_node_id]:
                if neighbor_id == to_node.id:
                    # Found the destination, build the path with node names
                    full_path = path + [neighbor_id]
                    node_names = []

                    # Convert node IDs to names
                    node_id_to_name = {
                        node.id: node.name
                        for node in Node.objects.filter(id__in=full_path)
                    }

                    for node_id in full_path:
                        node_names.append(node_id_to_name[node_id])

                    return node_names

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    @staticmethod
    def get_or_create_node(name: str) -> tuple[Node, bool]:
        """
        Get an existing node or create a new one.

        Args:
            name: The name of the node

        Returns:
            A tuple of (node, created) where created is True if the node was created
        """
        return Node.objects.get_or_create(name=name)

    @staticmethod
    def create_connection(from_node_name: str, to_node_name: str) -> Connection:
        """
        Create a connection between two nodes.

        Args:
            from_node_name: Name of the source node
            to_node_name: Name of the target node

        Returns:
            The created Connection instance

        Raises:
            Node.DoesNotExist: If either node doesn't exist
            ValidationError: If the connection is invalid
        """
        from_node = Node.objects.get(name=from_node_name)
        to_node = Node.objects.get(name=to_node_name)

        return Connection.objects.create(from_node=from_node, to_node=to_node)

    @staticmethod
    def get_node_by_name(name: str) -> Node:
        """
        Get a node by its name.

        Args:
            name: The name of the node

        Returns:
            The Node instance

        Raises:
            Node.DoesNotExist: If the node doesn't exist
        """
        return Node.objects.get(name=name)
