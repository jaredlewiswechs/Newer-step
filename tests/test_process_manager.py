from Kernel.demo import server
import asyncio


def test_launch_script_creates_process_and_window():
    # simple script that opens a window via shell.open_window
    script = 'shell.open_window("Scribbles")\n'
    class Req:
        async def json(self):
            return {'script': script, 'title': 'ScriptedApp'}
    res = asyncio.run(server.shell_launch(Req()))
    assert 'pid' in res
    pid = res['pid']

    procs = server._process_manager.list_processes()
    assert any(p['pid'] == pid for p in procs)
    # there should be at least one window owned by the process
    proc = next(p for p in procs if p['pid'] == pid)
    assert len(proc['windows']) >= 1


def test_kill_process():
    script = 'shell.open_window("Temp")\n'
    class Req:
        async def json(self):
            return {'script': script, 'title': 'TempApp'}
    res = asyncio.run(server.shell_launch(Req()))
    pid = res['pid']
    ok = server._process_manager.kill(pid)
    assert ok is True
    procs = server._process_manager.list_processes()
    assert all(p['pid'] != pid for p in procs)
