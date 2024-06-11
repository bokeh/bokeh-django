# bokeh-django
Support for running Bokeh apps with Django

## Introduction
Both Bokeh and Django are web frameworks that can be used independently to build and host web applications. They each have their own strengths and the purpose of the ``bokeh_django`` package is to integrate these two frameworks so their strengths can be used together. 

## Installation

```commandline
pip install bokeh-django
```

## Configuration

This documentation assumes that you have already started a [Django project](https://docs.djangoproject.com/en/4.2/intro/tutorial01/).

`bokeh-django` enables you to define routes (URLs) in your Django project that will map to Bokeh applications or embed Bokeh applications into a template rendered by Django. However, before defining the routes there are several configuration steps that need to be completed first.

1. Configure ``INSTALLED_APPS``:

    In the ``settings.py`` file ensure that both ``channels`` and ``bokeh_django`` are added to the ``INSTALLED_APPS`` list:

    ```python
    INSTALLED_APPS = [
        ...,
        'channels',
        'bokeh_django',
    ]
    ```

2. Set Up an ASGI Application:

    By default, the Django project will be configured to use a WSGI application, but the ``startproject`` command should have also created an ``asgi.py`` file.

    In ``settings.py`` change the ``WSGI_APPLICATION`` setting to ``ASGI_APPLICATION`` and modify the path accordingly. It should look something like this:

    ```python
    ASGI_APPLICATION = 'mysite.asgi.application'
    ```
   
    Next, modify the contents of the ``asgi.py`` file to get the URL patterns from the ``bokeh_django`` app config. Something similar to this will work:

    ```python
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from django.apps import apps
   
    bokeh_app_config = apps.get_app_config('bokeh_django')
   
    application = ProtocolTypeRouter({
       'websocket': AuthMiddlewareStack(URLRouter(bokeh_app_config.routes.get_websocket_urlpatterns())),
       'http': AuthMiddlewareStack(URLRouter(bokeh_app_config.routes.get_http_urlpatterns())),
    })
    ```

3. Configure Static Files:

    Both Bokeh and Django have several ways of configuring serving static resources. This documentation will describe several possible configuration approaches.
   
    The Bokeh [``resources`` setting](https://docs.bokeh.org/en/latest/docs/reference/settings.html#resources) can be set to one of several values (e.g ``server``, ``inline``, ``cdn``), the default is ``cdn``. If this setting is set to ``inline``, or ``cdn`` then Bokeh resources will be served independently of Django resources. However, if the Bokeh ``resources`` setting is set to ``server``, then the Bokeh resources are served up by the Django server in the same way that the Django static resources are and so Django must be configured to be able to find the Bokeh resources.
   
    To specify the Bokeh ``resources`` setting add the following to the Django ``settings.py`` file:
   
    ```python
    from bokeh.settings import settings as bokeh_settings
   
    bokeh_settings.resources = 'server'
    ```
   
    If the Bokeh ``resources`` setting is set to ``server`` then we must add the location of the Bokeh resources to the ``STATICFILES_DIRS`` setting:
   
    ```python
    from bokeh.settings import settings as bokeh_settings
   
    try:
        bokeh_js_dir = bokeh_settings.bokehjs_path()
    except AttributeError:
        # support bokeh versions < 3.4
        bokeh_js_dir = bokeh_settings.bokehjsdir()
   
    STATICFILES_DIRS = [
        ...,
        bokeh_js_dir,
    ]
    ```
   
    Django can be configured to automatically find and collect static files using the [``staticfiles`` app](https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/), or the static file URL patterns can be explicitly added to the list of ``urlpatterns`` in the ``urls.py`` file. 
   
    To explicitly add the static file ``urlpatterns`` add the following to the ``urls.py`` file:
   
    ```python
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from bokeh_django import static_extensions
   
    urlpatterns = [
        ...,
        *static_extensions(),
        *staticfiles_urlpatterns(),
    ]
    ```

    Be sure that the ``static_extensions`` are listed before the ``staticfiles_urlpatterns``.

    Alternatively, you can configure the [``staticfiles`` app](https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/) by adding ``'django.contrib.staticfiles',`` to ``INSTALLED_APPS``:

    ```python
    INSTALLED_APPS = [
        ...,
        'django.contrib.staticfiles',
        'channels',
        'bokeh_django',
    ]
    ```
   
    Next add ``bokeh_django.static.BokehExtensionFinder`` to the ``STATICFILES_FINDERS`` setting. The default value for ``STATICFILES_FINDERS`` has two items. If you override the default by adding the ``STATICFILES_FINDERS`` setting to your ``settings.py`` file, then be sure to also list the two default values in addition to the ``BokehExtensionFinder``:

    ```python
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        'bokeh_django.static.BokehExtensionFinder',
    )
    ```

## Define Routes

Bokeh applications are integrated into Django through routing or URLs. 
      
In a Django app, the file specified by the ``ROOT_URLCONF`` setting (e.g. ``urls.py``) must define ``urlpatterns`` which is a sequence of ``django.url.path`` and/or ``django.url.re_path`` objects. When integrating a Django app with Bokeh, the ``urls.py`` file must also define ``bokeh_apps`` as a sequence of ``bokeh_django`` routing objects. This should be done using the ``bokeh_djagno.document`` and/or ``bokeh_django.autoload`` functions.

### Document
   
The first way to define a route is to use ``bokeh_django.document``, which defines a route to a Bokeh app (as either a file-path or a function). 

```python
from bokeh_django import document
from .views import my_bokeh_app_function

bokeh_apps = [
    document('url-pattern/', '/path/to/bokeh/app.py'),
    document('another-url-pattern/', my_bokeh_app_function)   
]
```
When using the ``document`` route Django will route the URL directly to the Bokeh app and all the rendering will be handled by Bokeh.

### Directory

An alternative way to create ``document`` routes is to use ``bokeh_django.directory`` to automatically create a ``document`` route for all the bokeh apps found in a directory. In this case the file name will be used as the URL pattern.

```python
from bokeh_django import directory

bokeh_apps = directory('/path/to/bokeh/apps/')
```

### Autoload

To integrate more fully into a Django application routes can be created using ``autoload``. This allows the Bokeh application to be embedded in a template that is rendered by Django. This has the advantage of being able to leverage Django capabilities in the view and the template, but is slightly more involved to set up. There are five components that all need to be configured to work together: the [Bokeh handler](#bokeh-handler), the [Django view](#django-view), the [template](#template), the [Django URL path](#django-url-path), and the [Bokeh URL route](#bokeh-url-route).

#### Bokeh Handler

The handler is a function (or any callable) that accepts a ``bokeh.document.Document`` object and configures it with the Bokeh content that should be embedded. This is done by adding a Bokeh object as the document root:

```python
from bokeh.document import Document
from bokeh.layouts import column
from bokeh.models import Slider

def bokeh_handler(doc: Document) -> None:
 slider = Slider(start=0, end=30, value=0, step=1, title="Example")
 doc.add_root(column(slider))
```

The handler can also embed a Panel object. In this case the document is passed in to the ``server_doc`` method of the Panel object:

```python
import panel as pn
def panel_handler(doc: Document) -> None:
   pn.Row().server_doc(doc)
```

#### Django View

The view is a Django function that accepts a ``request`` object and returns a ``response``. A view that embeds a Bokeh app must create a ``bokeh.embed.server_document`` and pass it in the context to the template when rendering the response.

```python
from bokeh.embed import server_document
from django.shortcuts import render

def view_function(request):
    script = server_document(request.build_absolute_uri())
    return render(request, "embed.html", dict(script=script))
```

#### Template

The template document is a Django HTML template (e.g. ``"embed.html"``) that will be rendered by Django. It can be as complex as desired, but at the very least must render the ``script`` that was passed in from the context:

```html
<!doctype html>
<html lang="en">  
<body>
  {{ script|safe }}
</body>
</html>
```

#### Django URL Path

The [Django URL Path](#django-url-path) is a ``django.url.path`` or ``django.url.re_path`` object that is included in the ``urlpatters`` sequence and that maps a URL pattern to the [Django View](#django-view) as would normally be done with Django.

```python
urlpatterns = [
    path("embedded-bokeh-app/", views.view_function),
]
```

#### Bokeh URL Route

The [Bokeh URL Route](#bokeh-url-route) is a ``bokeh_django.autoload`` object that is included in the ``bokeh_apps`` sequence and that maps a URL pattern to the [Bokeh handler](#bokeh-handler).

```python
from bokeh_django import autoload

bokeh_apps = [
    autoload("embedded-bokeh-app/", views.handler) 
]
```

Note that the URL pattern should be the same URL pattern that was used in the corresponding [Django URL Path](#django-url-path). In reality the URL pattern must match the URL that the ``server_document`` script is configured with in the [Django View](#django-view). Normally, it is easiest to use the URL from the ``request`` object (e.g. ``script = server_document(request.build_absolute_uri())``), which is the URL of the corresponding [Django URL Path](#django-url-path).
