from os.path import join
from typing import Any
from bokeh_django import with_request, with_url_args

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.themes import Theme
import panel as pn

from .shape_viewer import shape_viewer

theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', {})


def shape_viewer_handler(doc: Document) -> None:
    panel = shape_viewer()
    panel.server_doc(doc)


@with_url_args
async def shape_viewer_handler_with_args(doc, arg1, arg2):
    viewer = shape_viewer()
    pn.Column(
        viewer,
        pn.pane.Markdown(f'## This app has URL Args: {arg1} and {arg2}')
    ).server_doc(doc)


async def sea_surface_handler(doc: Document) -> None:
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line("time", "temperature", source=source)

    def callback(attr: str, old: Any, new: Any) -> None:
        if new == 0:
            data = df
        else:
            data = df.rolling(f"{new}D").mean()
        source.data = dict(ColumnDataSource(data=data).data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    doc.theme = theme
    doc.add_root(column(slider, plot))


@with_request
async def sea_surface_handler_with_template(doc: Document, request: Any) -> None:
    await sea_surface_handler(doc)
    doc.template = """
{% block title %}Embedding a Bokeh Apps In Django{% endblock %}
{% block preamble %}
<style>
.bold { font-weight: bold; }
</style>
{% endblock %}
{% block contents %}
    <div>
    This Bokeh app below is served by a <span class="bold">Django</span> server for {{ username }}:
    </div>
    {{ super() }}
{% endblock %}
    """
    doc.template_variables["username"] = request.user


async def sea_surface(request: HttpRequest) -> HttpResponse:
    script = server_document(request.get_full_path())
    return render(request, "embed.html", dict(script=script))


def sea_surface_custom_uri(request: HttpRequest) -> HttpResponse:
    script = server_document("/sea_surface_custom_uri")
    return render(request, "embed.html", dict(script=script))


def shapes(request: HttpRequest) -> HttpResponse:
    script = server_document(request.get_full_path())
    return render(request, "embed.html", dict(script=script))


def shapes_with_args(request: HttpRequest, arg1: str, arg2: str) -> HttpResponse:
    script = server_document(request.get_full_path())
    return render(request, "embed.html", dict(script=script))
