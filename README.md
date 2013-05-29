Flask-Negotiation
=================

Better content-negotiation for flask.  

Install
-------

Install with distutil

    python setup.py install

Usage
-----

Make an app

    from flask import Flask
    from flask.ext.negotiation import provides

    app = Flask(__name__)

Make route that provides json only

    @app.route('/json')
    @provides('application/json')
    def view():
        return '{"message": "Hi"}'

If request is not acceptable, then it returns HTTP 406 (Not Acceptable)

And you can render data

    from flask.ext.negotiation import Render
    from flask.ext.negotiation.renderers import Renderer, TemplateRenderer

    class JSONRenderer(TemplateRenderer):
        __media_types__ = ('application/json', )

        def render(self, data, template=None, ctx=None):
            return json.dumps(data)
    render = Render(renderers=[TemplateRenderer, JSONRenderer])

    @app.route('/render')
    def render():
        data = get_data()
        ...
        return render(data, 'data/show.html')

It automatically choose renderer by `Accept` HTTP Field, and render to 
:class:`~flask.Response` object.  
