""":mod:`content_negotiation`
=============================

Provides better content-negotiation for flask.
"""
from flask import Response, request, abort

from renderers import TemplateRenderer
from media_type import acceptable_media_types, best_renderer

__all__ = ('Render', 'MediaType', 'provides')


class Render(object):
    """Dynamic function class renders content.
    """
    def __init__(self, renderers=(TemplateRenderer(), )):
        super(Render, self).__init__()
        self.renderers = renderers

    def __call__(self, data, template=None, status=200, headers=None,
                 renderers=None, ctx=None):
        """Render `_data` to response.

        :param data: rendering target.
        :param template: path for jinja template '.html' can be ommited.
        :param status: status code for HTTP response.
        :param headers: additional header informations.
        :param renderers: list of renderer will be used.  :cosnt:`None` to use
            default renderers
        :param ctx: context for template renderer.  defualt is
            `{'data':data}`

        :returns: rendered response
        :rtype: :class:`flask.Response`

        You can use it like::

            from flask.ext.negotiation import render

            @app.route('/')
            def view():
                data = get_data()
                return render(data)

        Or::

            from flask.ext.negotiation import render

            @app.route('/user/<uid>')
            def user_view(uid):
                user = get_user(uid)
                return render(user, 'user/read')

        Or::

            from flask.ext.negotiation import render
            from flask.ext.negotiation import provides

            @app.route('/new_content/')
            @provides(TemplateRenderer, 'application/json')
            def content_view():
                content = create_content()
                return render(content, 'content/read.html', 201, ctx={
                    'content':content,
                    'author':content.author,
                })

        """
        renderers = renderers or self.renderers
        media_types = acceptable_media_types(request)
        renderer, rendered_media_type = best_renderer(renderers, media_types)
        if renderer is None:
            abort(406)
        body = renderer.render(data, template, ctx)
        return Response(body, status, headers, unicode(rendered_media_type),
                        content_type=unicode(rendered_media_type))
