""":mod:`decorators` --- Decorators for Flask views
===================================================
"""
from flask import request
from functools import wraps
from renderers import Renderer
from media_type import acceptable_media_types, MediaType, choose_media_type
from werkzeug.exceptions import NotAcceptable

def provides(media_type, *args, **kwargs):
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

        from flask.ext.negotiation.renderes import template_renderer
        from flask.ext.negotiation.decorators import provides

        @app.route('/json_and_html')
        @provides(template_renderer, 'application/json')
        def json_and_html():
            data = get_data()
            return render(data)

    And you can handle choosen media type::

        from flask.ext.negotiation.decorators import provides
        @provides('application/json', 'text/html', to='provide_type')
        def handle_type(provide_type):
            return str(provide_type)

    `to` does *not* guarantee same media type with `render` function.  
    """
    to = kwargs.get('to', None)
    # Collect media types
    media_types = []
    for media_type in (media_type, ) + args:
        if isinstance(media_type, MediaType):
            media_types.append(media_type)
        elif isinstance(media_type, type) and issubclass(media_type, Renderer):
            media_types += map(MediaType, media_type.__media_types__)
        elif isinstance(media_type, Renderer):
            media_types += media_type.media_types
        else:
            media_types.append(MediaType(media_type))
    # Decorator here
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            acceptables = acceptable_media_types(request)
            acceptable = choose_media_type(acceptables, media_types)
            if acceptable is None:
                raise NotAcceptable()
            if not to is None:
                kwargs.update({to:acceptable})
            return fn(*args, **kwargs)
        return wrapper
    return decorator
