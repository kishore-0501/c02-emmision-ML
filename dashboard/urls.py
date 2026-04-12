from django.urls import path
from .views import dashboard_home, dashboard_graphs

urlpatterns = [
    path("", dashboard_home, name="dashboard_home"),
    path("graphs/", dashboard_graphs, name="dashboard_graphs"),
]