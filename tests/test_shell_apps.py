from Kernel.demo import server
import asyncio


class DummyRequest:
    def __init__(self, body):
        self._body = body

    async def json(self):
        return self._body


def test_list_apps_and_launch():
    server._ensure_shell()
    assert 'notes' in server._ensure_shell._apps

    # launch notes app
    req = DummyRequest({'app': 'notes', 'title': 'MyNotes'})
    res = asyncio.run(server.shell_launch(req))
    assert res['title'] == 'MyNotes'


def test_snapshot_and_restore():
    shell = server._ensure_shell()
    # take snapshot
    snap = server.shell_snapshot()
    # restore into a fresh shell
    req = DummyRequest(snap)
    res = asyncio.run(server.shell_restore(req))
    assert res['restored'] is True
