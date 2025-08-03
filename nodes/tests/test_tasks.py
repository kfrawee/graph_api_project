from unittest.mock import patch, MagicMock

from django.test import TestCase

from ..models import Node
from ..tasks import slow_find_path_task


class TasksTest(TestCase):
    """Test cases for Celery tasks."""

    def setUp(self):
        """Set up test data."""
        self.node_a = Node.objects.create(name="A")
        self.node_b = Node.objects.create(name="B")

    @patch("nodes.tasks.time.sleep")
    @patch("nodes.tasks.GraphService.find_path")
    def test_slow_find_path_task_success(self, mock_find_path, mock_sleep):
        """Test successful execution of slow_find_path_task."""
        mock_find_path.return_value = ["A", "B"]

        # Create a mock task instance
        mock_task = MagicMock()

        result = slow_find_path_task.apply(args=["A", "B"], task_id="test-task-id")

        mock_sleep.assert_called_once_with(5)
        self.assertIsNotNone(result.result)

    @patch("nodes.tasks.time.sleep")
    def test_slow_find_path_task_node_not_found(self, mock_sleep):
        """Test slow_find_path_task when node doesn't exist."""
        result = slow_find_path_task.apply(
            args=["A", "NonExistent"], task_id="test-task-id"
        )
        self.assertEqual(result.info.get("status"), "FAILURE")
        self.assertIn("Node not found", result.info["message"])
        mock_sleep.assert_called_once_with(5)
