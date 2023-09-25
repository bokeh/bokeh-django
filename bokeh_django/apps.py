# -----------------------------------------------------------------------------
# Copyright (c) 2012 - 2022, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Boilerplate
# -----------------------------------------------------------------------------
from __future__ import annotations

import logging # isort:skip
log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# Standard library imports
from importlib import import_module
from typing import List

# External imports
from django.apps import AppConfig
from django.conf import settings
from django.urls import URLPattern, URLResolver

# Bokeh imports
from .routing import Routing, RoutingConfiguration

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------

__all__ = (
    'DjangoBokehConfig',
)

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------


class DjangoBokehConfig(AppConfig):

    name = 'bokeh_django'
    label = 'bokeh_django'

    _routes: RoutingConfiguration | None = None

    '''
    @property
    def bokeh_apps(self) -> List[Routing]:
        """
        https://www.fusionbox.com/blog/detail/making-a-django-url-resolver-field-a-case-study/628/
        Think about how to improve this part ???
        """
        module = settings.ROOT_URLCONF
        url_conf = import_module(module) if isinstance(module, str) else module
        return url_conf.bokeh_apps
    '''

    @property
    def bokeh_apps(self) -> List[Routing]:
        """
        https://www.fusionbox.com/blog/detail/making-a-django-url-resolver-field-a-case-study/628/
        Think about how to improve this part ???
        """
        bokeh_apps = [ ]
        module = settings.ROOT_URLCONF
        url_conf = import_module(module) if isinstance(module, str) else module
        if hasattr(url_conf, 'bokeh_apps'):
            bokeh_apps.extend(url_conf.bokeh_apps)
        for p in url_conf.urlpatterns:
            if isinstance(p, (URLResolver)):
                if hasattr(p, 'bokeh_apps'):
                    bokeh_apps.extend(p.bokeh_apps)
        return bokeh_apps

    @property
    def routes(self) -> RoutingConfiguration:
        if self._routes is None:
            self._routes = RoutingConfiguration(self.bokeh_apps)
        return self._routes

# -----------------------------------------------------------------------------
# Dev API
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private API
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------
