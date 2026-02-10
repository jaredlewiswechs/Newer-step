"""A minimal Desktop Shell abstraction for window stack, focus, dock, and session snapshots."""

from __future__ import annotations
from typing import List, Optional, Dict, Any

from Kernel.window.nswindow import NSWindow, NSWindowStyleMask
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
        # simple menu bar definition (label + items)
        self._menu_bar = [
            {"label": "Apple", "items": [{"label": "About"}, {"label": "Quit"}]},
            {"label": "File", "items": [{"label": "New"}, {"label": "Open"}]},
            {"label": "Edit", "items": [{"label": "Undo"}, {"label": "Redo"}]},
            {"label": "Window", "items": [{"label": "Minimize"}, {"label": "Close"}]},
        ]
        # last rendered menu bboxes for hit-testing: list of (x, y, w, h)
        self._menu_bboxes = []

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

        # menu bar (top)
        menu_h = 24
        parts.append(f'<rect x="0" y="0" width="{w}" height="{menu_h}" fill="#f0f0f0" />')
        # render menu labels and record bboxes
        self._menu_bboxes = []
        start_x = 8
        spacing = 76
        for i, m in enumerate(self._menu_bar):
            mx = start_x + i * spacing
            my = 0
            mw = 64
            mh = menu_h
            # text vertically centered
            parts.append(f'<text x="{mx+mw/2}" y="{my+menu_h/2+4}" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#000">{m["label"]}</text>')
            self._menu_bboxes.append((mx, my, mw, mh))

        # render windows (in z-order: bottom first)
        for win in list(self._windows):
            inner = self._extract_inner_svg(win.render_to_svg(include_chrome=True))
            # determine chrome height (title bar) to align rendering and hit-testing
            chrome_h = 22 if (hasattr(win, "style_mask") and (win.style_mask & NSWindowStyleMask.TITLED)) else 0
            total_h = win.frame.height + chrome_h
            # convert window-origin (assumed bottom-left) to SVG top-left translation
            tx = win.frame.x
            # account for the menu bar at top
            ty = h - (win.frame.y + win.frame.height) - chrome_h - menu_h
            parts.append(
                f'<g transform="translate({tx},{ty})" data-window-id="{id(win)}" data-window-title="{win.title}">'
            )
            # if window is being dragged, render a highlight rectangle behind it
            try:
                is_dragging = bool(getattr(win, '_is_dragging', False))
            except Exception:
                is_dragging = False
            if is_dragging:
                parts.append(f'<rect x="-4" y="-4" width="{win.frame.width+8}" height="{total_h+8}" fill="none" stroke="#ff0" stroke-width="3" opacity="0.9" rx="8" />')
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
        # check menu bar first
        menu_h = 24
        if y <= menu_h:
            # find which menu label was clicked
            for i, bbox in enumerate(self._menu_bboxes):
                bx, by, bw, bh = bbox
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    # return a sentinel value by raising a custom attribute? Instead, store last menu hit
                    self._last_menu_hit = {"menu_index": i, "label": self._menu_bar[i]["label"]}
                    return None
            # clicked on menu bar but not on a label
            self._last_menu_hit = {"menu_index": None, "label": None}
            return None
        # check topmost first
        for win in reversed(self._windows):
            chrome_h = 22 if (hasattr(win, "style_mask") and (win.style_mask & NSWindowStyleMask.TITLED)) else 0
            tx = win.frame.x
            ty = self._height - (win.frame.y + win.frame.height) - chrome_h
            total_h = win.frame.height + chrome_h
            if tx <= x <= tx + win.frame.width and ty <= y <= ty + total_h:
                return win

        # If no window hit, check dock icons (they map to open windows)
        dock_h = 64
        icon_spacing = 72
        start_x = 16
        y_center = self._height - dock_h / 2
        r = 20
        for i, win in enumerate(self._windows):
            cx = start_x + i * icon_spacing
            dx = x - cx
            dy = y - y_center
            if dx * dx + dy * dy <= r * r:
                return win
        return None

    def menu_hit_test(self, point: tuple):
        """Return menu hit info dict or None."""
        x, y = point
        menu_h = 24
        if y <= menu_h:
            for i, bbox in enumerate(self._menu_bboxes):
                bx, by, bw, bh = bbox
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    return {"menu_index": i, "label": self._menu_bar[i]["label"]}
            return {"menu_index": None, "label": None}
        return None

    def __repr__(self):
        return (
            f"<DesktopShell windows={len(self._windows)} dock={len(self._dock_items)}>"
        )
