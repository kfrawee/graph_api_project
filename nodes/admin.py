from django.contrib import admin

from .models import Connection, Node


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    """Admin interface for Node model."""

    list_display = ["name", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["name"]


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    """Admin interface for Connection model."""

    list_display = ["from_node", "to_node", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["from_node__name", "to_node__name"]
    readonly_fields = ["created_at"]
    ordering = ["from_node__name", "to_node__name"]

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("from_node", "to_node")
