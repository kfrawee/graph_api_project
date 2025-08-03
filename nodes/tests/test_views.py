import os
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Connection, Node


class NodesAPITest(APITestCase):
    """Test cases for the nodes API views."""

    def setUp(self):
        """Set up test data."""
        self.node_a = Node.objects.create(name="A")
        self.node_b = Node.objects.create(name="B")

    def test_health_check(self):
        """Test the health check endpoint."""
        url = reverse("nodes:health_check")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertIn("timestamp", response.data)

    def test_create_node_success(self):
        """Test creating a node successfully."""
        url = reverse("nodes:create_node")
        data = {"name": "TestNode"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "TestNode")
        self.assertTrue(Node.objects.filter(name="TestNode").exists())

    def test_create_node_duplicate_name(self):
        """Test creating a node with duplicate name."""
        url = reverse("nodes:create_node")
        data = {"name": "A"}  # Node A already exists

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", str(response.data))

    def test_create_node_invalid_data(self):
        """Test creating a node with invalid data."""
        url = reverse("nodes:create_node")
        data = {}  # Missing name

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_connect_nodes_success(self):
        """Test connecting nodes successfully."""
        url = reverse("nodes:connect_nodes")
        data = {"from_node": "A", "to_node": "B"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Successfully connected", response.data["message"])
        self.assertTrue(
            Connection.objects.filter(
                from_node=self.node_a, to_node=self.node_b
            ).exists()
        )

    def test_connect_nodes_nonexistent_node(self):
        """Test connecting nodes when one doesn't exist."""
        url = reverse("nodes:connect_nodes")
        data = {"from_node": "A", "to_node": "NonExistent"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_connect_nodes_self_loop(self):
        """Test connecting a node to itself."""
        url = reverse("nodes:connect_nodes")
        data = {"from_node": "A", "to_node": "A"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_find_path_success(self):
        """Test finding a path successfully."""
        # Create a connection
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)

        url = reverse("nodes:find_path")
        data = {"from_node": "A", "to_node": "B"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["path"], ["A", "B"])
        self.assertTrue(response.data["path_exists"])

    def test_find_path_no_connection(self):
        """Test finding a path when no connection exists."""
        url = reverse("nodes:find_path")
        data = {"from_node": "A", "to_node": "B"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["path"])
        self.assertFalse(response.data["path_exists"])

    def test_list_nodes(self):
        """Test listing all nodes."""
        url = reverse("nodes:list_nodes")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["nodes"]), 2)

    @patch("nodes.views.slow_find_path_task.delay")
    def test_slow_find_path_success(self, mock_delay):
        """Test async task initiation for finding path."""
        mock_result = MagicMock()
        mock_result.id = "test-task-id"
        mock_result.state = "PENDING"
        mock_delay.return_value = mock_result

        url = reverse("nodes:slow_find_path")
        data = {"from_node": "A", "to_node": "B"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["task_id"], "test-task-id")
        self.assertEqual(response.data["status"], "PENDING")
        mock_delay.assert_called_once_with("A", "B")

    @patch("nodes.views.AsyncResult")
    def test_get_slow_path_result_pending(self, mock_async_result_class):
        """Test fetching async result when task is still pending."""
        mock_result = MagicMock()
        mock_result.state = "PENDING"
        mock_result.ready.return_value = False
        mock_result.backend.get_task_meta.return_value = {
            "status": "PENDING",
            "result": None,
        }
        mock_async_result_class.return_value = mock_result

        url = reverse("nodes:get_slow_path_result", kwargs={"task_id": "test-id"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")

    @patch("nodes.views.AsyncResult")
    def test_get_slow_path_result_success(self, mock_async_result_class):
        """Test fetching async result after task completion."""
        mock_async_result = MagicMock()
        mock_async_result_class.return_value = mock_async_result

        mock_async_result.id = "test-id"
        mock_async_result.state = "SUCCESS"
        mock_async_result.ready.return_value = True
        mock_async_result.info = {
            "path": ["A", "B"],
            "message": "Success",
            "status": "SUCCESS",
            "error": None,
        }

        mock_async_result.backend.get_task_meta.return_value = {
            "status": "SUCCESS",
            "result": {"path": ["A", "B"], "message": "Success"},
        }

        url = reverse("nodes:get_slow_path_result", kwargs={"task_id": "test-id"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "SUCCESS")
        self.assertEqual(response.data["path"], ["A", "B"])
