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
import os
import re

# External imports
from django.http import Http404
from django.urls import re_path
from django.views import static
from django.contrib.staticfiles.finders import BaseFinder
from django.utils._os import safe_join

# Bokeh imports
from bokeh.embed.bundle import extension_dirs

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------

class BokehExtensionFinder(BaseFinder):
    """
    A custom staticfiles finder class to find bokeh resources.

    In Django settings:
        When using `django.contrib.staticfiles' in `INSTALLED_APPS` then add
        `bokeh_django.static.BokehExtensionFinder` to `STATICFILES_FINDERS`
    """
    _root = extension_dirs
    _prefix = 'extensions/'

    def find(self, path, all=False):
        """
        Given a relative file path, find an absolute file path.

        If the ``all`` parameter is False (default) return only the first found
        file path; if True, return a list of all found files paths.
        """
        matches = []
        location = self.find_location(path, self._prefix)
        if location:
            if not all:
                return location
            else:
                matches.append(location)

        return matches

    @classmethod
    def find_location(cls, path, prefix=None, as_components=False):
        """
        Find the absolute path to a resouces given a relative path.

        Args:
            path (str): relative path to resource
            prefix (str): if passed then verifies that path starts with `prefix` else returns `None`
            as_components (bool): If `True` return tuple of (artifacts_dir, artifact_path) rather than absolute path.
                Used when needing seperate components for `static.serve` function to manually serve resources.
        """
        prefix = prefix or ''
        if not prefix or path.startswith(prefix):
            path = path[len(prefix):]
            try:
                name, artifact_path = path.split(os.sep, 1)
            except ValueError:
                pass
            else:
                artifacts_dir = cls._root.get(name, None)
                if artifacts_dir is not None:
                    path = safe_join(artifacts_dir, artifact_path)
                    if os.path.exists(path):
                        if as_components:
                            return artifacts_dir, artifact_path
                        return path


def serve_extensions(request, path):
    components = BokehExtensionFinder.find_location(path, as_components=True)
    if components is not None:
        artifacts_dir, artifact_path = components
        return static.serve(request, artifact_path, document_root=artifacts_dir)
    else:
        raise Http404


def static_extensions(prefix: str = "/static/extensions/"):
    return [re_path(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), serve_extensions)]

# -----------------------------------------------------------------------------
# Dev API
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private API
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------
