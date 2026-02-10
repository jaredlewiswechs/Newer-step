from Kernel.demo import server
import asyncio


def test_install_and_list_app():
    # install an app via endpoint
    class Req:
        async def json(self):
            return {'name': 'helloapp', 'manifest': {'name': 'helloapp', 'entry': 'main.tt'}, 'script': 'show("hello")\n'}

    res = asyncio.run(server.shell_apps_install(Req()))
    assert res['installed'] is True

    apps = server.shell_apps()
    assert any(a.get('name') == 'helloapp' for a in apps['installed'])

    # uninstall
    class UR:
        async def json(self):
            return {'name': 'helloapp'}

    r2 = asyncio.run(server.shell_apps_uninstall(UR()))
    assert r2['uninstalled'] is True
