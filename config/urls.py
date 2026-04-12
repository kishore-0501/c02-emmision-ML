from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    return redirect("dashboard_home")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_redirect, name="root"),
    path("users/", include("users.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("shipments/", include("shipments.urls")),
    path("predictions/", include("predictions.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)