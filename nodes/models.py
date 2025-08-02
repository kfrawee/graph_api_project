from django.db import models


class Node(models.Model):
    """
    A node in the graph.

    Attributes:
        name: Unique name of the node
        created_at: Timestamp when the node was created
        updated_at: Timestamp when the node was last updated
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="The unique name of the node"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nodes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Node: {self.name}>"


class Connection(models.Model):
    """
    A directed connection between two nodes.

    Attributes:
        from_node: The source node of the connection
        to_node: The target node of the connection
        created_at: Timestamp when the connection was created
    """

    from_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="outgoing_connections",
        help_text="The source node of the connection",
    )
    to_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="incoming_connections",
        help_text="The target node of the connection",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "connections"
        unique_together = ("from_node", "to_node")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_node.name} -> {self.to_node.name}"

    def __repr__(self):
        return f"<Connection: {self.from_node.name} -> {self.to_node.name}>"

    def clean(self):
        """Validate that a node cannot connect to itself."""
        from django.core.exceptions import ValidationError

        if self.from_node == self.to_node:
            raise ValidationError("A node cannot connect to itself.")

    def save(self, *args, **kwargs):
        """Override save to call clean method."""
        self.clean()
        super().save(*args, **kwargs)
