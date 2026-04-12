from django.urls import path
from .views import dashboard_home, user_dashboard, admin_dashboard, dashboard_graphs

urlpatterns = [
    path("", dashboard_home, name="dashboard_home"),
    path("user/", user_dashboard, name="user_dashboard"),
    path("admin/", admin_dashboard, name="admin_dashboard"),
    path("graphs/", dashboard_graphs, name="dashboard_graphs"),
]