# Bokeh imports
from bokeh.util.dependencies import import_required

# Bokeh imports
from .apps import DjangoBokehConfig
from .consumers import AutoloadJsConsumer, WSConsumer
from .routing import autoload, directory, document
from .static import static_extensions

import_required("django", "django is required by bokeh-django")
import_required("channels", "The package channels is required by bokeh-django and must be installed")
