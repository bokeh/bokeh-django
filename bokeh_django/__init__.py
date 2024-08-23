import inspect

# Bokeh imports
from bokeh.util.dependencies import import_required

# Bokeh imports
from .apps import DjangoBokehConfig
from .consumers import AutoloadJsConsumer, WSConsumer
from .routing import autoload, directory, document
from .static import static_extensions

import_required("django", "django is required by bokeh-django")
import_required("channels", "The package channels is required by bokeh-django and must be installed")


def with_request(handler):
    # Note that functools.wraps cannot be used here because Bokeh requires that the signature of the returned function
    # must only accept single (Document) argument
    def wrapper(doc):
        return handler(doc, doc.session_context.request)

    async def async_wrapper(doc):
        return await handler(doc, doc.session_context.request)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper


def _get_args_kwargs_from_doc(doc):
    request = doc.session_context.request
    args = request.url_route['args']
    kwargs = request.url_route['kwargs']
    return args, kwargs


def with_url_args(handler):
    # Note that functools.wraps cannot be used here because Bokeh requires that the signature of the returned function
    # must only accept single (Document) argument
    def wrapper(doc):
        args, kwargs = _get_args_kwargs_from_doc(doc)
        return handler(doc, *args, **kwargs)

    async def async_wrapper(doc):
        args, kwargs = _get_args_kwargs_from_doc(doc)
        return await handler(doc, *args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper
