from Kernel.demo import server
import asyncio


def test_notes_save_list_load_flow():
    # Launch a notes app process using the example script
    class Req:
        async def json(self):
            import json
            from pathlib import Path
            script = Path('realTinyTalk/examples/notes_app.tt').read_text(encoding='utf-8')
            return {'script': script, 'title': 'NotesUI'}

    res = asyncio.run(server.shell_launch(Req()))
    assert 'pid' in res
    pid = res['pid']

    # Save a note via API
    class SaveReq:
        async def json(self):
            return {'pid': pid, 'title': 'UI Note', 'content': 'Saved via UI endpoints'}

    save = asyncio.run(server.shell_save_note(SaveReq()))
    assert 'entry_id' in save
    eid = save['entry_id']

    # List notes
    lst = server.shell_notes_list(pid)
    assert any(n['id'] == eid for n in lst['notes'])

    # Load note
    class LoadReq:
        async def json(self):
            return {'pid': pid, 'entry_id': eid}

    loaded = asyncio.run(server.shell_load_note(LoadReq()))
    assert 'entry' in loaded
    assert loaded['entry']['content'] == 'Saved via UI endpoints'