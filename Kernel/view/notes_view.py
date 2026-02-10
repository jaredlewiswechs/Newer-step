from __future__ import annotations
from typing import Optional

from .nsview import NSView, NSRect
from ..gui.nsbezier import NSColor


class NotesView(NSView):
    """A simple notes editor view that renders a title and content as SVG text."""

    def __init__(self, frame: NSRect, title: str = "Untitled"):
        super().__init__(frame)
        self.title = title
        self.content = ""
        self.identifier = "notes-view"
        self._background_color = NSColor(255, 255, 250)

    def set_content(self, title: Optional[str], content: str):
        if title:
            self.title = title
        self.content = content

    def render_tree(self) -> str:
        # Leverage base render of background and render title/content as text
        w = self.frame.width
        h = self.frame.height
        parts = [f'<g class="notes-view" data-view-id="{id(self)}">']
        # background
        parts.append(
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fff8e1" stroke="#ddd" rx="6" />'
        )
        # title area
        parts.append(
            f'<text x="12" y="22" font-size="14" font-family="sans-serif" font-weight="bold">{self.title}</text>'
        )
        # content (simple, no wrapping beyond newlines)
        lines = (self.content or "").split("\n")
        y = 46
        for line in lines[:20]:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            parts.append(
                f'<text x="12" y="{y}" font-size="12" font-family="monospace">{safe}</text>'
            )
            y += 16
        parts.append("</g>")
        return "\n".join(parts)
