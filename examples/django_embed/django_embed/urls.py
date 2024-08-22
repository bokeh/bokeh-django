"""django_embed URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from bokeh_django import autoload, directory, document, static_extensions

from . import views


urlpatterns = [
    path(r"", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("sea-surface-temp", views.sea_surface),
    path("my-sea-surface", views.sea_surface_custom_uri),
    path("shapes", views.shapes),
    path("shapes/<str:arg1>/<str:arg2>", views.shapes_with_args),
    # *static_extensions(),
    # *staticfiles_urlpatterns(),
]

base_path = settings.BASE_DIR
apps_path = base_path / "bokeh_apps"

bokeh_apps = [
    *directory(apps_path),
    document("sea_surface_direct", views.sea_surface_handler),
    document("sea_surface_with_template", views.sea_surface_handler_with_template),
    document("sea_surface_bokeh", apps_path / "sea_surface.py"),
    document("shape_viewer", views.shape_viewer_handler),
    autoload("sea-surface-temp", views.sea_surface_handler),
    autoload("sea_surface_custom_uri", views.sea_surface_handler),
    autoload("shapes", views.shape_viewer_handler),
    autoload(r"shapes/(?P<arg1>[\w_\-]+)/(?P<arg2>[\w_\-]+)", views.shape_viewer_handler_with_args),
]
