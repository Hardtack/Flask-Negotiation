Simple Guide
============

Handle Accept Field
-------------------

You can specify media type that you can provide with 
:func:`~decorators.provides`.  

See an example.

First, create an Flask application::  

    from flask import Flask
    from flask.ext.negotiation import provides

    app = Flask(__name__)

Make route that provides json only::  

    @app.route('/json')
    @provides('application/json')
    def json():
        return '{"message": "Hi"}'

If request is not acceptable, then it returns HTTP 406 (Not Acceptable)

You can also handle media type::  
    
    @app.route('/dynamic')
    @provides('application/json', 'text/html', to='media_type')
    def dynamic(media_type):
        if media_type == 'application/json':
            return '{"message": "Hi"}'
        else:
            return '<html><body>Hi!</body></html>

`provides` will choose best media type can be handled in acceptables and give it
to keyword argument named `to`

Render Contents
---------------

:class:`Render` renders content with renderer choosen by `Accept` HTTP header
field

First, You have to define a renderer:: 

    import json
    from flask.ext.negotiation import Render
    from flask.ext.negotiation.renderer import renderer, template_renderer

    @renderer('application/json')
    def json_renderer(data, template=None, ctx=None):
        return json.dumps(data)

Then create a instance of :class:`Render`:: 

    render = Render(renderers=(template_renderer, json_renderer))

In module defining views import `render`:: 

    from . import app, render

    @app.route('/data/<data_id>')
    def data_view(data_id):
        data = get_data(data_id)
        # Let data = {'data_id':3, 'content':'secret'}

        ...

        return render(data, 'data/view.html')

`data/view.html`'s source is here::

    <html>
      <head>
        <title>The Data Is Here</title>
      </head>
      <body>
        {{ data['content'] }}
      </body>
    </html>

When we send a HTTP request to `/data/3` with `Accept` header field `text/html`
response will be like::
    
    <title>
      <head>
        <title>The Data Is Here</title>
      </head>
      <body>
        secret
      </body>
    </html>

When `Accept` is `application/json`, response will be like:: 

    {"content": "secret", "data_id": 3}
