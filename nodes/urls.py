from django.urls import path

from . import views

app_name = "nodes"

urlpatterns = [
    # Health check
    path("health/", views.health_check, name="health_check"),
    # Node operations
    path("nodes/create/", views.create_node, name="create_node"),
    path("nodes/", views.list_nodes, name="list_nodes"),
    # Connection operations
    path("nodes/connect/", views.connect_nodes, name="connect_nodes"),
    # Path finding operations
    path("path/find/", views.find_path, name="find_path"),
    path("path/slow-find/", views.slow_find_path, name="slow_find_path"),
    path(
        "path/result/<str:task_id>/",
        views.get_slow_path_result,
        name="get_slow_path_result",
    ),
]
