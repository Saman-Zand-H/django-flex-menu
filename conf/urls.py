from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("test", TemplateView(template_name="flex_menu/sidebar.html").as_view())
]
