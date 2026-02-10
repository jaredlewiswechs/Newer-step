"""A minimal Desktop Shell abstraction for window stack, focus, dock, and session snapshots."""

from __future__ import annotations
from typing import List, Optional, Dict, Any

from Kernel.window.nswindow import NSWindow
from Kernel.view.nsview import NSRect


class DesktopShell:
    """Manages a set of open windows, z-order, focus, and provides a simple
    SVG renderer for a shell-like UI (background + dock + windows).
    """

    def __init__(
        self,
        dock_items: Optional[List[str]] = None,
        width: int = 1024,
        height: int = 768,
    ):
        self._windows: List[NSWindow] = []
        self._dock_items = list(dock_items or [])
        self._width = width
        self._height = height

    # window management
    def open_window(self, w: NSWindow):
        if w not in self._windows:
            self._windows.append(w)
        self.bring_to_front(w)
        w.make_key_and_order_front()

    def close_window(self, w: NSWindow):
        if w in self._windows:
            self._windows.remove(w)
        w.close()

    def bring_to_front(self, w: NSWindow):
        if w in self._windows:
            self._windows.remove(w)
        self._windows.append(w)
        # ensure only this window is key
        for win in self._windows:
            win._is_key = win is w

    def focus_window(self, w: NSWindow):
        if w in self._windows:
            self.bring_to_front(w)

    @property
    def windows(self) -> List[NSWindow]:
        return list(self._windows)

    # snapshot/restore
    def snapshot(self) -> Dict[str, Any]:
        return {
            "width": self._width,
            "height": self._height,
            "dock": list(self._dock_items),
            "windows": [
                {
                    "title": win.title,
                    "frame": (
                        win.frame.x,
                        win.frame.y,
                        win.frame.width,
                        win.frame.height,
                    ),
                }
                for win in self._windows
            ],
        }

    @classmethod
    def restore(cls, data: Dict[str, Any]) -> "DesktopShell":
        ds = cls(
            dock_items=data.get("dock", []),
            width=data.get("width", 1024),
            height=data.get("height", 768),
        )
        for winfo in data.get("windows", []):
            x, y, w, h = winfo.get("frame", (0, 0, 480, 320))
            win = NSWindow(
                content_rect=NSRect(x, y, w, h), title=winfo.get("title", "Window")
            )
            ds.open_window(win)
        return ds

    # rendering
    def _extract_inner_svg(self, svg: str) -> str:
        # strip the outer <svg ...>...</svg>
        start = svg.find(">")
        if start == -1:
            return svg
        inner = svg[start + 1 :]
        if inner.endswith("</svg>"):
            inner = inner[:-6]
        return inner

    def render_to_svg(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> str:
        w = width or self._width
        h = height or self._height
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        ]
        # background
        parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#111" />')

        # render windows (in z-order: bottom first)
        for win in list(self._windows):
            inner = self._extract_inner_svg(win.render_to_svg(include_chrome=True))
            # convert window-origin (assumed bottom-left) to SVG top-left translation
            tx = win.frame.x
            ty = h - (win.frame.y + win.frame.height)
            parts.append(
                f'<g transform="translate({tx},{ty})" data-window-id="{id(win)}" data-window-title="{win.title}">'
            )
            parts.append(inner)
            parts.append("</g>")

        # dock
        dock_h = 64
        parts.append(
            f'<rect x="0" y="{h - dock_h}" width="{w}" height="{dock_h}" fill="#222" opacity="0.9"/>'
        )
        # show icons for each open window
        icon_spacing = 72
        start_x = 16
        y_center = h - dock_h / 2
        for i, win in enumerate(self._windows):
            cx = start_x + i * icon_spacing
            parts.append(
                f'<g class="dock-item" transform="translate({cx},{y_center})">'
            )
            parts.append('<circle cx="0" cy="0" r="20" fill="#fff" opacity="0.9" />')
            parts.append(
                f'<text x="0" y="36" text-anchor="middle" font-size="11" fill="#fff" font-family="sans-serif">{win.title}</text>'
            )
            parts.append("</g>")

        parts.append("</svg>")
        return "\n".join(parts)

    def hit_test(self, point: tuple) -> Optional[NSWindow]:
        """Return the topmost window at the given SVG-space point (x,y) or None.

        Coordinates are in SVG space (top-left origin, y increases downward).
        """
        x, y = point
        # check topmost first
        for win in reversed(self._windows):
            tx = win.frame.x
            ty = self._height - (win.frame.y + win.frame.height)
            if tx <= x <= tx + win.frame.width and ty <= y <= ty + win.frame.height:
                return win
        return None

    def __repr__(self):
        return (
            f"<DesktopShell windows={len(self._windows)} dock={len(self._dock_items)}>"
        )
