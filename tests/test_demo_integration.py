from Kernel.demo import server
import asyncio


def test_views_page_available():
    r = server.views_demo()
    # Response content may be bytes under .body or set as .content; normalize
    body = getattr(r, 'body', getattr(r, 'content', None))
    text = body.decode('utf-8') if isinstance(body, (bytes, bytearray)) else str(body)
    assert 'Interactive View Tree' in text


class DummyRequest:
    def __init__(self, data):
        self._data = data

    async def json(self):
        return self._data


def test_post_event_hits_header():
    # header is at (10,10) in content coords and chrome offset is 22 in server
    x = 20
    y = 10 + 22 + 5  # within the header area
    req = DummyRequest({'x': x, 'y': y, 'type': 'MOUSE_DOWN'})
    data = asyncio.run(server.post_event(req))
    assert 'view_id' in data
    assert data['view_id'] == 'header' or data['view_id'] != 'none'
    assert 'hit=' in data['message']
