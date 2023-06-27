# Bokeh imports
from bokeh.util.dependencies import import_required

# Bokeh imports
from .apps import DjangoBokehConfig
from .consumers import AutoloadJsConsumer, WSConsumer
from .routing import autoload, directory, document
from .static import static_extensions

import_required("django", "django is required by bokeh-django")
import_required("channels", "The package channels is required by bokeh-django and must be installed")


def with_request(f):
    def wrapper(doc):
        return f(doc, doc.session_context.request)
    return wrapper


def with_url_args(handler):
    def wrapper(doc):
        request = doc.session_context.request
        args = request.url_route['args']
        kwargs = request.url_route['kwargs']
        return handler(doc, *args, **kwargs)

    return wrapper
