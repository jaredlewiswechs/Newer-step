from Kernel.demo import server
import asyncio


def test_notes_window_render_and_update():
    # Launch a process and create a notes window via the process API
    class Req:
        async def json(self):
            # script uses shell.open_note_window to ensure a NotesView is created
            return {'script': 'shell.open_note_window("MyNotes")\n', 'title': 'NotesWinApp'}

    res = asyncio.run(server.shell_launch(Req()))
    pid = res['pid']
    procs = server._process_manager.list_processes()
    proc = next(p for p in procs if p['pid'] == pid)
    # find window
    assert len(proc['windows']) >= 1
    window_id = proc['windows'][0]['id']

    # update window content via window save endpoint
    class SaveReq:
        async def json(self):
            return {'pid': pid, 'window_id': window_id, 'title': 'Hello', 'content': 'This is a note.'}

    res2 = asyncio.run(server.shell_notes_window_save(SaveReq()))
    assert res2['ok'] is True

    # retrieve the window content
    class GetReq:
        async def json(self):
            return {'pid': pid, 'window_id': window_id}

    got = asyncio.run(server.shell_notes_window_get(GetReq()))
    assert got['title'] == 'Hello'
    assert got['content'].startswith('This is a note.')

    # verify SVG contains the note
    shell = server._ensure_shell()
    svg = shell.render_to_svg()
    assert 'This is a note' in svg
