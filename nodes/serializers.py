from rest_framework import serializers

from .constants import TASK_STATUSES
from .models import Connection, Node


class NodeSerializer(serializers.ModelSerializer):
    """Serializer for Node model."""

    class Meta:
        model = Node
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateNodeSerializer(serializers.Serializer):
    """Serializer for creating a new node."""

    name = serializers.CharField(
        max_length=255, help_text="The name of the node to create"
    )

    def validate_name(self, value):
        """Validate that the node name doesn't already exist."""
        if Node.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"Node with name '{value}' already exists."
            )
        return value

    def create(self, validated_data):
        """Create and return a new Node instance."""
        return Node.objects.create(**validated_data)


class ConnectNodesSerializer(serializers.Serializer):
    """Serializer for connecting two nodes."""

    from_node = serializers.CharField(
        max_length=255, help_text="The name of the source node"
    )
    to_node = serializers.CharField(
        max_length=255, help_text="The name of the target node"
    )

    def validate_from_node(self, value):
        """Validate that the from_node exists."""
        try:
            return Node.objects.get(name=value)
        except Node.DoesNotExist:
            raise serializers.ValidationError(
                f"Node with name '{value}' does not exist."
            )

    def validate_to_node(self, value):
        """Validate that the to_node exists."""
        try:
            return Node.objects.get(name=value)
        except Node.DoesNotExist:
            raise serializers.ValidationError(
                f"Node with name '{value}' does not exist."
            )

    def validate(self, attrs):
        """Validate that the connection doesn't already exist and nodes are different."""
        from_node = attrs["from_node"]
        to_node = attrs["to_node"]

        if from_node == to_node:
            raise serializers.ValidationError("A node cannot connect to itself.")

        if Connection.objects.filter(from_node=from_node, to_node=to_node).exists():
            raise serializers.ValidationError(
                f"Connection from '{from_node.name}' to '{to_node.name}' already exists."
            )

        return attrs

    def create(self, validated_data):
        """Create and return a new Connection instance."""
        return Connection.objects.create(**validated_data)


class FindPathSerializer(serializers.Serializer):
    """Serializer for finding a path between two nodes."""

    from_node = serializers.CharField(
        max_length=255, help_text="The name of the source node"
    )
    to_node = serializers.CharField(
        max_length=255, help_text="The name of the target node"
    )

    def validate_from_node(self, value):
        """Validate that the from_node exists."""
        try:
            return Node.objects.get(name=value)
        except Node.DoesNotExist:
            raise serializers.ValidationError(
                f"Node with name '{value}' does not exist."
            )

    def validate_to_node(self, value):
        """Validate that the to_node exists."""
        try:
            return Node.objects.get(name=value)
        except Node.DoesNotExist:
            raise serializers.ValidationError(
                f"Node with name '{value}' does not exist."
            )


class TaskResultSerializer(serializers.Serializer):
    """Serializer for task results."""

    task_id = serializers.CharField(help_text="The ID of the Celery task")
    status = serializers.ChoiceField(
        choices=TASK_STATUSES.CHOICES,
        default=TASK_STATUSES.PENDING,
        help_text="The status of the task (PENDING, SUCCESS, FAILURE, etc.)",
    )
    created_at = serializers.DateTimeField(
        help_text="Timestamp when the task was created"
    )
    updated_at = serializers.DateTimeField(
        help_text="Timestamp when the task status was last updated"
    )
    error = serializers.CharField(
        required=False, allow_blank=True, help_text="Error message if the task failed"
    )
    result = serializers.JSONField(
        required=False, help_text="The result of the task (if completed)"
    )
