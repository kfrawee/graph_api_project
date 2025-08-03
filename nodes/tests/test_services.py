from django.test import TestCase

from ..models import Connection, Node
from ..services import GraphService


class GraphServiceTest(TestCase):
    """Test cases for the GraphService."""

    def setUp(self):
        """Set up test data with a more complex graph."""
        # Create nodes: A -> B -> C -> D
        #               A -> E -> D
        self.node_a = Node.objects.create(name="A")
        self.node_b = Node.objects.create(name="B")
        self.node_c = Node.objects.create(name="C")
        self.node_d = Node.objects.create(name="D")
        self.node_e = Node.objects.create(name="E")
        self.node_isolated = Node.objects.create(name="Isolated")

        # Create connections
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)
        Connection.objects.create(from_node=self.node_b, to_node=self.node_c)
        Connection.objects.create(from_node=self.node_c, to_node=self.node_d)
        Connection.objects.create(from_node=self.node_a, to_node=self.node_e)
        Connection.objects.create(from_node=self.node_e, to_node=self.node_d)

    def test_find_direct_path(self):
        """Test finding a direct path between connected nodes."""
        path = GraphService.find_path(self.node_a, self.node_b)
        self.assertEqual(path, ["A", "B"])

    def test_find_shortest_path(self):
        """Test finding the shortest path when multiple paths exist."""
        path = GraphService.find_path(self.node_a, self.node_d)
        # Should find the shorter path A -> E -> D instead of A -> B -> C -> D
        self.assertEqual(path, ["A", "E", "D"])

    def test_find_path_same_node(self):
        """Test finding path from a node to itself."""
        path = GraphService.find_path(self.node_a, self.node_a)
        self.assertEqual(path, ["A"])

    def test_find_path_no_connection(self):
        """Test finding path when no connection exists."""
        path = GraphService.find_path(self.node_a, self.node_isolated)
        self.assertIsNone(path)

    def test_find_path_reverse_direction(self):
        """Test finding path in reverse direction (should fail)."""
        path = GraphService.find_path(self.node_d, self.node_a)
        self.assertIsNone(path)

    def test_get_or_create_node_existing(self):
        """Test getting an existing node."""
        node, created = GraphService.get_or_create_node("A")
        self.assertEqual(node, self.node_a)
        self.assertFalse(created)

    def test_get_or_create_node_new(self):
        """Test creating a new node."""
        node, created = GraphService.get_or_create_node("NewNode")
        self.assertEqual(node.name, "NewNode")
        self.assertTrue(created)

    def test_get_node_by_name(self):
        """Test getting a node by name."""
        node = GraphService.get_node_by_name("A")
        self.assertEqual(node, self.node_a)

    def test_get_node_by_name_not_found(self):
        """Test getting a non-existent node by name."""
        with self.assertRaises(Node.DoesNotExist):
            GraphService.get_node_by_name("NonExistent")
