""":mod:`content_negotiation.renderers`
=======================================

Renderers
"""
import json
from abc import ABCMeta, abstractmethod
from flask import render_template
from functools import wraps
from media_type import MediaType


class Renderer(object):
    """Base renderer class.
    """
    __metaclass__ = ABCMeta

    __media_types__ = ()
    """A collection of supporting media-type :class:`string`s, subclasses must
    redefine this value.
    """

    @property
    def media_types(self):
        """Collections of abstracted media-types.
        """
        return (MediaType(x) for x in self.__media_types__)

    def can_render(self, media_type):
        """Determines that renderer can render `media_type`.
        """
        return not self.choose_media_type(media_type) is None

    def choose_media_type(self, media_type):
        """Chooses media type that will be rendered.
        """
        chosen_type = None
        for renderer_type in self.media_types:
            if media_type in renderer_type:
                chosen_type = renderer_type
        return chosen_type

    @abstractmethod
    def render(self, data, template=None, ctx=None):
        """Renders `data`.

        You must implement it
        """
        pass


class TemplateRenderer(Renderer):
    """Renders object to HTML response.
    """
    __media_types__ = ('text/html', 'application/xhtml+xml')

    def __init__(self, ext='html'):
        super(TemplateRenderer, self).__init__()
        self.ext = ext

    def render(self, data, template=None, ctx=None):
        template = template or ''
        ext = '.' + self.ext
        if not template.endswith(ext):
            template += ext
        ctx = ctx or {
            'data': data
        }
        return render_template(template, **ctx)


class JSONRenderer(Renderer):
    """Renders object to json with JSONEncoder.
    """
    __media_types__ = ('application/json',)

    def __init__(self, encoder=json.JSONEncoder()):
        """:param encoder: encoder to be used with renderer.
        """
        super(JSONRenderer, self).__init__()
        self.encoder = encoder

    def render(self, data, template=None, ctx=None):
        return self.encoder.encode(data)


class FunctionRenderer(Renderer):
    """Renders object with a function.
    """
    def __init__(self, fn, media_types):
        super(FunctionRenderer, self).__init__()
        self.fn = fn
        self.__media_types__ = map(unicode, media_types)

    def render(self, data, template=None, ctx=None):
        return self.fn(data, template=template, ctx=ctx)

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)


def renderer(*media_types):
    """Decorator that creates simple renderer with function.
    """
    def decorator(fn):
        renderer = wraps(fn)(FunctionRenderer(fn, media_types))
        return renderer
    return decorator

# default_renderers
template_renderer = TemplateRenderer()
json_renderer = JSONRenderer()
