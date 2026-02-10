from Kernel.demo import server
import asyncio


def test_tinytalk_save_and_load_note():
    server._ensure_shell()
    # create a tinyTalk script that saves and loads a note
    script = '''
shell.open_window("Notes")
entry = shell.save_note("TestNote", "Hello from TinyTalk")
ret = shell.load_note(entry)
show(ret)
'''

    class Req:
        async def json(self):
            return {'script': script, 'title': 'NotesApp'}

    res = asyncio.run(server.shell_launch(Req()))
    assert 'pid' in res
    pid = res['pid']
    procs = server._process_manager.list_processes()
    proc = next(p for p in procs if p['pid'] == pid)
    assert proc['title'] == 'NotesApp'
    # there's at least one window opened
    assert len(proc['windows']) >= 1

    # Find the entry id by scanning vault entries for owner
    from newton_supercomputer import vault
    proc_obj = next(p for p in server._process_manager._processes.values() if p.pid == pid)
    owner = proc_obj._owner_id
    assert owner is not None
    entries = vault._owner_index.get(owner, [])
    assert len(entries) >= 1
    entry_id = entries[-1]
    data = vault.retrieve(owner, entry_id)
    assert isinstance(data, dict)
    assert data['title'] == 'TestNote'
    assert data['content'] == 'Hello from TinyTalk'