""":mod:`content_negotiation.renderers`
=======================================

Renderers
"""
from abc import ABCMeta, abstractmethod
from flask import render_template
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
        return not all(x not in media_type for x in self.media_types)

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

    @classmethod
    def default_template(cls):
        return ''

    def render(self, data, template=None, ctx=None):
        template = template or ''
        if not template.endswith('.html'):
            template += '.html'
        ctx = ctx or {
            'data':data
        }
        return render_template(template, **ctx)
