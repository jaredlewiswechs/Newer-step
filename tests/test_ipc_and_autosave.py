from Kernel.demo import server
import asyncio


def test_publish_and_fetch_messages():
    server._ensure_shell()
    # publish a message on channel 'chat'
    r = server._process_manager.publish('chat', {'from': 0, 'message': 'hello'})
    msgs = server._process_manager.fetch_channel('chat')
    assert any(m['message'] == 'hello' for m in msgs)


def test_autosave_on_window_save():
    # Launch notes window process
    class Req:
        async def json(self):
            return {'script': 'shell.open_note_window("AutoNotes")\n', 'title': 'AutoNotesApp'}

    res = asyncio.run(server.shell_launch(Req()))
    pid = res['pid']
    proc = server._process_manager._processes[pid]
    # find window
    wid = proc.windows[0].__repr__()  # ensure exists
    wid = proc.windows[0]
    window_id = id(wid)

    # save via process API wrapper
    ok = proc.runtime.global_scope.get('shell').data.get('set_window_note')
    # call native wrapper (pass TinyTalk Values)
    from realTinyTalk.types import Value as TTValue
    ok.data.native_fn([TTValue.int_val(window_id), TTValue.string_val('Auto'), TTValue.string_val('Autosave test')])

    # check vault entries
    from newton_supercomputer import vault
    owner = proc._owner_id
    entries = vault._owner_index.get(owner, [])
    assert any(isinstance(eid, str) for eid in entries)
