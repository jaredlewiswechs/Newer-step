"""Application process model using realTinyTalk as the scripting language."""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import itertools

from realTinyTalk.runtime import Runtime
from realTinyTalk.lexer import Lexer
from realTinyTalk.parser import Parser
from realTinyTalk.ffi import wrap_python_function
from realTinyTalk.types import Value

from nina.desktop_shell import DesktopShell
from Kernel.window.nswindow import NSWindow
from Kernel.view.nsview import NSRect


_pid_counter = itertools.count(1)


class AppProcess:
    def __init__(self, source: str, shell: DesktopShell, title: Optional[str] = None, *,
                 allow_system: bool = False, allow_network: bool = False, allow_filesystem: bool = False, allow_vault: bool = True, autosave: bool = True):
        self.pid = next(_pid_counter)
        self.source = source
        self.shell = shell
        self.title = title or f"App-{self.pid}"
        self.runtime = Runtime()
        self._windows: List[NSWindow] = []
        self._owner_id: Optional[str] = None
        # FFI / permission flags
        self.allow_system = allow_system
        self.allow_network = allow_network
        self.allow_filesystem = allow_filesystem
        self.allow_vault = allow_vault
        self.autosave = autosave
        # simple message queue for IPC
        self._inbox: List[Dict[str, Any]] = []
        self._subscriptions: set = set()
        self._register_shell_api()
        self._running = False

    def _ensure_owner(self) -> str:
        """Ensure this process has a Vault owner identity registered."""
        if self._owner_id:
            return self._owner_id
        from newton_supercomputer import vault
        self._owner_id = vault.register_identity(f"app:{self.pid}", "demo")
        return self._owner_id

    def _register_shell_api(self):
        # provide a minimal shell API to TinyTalk scripts
        def open_window_py(title: str = None):
            t = title or self.title
            w = NSWindow(content_rect=NSRect(80, 80, 360, 240), title=t)
            self.shell.open_window(w)
            self._windows.append(w)
            return {'id': id(w), 'title': w.title}

        def open_note_window_py(title: str = None):
            t = title or self.title
            from Kernel.view.notes_view import NotesView
            w = NSWindow(content_rect=NSRect(80, 80, 420, 320), title=t)
            nv = NotesView(NSRect(6, 6, 408, 308), title=t)
            w.content_view = nv
            self.shell.open_window(w)
            self._windows.append(w)
            return {'id': id(w), 'title': w.title}

        def list_windows_py():
            return [{'id': id(w), 'title': w.title} for w in self._windows]

        def set_window_note_py(window_id: int, title: str, content: str):
            for w in self._windows:
                if id(w) == window_id and hasattr(w.content_view, 'set_content'):
                    w.content_view.set_content(title, content)
                    # autosave if enabled and permitted
                    try:
                        if self.autosave:
                            if not self.allow_vault:
                                raise RuntimeError('Vault access disallowed for this process')
                            owner = self._ensure_owner()
                            from newton_supercomputer import vault
                            vault.store(owner, {'title': title, 'content': content}, metadata={'app': self.title})
                    except Exception:
                        pass
                    return True
            return False

        def get_window_note_py(window_id: int):
            for w in self._windows:
                if id(w) == window_id and hasattr(w.content_view, 'content'):
                    return {'title': getattr(w.content_view, 'title', ''), 'content': getattr(w.content_view, 'content', '')}
            return None

        # IPC (publish/receive simple message queue)
        def publish_py(channel: str, message: str):
            from nina.process import _process_registry
            _process_registry.publish(channel, {'from': self.pid, 'message': message})
            return True

        def subscribe_py(channel: str):
            self._subscriptions.add(channel)
            return True

        def unsubscribe_py(channel: str):
            self._subscriptions.discard(channel)
            return True

        def fetch_messages_py():
            inbox = list(self._inbox)
            self._inbox.clear()
            return inbox

        def show_message_py(msg: str):
            # simple print for now
            print(f"[App {self.pid}] {msg}")
            return None

        # note persistence via Vault
        def save_note_py(title: str, content: str):
            from newton_supercomputer import vault
            owner = self._ensure_owner()
            entry_id = vault.store(owner, {'title': title, 'content': content}, metadata={'app': self.title})
            return entry_id

        def load_note_py(entry_id: str):
            from newton_supercomputer import vault
            owner = self._ensure_owner()
            try:
                data = vault.retrieve(owner, entry_id)
                # If data is bytes, decode
                if isinstance(data, (bytes, bytearray)):
                    try:
                        return data.decode()
                    except Exception:
                        return data
                return data
            except Exception as e:
                raise RuntimeError(str(e))

        shell_map = {
            'open_window': wrap_python_function(open_window_py),
            'open_note_window': wrap_python_function(open_note_window_py),
            'list_windows': wrap_python_function(list_windows_py),
            'set_window_note': wrap_python_function(set_window_note_py),
            'get_window_note': wrap_python_function(get_window_note_py),
            'publish': wrap_python_function(publish_py),
            'subscribe': wrap_python_function(subscribe_py),
            'unsubscribe': wrap_python_function(unsubscribe_py),
            'fetch_messages': wrap_python_function(fetch_messages_py),
            'show_message': wrap_python_function(show_message_py),
            'save_note': wrap_python_function(save_note_py),
            'load_note': wrap_python_function(load_note_py),
        }

        self.runtime.global_scope.define('shell', Value.map_val(shell_map), const=True)

    def start(self) -> Value:
        if self._running:
            raise RuntimeError("Process already running")
        # Configure FFI according to process policy
        from realTinyTalk.ffi import FFIConfig, configure_ffi
        cfg = FFIConfig()
        cfg.allow_system = self.allow_system
        cfg.allow_javascript = self.allow_network  # proxy mapping: network -> js allowed
        cfg.allow_filesystem = self.allow_filesystem
        configure_ffi(cfg)

        lexer = Lexer(self.source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self._running = True
        try:
            result = self.runtime.execute(ast)
        finally:
            # restore to defaults (per-process config cleanup)
            configure_ffi(FFIConfig())
        return result

    def kill(self):
        # best-effort cleanup
        self._running = False
        for w in list(self._windows):
            self.shell.close_window(w)
        self._windows = []

    @property
    def windows(self) -> List[NSWindow]:
        return list(self._windows)


class ProcessManager:
    def __init__(self, shell: DesktopShell):
        self.shell = shell
        self._processes: Dict[int, AppProcess] = {}
        # simple pub/sub registry: channel -> list of messages
        self._channels: Dict[str, List[Dict[str, Any]]] = {}

    def launch_script(self, source: str, title: Optional[str] = None, **kwargs) -> AppProcess:
        p = AppProcess(source, self.shell, title, **kwargs)
        self._processes[p.pid] = p
        p.start()
        return p

    def subscribe(self, pid: int, channel: str) -> bool:
        p = self._processes.get(pid)
        if not p:
            return False
        p._subscriptions.add(channel)
        return True

    def unsubscribe(self, pid: int, channel: str) -> bool:
        p = self._processes.get(pid)
        if not p:
            return False
        p._subscriptions.discard(channel)
        return True

    def publish(self, channel: str, message: Dict[str, Any]):
        self._channels.setdefault(channel, []).append(message)
        # deliver only to subscribers
        for p in self._processes.values():
            if channel in p._subscriptions:
                p._inbox.append({'channel': channel, **message})


    def list_processes(self) -> List[Dict[str, Any]]:
        return [{'pid': pid, 'title': p.title, 'windows': [{'id': id(w), 'title': w.title} for w in p.windows]} for pid, p in self._processes.items()]

    def kill(self, pid: int) -> bool:
        p = self._processes.get(pid)
        if not p:
            return False
        p.kill()
        del self._processes[pid]
        return True

    # pub/sub
    def publish(self, channel: str, message: Dict[str, Any]):
        self._channels.setdefault(channel, []).append(message)
        # fan-out: deliver to process inboxes that have subscribed (subscription model TBD)
        # For now, deliver to all inboxes
        for p in self._processes.values():
            p._inbox.append({'channel': channel, **message})

    def fetch_channel(self, channel: str) -> List[Dict[str, Any]]:
        return list(self._channels.get(channel, []))


# lightweight registry for module-level access in publish wrappers
_process_registry: Optional[ProcessManager] = None

def init_process_registry(reg: ProcessManager):
    global _process_registry
    _process_registry = reg
