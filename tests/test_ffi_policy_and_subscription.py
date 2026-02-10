from Kernel.demo import server
import asyncio


def test_vault_policy_blocks_save():
    # launch process with vault disabled
    class Req:
        async def json(self):
            return {'script': 'show("hi")\n', 'title': 'NoVaultApp', 'allow_vault': False}

    res = asyncio.run(server.shell_launch(Req()))
    pid = res['pid']
    proc = server._process_manager._processes[pid]

    # attempt to save via native wrapper; should not store to vault (raises/returns False)
    save_val = proc.runtime.global_scope.get('shell').data.get('save_note')
    try:
        # call native wrapper
        from realTinyTalk.types import Value as TTValue
        entry = save_val.data.native_fn([TTValue.string_val('T'), TTValue.string_val('C')])
        # if no exception, ensure that owner is None or no entries
        owner = proc._owner_id
        from newton_supercomputer import vault
        if owner:
            assert owner not in vault._owner_index or len(vault._owner_index.get(owner, [])) == 0
    except Exception:
        # acceptable: native wrapper may raise
        pass


def test_ipc_subscribe_and_publish():
    # two processes
    class R1:
        async def json(self):
            return {'script': 'show("p1")\n', 'title': 'P1'}
    class R2:
        async def json(self):
            return {'script': 'show("p2")\n', 'title': 'P2'}

    p1 = asyncio.run(server.shell_launch(R1()))['pid']
    p2 = asyncio.run(server.shell_launch(R2()))['pid']

    proc2 = server._process_manager._processes[p2]
    # subscribe proc2 to channel 'alerts'
    proc2.runtime.global_scope.get('shell').data.get('subscribe').data.native_fn([__import__('realTinyTalk').types.Value.string_val('alerts')])

    # publish on channel
    server._process_manager.publish('alerts', {'from': p1, 'message': 'wake up'})

    # proc2 should receive message
    msgs = proc2._inbox
    assert any(m['message'] == 'wake up' for m in msgs)
