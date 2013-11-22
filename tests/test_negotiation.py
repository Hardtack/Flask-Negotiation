import os
import json

import pytest
from flask import Flask

from flask_negotiation import provides, Render
from flask_negotiation.media_type import MediaType, can_accept
from flask_negotiation.renderers import (renderer, template_renderer,
                                         json_renderer, TemplateRenderer)


@pytest.fixture
def app():
    def teardown():
        ctx.pop()
    app = Flask(__name__)
    ctx = app.test_request_context()
    ctx.push()
    return app


def test_renderer(app, tmpdir):
    # Template renderer
    app.template_folder = str(tmpdir)
    template = '''
    <html><body>{{ data['key'] }}</body></html>
    '''.strip()
    template_name = 'test.html'
    with open(os.path.join(app.template_folder, template_name), 'w') as f:
        f.write(template)

    data = {'key': 'value'}

    rendered = template_renderer.render(data, 'test.html')
    assert '<html><body>value</body></html>' == rendered

    # Custom extension
    template_renderer2 = TemplateRenderer(ext='tpl')
    template = '''
    <html><body><div>{{ data['key'] }}</div></body></html>
    '''.strip()
    template_name = 'test.tpl'
    with open(os.path.join(app.template_folder, template_name), 'w') as f:
        f.write(template)
    rendered = template_renderer2.render(data, 'test')
    assert '<html><body><div>value</div></body></html>' == rendered

    # JSON Renderer

    rendered = json_renderer.render(data)
    assert data == json.loads(rendered)

    # Create Custom renderer
    @renderer('application/json')
    def custom_renderer(data, template=None, ctx=None):
        return json.dumps({'data': data})

    rendered = custom_renderer.render(data)
    assert data == json.loads(rendered)['data']


def test_render(app, tmpdir):
    app.template_folder = str(tmpdir)
    template = '''
    <html><body>{{ data['key'] }}</body></html>
    '''.strip()
    template_name = 'test.html'
    with open(os.path.join(app.template_folder, template_name), 'w') as f:
        f.write(template)
    client = app.test_client()

    # Render function
    render = Render(renderers=[template_renderer, json_renderer])

    @app.route('/render')
    def first():
        return render({'key': 'value'}, 'test')

    @app.route('/status')
    @provides('application/json')
    def second():
        return render(None, 'test', 204)

    headers = {
        'Accept': 'application/json'
    }
    rv = client.get('/render', headers=headers)
    assert 200 == rv.status_code
    assert {'key': 'value'} == json.loads(rv.data)

    headers = {
        'Accept': 'text/html'
    }
    rv = client.get('/render', headers=headers)
    assert 200 == rv.status_code
    assert '<html><body>value</body></html>' == rv.data

    headers = {
        'Accept': 'application/json; q=0.7, text/html; q=0.8'
    }
    rv = client.get('/render', headers=headers)
    assert 200 == rv.status_code
    assert '<html><body>value</body></html>' == rv.data

    headers = {
        'Accept': 'application/json; q=0.7, text/html; q=0.8'
    }
    rv = client.get('/status', headers=headers)
    assert 204 == rv.status_code


def test_provides(app):
    client = app.test_client()

    @app.route('/1')
    @provides('application/json')
    def first():
        return '{"message": "Hi"}'

    @app.route('/2')
    @provides('application/json', 'text/html')
    def second():
        return 'Done'

    @app.route('/3')
    @provides(template_renderer)
    def third():
        return 'OK'

    @app.route('/4')
    @provides(MediaType('application/json'))
    def fourth():
        return 'Right'

    @app.route('/5')
    @provides('text/*', 'application/json', to='provide_type')
    def fifth(provide_type):
        return str(provide_type)

    # 1
    headers = {
        'Accept': 'application/json'
    }
    assert 200 == client.get('/1', headers=headers).status_code

    headers = {
        'Accept': 'text/html'
    }
    assert 406 == client.get('/1', headers=headers).status_code

    # 2
    headers = {
        'Accept': 'text/html'
    }
    assert 200 == client.get('/2', headers=headers).status_code

    headers = {
        'Accept': 'application/json'
    }
    assert 200 == client.get('/2', headers=headers).status_code

    headers = {
        'Accept': 'image/jpeg'
    }
    assert 406 == client.get('/2', headers=headers).status_code

    # 3
    headers = {
        'Accept': 'text/html, application/json'
    }
    assert 200 == client.get('/3', headers=headers).status_code

    headers = {
        'Accept': 'application/json'
    }
    assert 406 == client.get('/3', headers=headers).status_code

    # 4
    headers = {
        'Accept': 'application/json'
    }
    assert 200 == client.get('/4', headers=headers).status_code

    # 5
    headers = {
        'Accept': 'application/json'
    }
    assert 'application/json' == client.get('/5', headers=headers).data

    headers = {
        'Accept': 'text/html'
    }
    assert 'text/html' == client.get('/5', headers=headers).data


def test_media_type():
    application_json_type = MediaType('application/json')
    application_type = MediaType('application/*')
    assert application_json_type in application_type

    json_type = MediaType('*/json')
    assert application_json_type in json_type

    image_type = MediaType('image/*')
    assert not application_json_type in image_type

    assert application_json_type == MediaType('application/json')


def test_media_order():
    image_type = MediaType('image/jpeg')
    html_type = MediaType('text/html; q=0.9')
    json_type = MediaType('application/json; q=0.8')
    li = [html_type, json_type, image_type]
    assert [json_type, html_type, image_type] == sorted(li)


def test_acceptablility():
    # Single
    media_types = map(MediaType, ['application/json'])
    acceptables = map(MediaType, ['application/json'])
    assert can_accept(acceptables, media_types)

    # Wildcard
    media_types = map(MediaType, ['*/*'])
    acceptables = map(MediaType, ['application/json'])
    assert can_accept(acceptables, media_types)

    # Partitial wildcard
    media_types = map(MediaType, ['text/*'])
    acceptables = map(MediaType, ['application/json'])
    assert not can_accept(acceptables, media_types)

    acceptables = map(MediaType, ['text/html'])
    assert can_accept(acceptables, media_types)

    # Multiple acceptables
    media_types = map(MediaType, ['text/html'])
    acceptables = map(MediaType, ['application/json', 'text/html'])
    assert can_accept(acceptables, media_types)

    media_types = map(MediaType, ['image/jpeg'])
    acceptables = map(MediaType, ['application/json', 'text/html'])
    assert not can_accept(acceptables, media_types)

    # Multiple media types
    media_types = map(MediaType, ['text/*', 'application/json'])
    acceptables = map(MediaType, ['application/json'])
    assert can_accept(acceptables, media_types)
    acceptables = map(MediaType, ['text/html'])
    assert can_accept(acceptables, media_types)

    acceptables = map(MediaType, ['image/jpeg'])
    assert not can_accept(acceptables, media_types)

    # Multiple both
    media_types = map(MediaType, ['text/html', 'application/*'])
    acceptables = map(MediaType, ['application/json', 'image/jpeg'])
    assert can_accept(acceptables, media_types)

    media_types = map(MediaType, ['text/html', 'application/*'])
    acceptables = map(MediaType, ['image/png', 'image/jpeg'])
    assert not can_accept(acceptables, media_types)
