from Kernel.demo import server
import asyncio


def test_overlay_flow_save_and_render():
    # Launch a notes window process
    class Req:
        async def json(self):
            return {'script': 'shell.open_note_window("OverlayNotes")\n', 'title': 'OverlayNotesApp'}

    res = asyncio.run(server.shell_launch(Req()))
    pid = res['pid']
    proc = server._process_manager._processes[pid]
    window_id = id(proc.windows[0])

    # Simulate overlay save
    class SaveReq:
        async def json(self):
            return {'pid': pid, 'window_id': window_id, 'title': 'Overlay', 'content': 'Edited in overlay.'}

    out = asyncio.run(server.shell_notes_window_save(SaveReq()))
    assert out['ok'] is True

    # Verify window get returns updated content
    class GetReq:
        async def json(self):
            return {'pid': pid, 'window_id': window_id}

    got = asyncio.run(server.shell_notes_window_get(GetReq()))
    assert got['title'] == 'Overlay'
    assert 'Edited in overlay' in got['content']

    # Ensure SVG contains updated text
    shell = server._ensure_shell()
    svg = shell.render_to_svg()
    assert 'Edited in overlay' in svg
