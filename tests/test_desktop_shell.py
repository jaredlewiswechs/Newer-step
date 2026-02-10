from nina.desktop_shell import DesktopShell
from Kernel.window.nswindow import NSWindow
from Kernel.view.nsview import NSRect


def test_open_and_focus_window():
    shell = DesktopShell(width=800, height=600)
    w1 = NSWindow(content_rect=NSRect(50, 50, 300, 200), title="First")
    w2 = NSWindow(content_rect=NSRect(200, 120, 300, 200), title="Second")

    shell.open_window(w1)
    shell.open_window(w2)

    assert shell.windows[-1] is w2
    # focusing w1 should bring it to front
    shell.focus_window(w1)
    assert shell.windows[-1] is w1


def test_snapshot_and_restore():
    shell = DesktopShell(width=800, height=600)
    w1 = NSWindow(content_rect=NSRect(40, 40, 320, 240), title="Doc")
    shell.open_window(w1)
    snap = shell.snapshot()
    new_shell = DesktopShell.restore(snap)
    assert len(new_shell.windows) == 1
    assert new_shell.windows[0].title == "Doc"


def test_render_shell_svg_contains_windows_and_dock():
    shell = DesktopShell(width=640, height=480)
    w1 = NSWindow(content_rect=NSRect(10, 10, 200, 150), title="A")
    w2 = NSWindow(content_rect=NSRect(220, 30, 200, 150), title="B")
    shell.open_window(w1)
    shell.open_window(w2)
    svg = shell.render_to_svg()
    assert '<rect' in svg
    assert 'dock-item' in svg
    assert 'A' in svg and 'B' in svg
