import pytest
from flask import Flask
from media_type import MediaType, can_accept
from renderers import Renderer, TemplateRenderer
from . import provides

@pytest.fixture
def app():
    def teardown():
        ctx.pop()
    app = Flask(__name__)
    ctx = app.test_request_context()
    ctx.push()
    return app

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
    @provides(TemplateRenderer)
    def third():
        return 'OK'

    @app.route('/4')
    @provides(MediaType('application/json'))
    def fourth():
        return 'Right'

    # 1
    headers = {
        'Accept':'application/json'
    }
    assert client.get('/1', headers=headers).status_code == 200

    headers = {
        'Accept':'text/html'
    }
    assert client.get('/1', headers=headers).status_code == 406

    # 2
    headers = {
        'Accept':'text/html'
    }
    assert client.get('/2', headers=headers).status_code == 200

    headers = {
        'Accept':'application/json'
    }
    assert client.get('/2', headers=headers).status_code == 200

    headers = {
        'Accept':'image/jpeg'
    }
    assert client.get('/2', headers=headers).status_code == 406

    # 3
    headers = {
        'Accept':'text/html, application/json'
    }
    assert client.get('/3', headers=headers).status_code == 200

    headers = {
        'Accept':'application/json'
    }
    assert client.get('/3', headers=headers).status_code == 406

    # 4
    headers = {
        'Accept':'application/json'
    }
    assert client.get('/4', headers=headers).status_code == 200


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
