""":mod:`decorators` --- Decorators for Flask views
===================================================
"""
from flask import request
from functools import wraps
from renderers import Renderer
from media_type import acceptable_media_types, MediaType, can_accept
from werkzeug.exceptions import NotAcceptable

def provides(media_type, *args):
    """Decorator that recognizes acceptablility of view function.  
    For example::   

        from flask.ext.negotiation.decorators import provides

        @app.route('/json_only')
        @provides('application/json')
        def json_only():
            return json.dumps({'text':'JSON Mraz'})

    And you can provide multiple types like this::  

        from flask.ext.negotiation.decorators import provides

        @app.route('/json_and_html')
        @provides('text/html', 'application/json')
        def json_and_html():
            data = get_data()
            return render(data)

    Or you can use renderer::

        from flask.ext.negotiation.renderes import TemplateRenderer
        from flask.ext.negotiation.decorators import provides

        @app.route('/json_and_html')
        @provides(TemplateRenderer, 'application/json')
        def json_and_html():
            data = get_data()
            return render(data)
    """
    # Collect media types
    media_types = []
    for media_type in (media_type, ) + args:
        if isinstance(media_type, MediaType):
            media_types.append(media_type)
        elif isinstance(media_type, type) and issubclass(media_type, Renderer):
            media_types += map(MediaType, media_type.__media_types__)
        else:
            media_types.append(MediaType(media_type))
    # Decorator here
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            acceptables = acceptable_media_types(request)
            if can_accept(acceptables, media_types):
                return fn(*args, **kwargs)
            raise NotAcceptable()
        return wrapper
    return decorator
