import asyncio
from Kernel.demo import server


class DummyRequest:
    def __init__(self, body):
        self._body = body

    async def json(self):
        return self._body


def test_launch_and_focus():
    shell = server._ensure_shell()
    # clear existing windows and create two known windows
    for w in list(shell.windows):
        shell.close_window(w)
    from Kernel.window.nswindow import NSWindow
    from Kernel.view.nsview import NSRect

    w1 = NSWindow(content_rect=NSRect(60, 80, 360, 260), title='One')
    w2 = NSWindow(content_rect=NSRect(440, 120, 360, 260), title='Two')
    shell.open_window(w1)
    shell.open_window(w2)

    # click in area inside 'Two' (SVG coords: roughly x=500,y=300)
    req = DummyRequest({'x': 500, 'y': 300})
    data = asyncio.run(server.shell_event(req))
    assert 'message' in data

    # ensure the focused window is topmost
    last = shell.windows[-1]
    assert last.title == data.get('title')


def test_close_window():
    shell = server._ensure_shell()
    from Kernel.window.nswindow import NSWindow
    from Kernel.view.nsview import NSRect
    w = NSWindow(content_rect=NSRect(80, 80, 360, 260), title='ToClose')
    shell.open_window(w)
    wid = id(w)

    req = DummyRequest({'id': wid})
    data = asyncio.run(server.shell_close(req))
    assert data['closed'] == wid
