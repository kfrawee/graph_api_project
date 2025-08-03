from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from nodes.models import Connection, Node


class NodeModelTest(TestCase):
    """Test cases for the Node model."""

    def test_create_node(self):
        """Test creating a node."""
        node = Node.objects.create(name="test_node")
        self.assertEqual(node.name, "test_node")
        self.assertIsNotNone(node.created_at)
        self.assertIsNotNone(node.updated_at)

    def test_node_name_required(self):
        """Test that node name is required."""
        with self.assertRaises(IntegrityError):
            Node.objects.create(name=None)

    def test_node_str_representation(self):
        """Test string representation of node."""
        node = Node.objects.create(name="test_node")
        self.assertEqual(str(node), "test_node")

    def test_node_unique_name_constraint(self):
        """Test that node names must be unique."""
        Node.objects.create(name="duplicate")
        with self.assertRaises(IntegrityError):
            Node.objects.create(name="duplicate")


class ConnectionModelTest(TestCase):
    """Test cases for the Connection model."""

    def setUp(self):
        """Set up test data."""
        self.node_a = Node.objects.create(name="A")
        self.node_b = Node.objects.create(name="B")
        self.node_c = Node.objects.create(name="C")

    def test_create_connection(self):
        """Test creating a connection between nodes."""
        connection = Connection.objects.create(
            from_node=self.node_a, to_node=self.node_b
        )
        self.assertEqual(connection.from_node, self.node_a)
        self.assertEqual(connection.to_node, self.node_b)
        self.assertIsNotNone(connection.created_at)

    def test_connection_str_representation(self):
        """Test string representation of connection."""
        connection = Connection.objects.create(
            from_node=self.node_a, to_node=self.node_b
        )
        self.assertEqual(str(connection), "A -> B")

    def test_connection_unique_constraint(self):
        """Test that connections between same nodes must be unique."""
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)
        with self.assertRaises(IntegrityError):
            Connection.objects.create(from_node=self.node_a, to_node=self.node_b)

    def test_connection_self_loop_validation(self):
        """Test that a node cannot connect to itself."""
        connection = Connection(from_node=self.node_a, to_node=self.node_a)
        with self.assertRaises(ValidationError):
            connection.save()

    def test_connection_related_names(self):
        """Test related names for connections."""
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)
        Connection.objects.create(from_node=self.node_b, to_node=self.node_c)
        Connection.objects.create(from_node=self.node_c, to_node=self.node_a)

        # Test outgoing connections
        outgoing = self.node_a.outgoing_connections.all()
        self.assertEqual(len(outgoing), 1)
        self.assertEqual(outgoing[0].to_node, self.node_b)

        # Test incoming connections
        incoming = self.node_a.incoming_connections.all()
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0].from_node, self.node_c)
