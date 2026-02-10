"""Geometry helpers for Floorplans.

Simple converters from floorplan JSON to SVG and DXF.
This is intentionally minimal and tolerant of simple input formats.

Expected floorplan.data example:
{
  "walls": [ {"points": [[10,10],[200,10]]}, {"points": [[200,10],[200,150]]} ],
  "rooms": [ {"polygon": [[10,10],[200,10],[200,150],[10,150]]} ]
}
"""
from io import BytesIO
from typing import Dict, List

try:
    from shapely.geometry import LineString, Polygon
except Exception:
    LineString = None
    Polygon = None


def _points_to_path(points: List[List[float]]) -> str:
    if not points:
        return ""
    path = f"M {points[0][0]} {points[0][1]}"
    for x, y in points[1:]:
        path += f" L {x} {y}"
    return path


def floorplan_to_svg(data: Dict) -> str:
    width = 1000
    height = 800
    walls = data.get("walls", [])
    rooms = data.get("rooms", [])

    svg_parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>"]

    # rooms (filled polygons)
    for room in rooms:
        poly = room.get("polygon", [])
        if not poly:
            continue
        path = _points_to_path(poly) + " Z"
        svg_parts.append(f"<path d=\"{path}\" fill=\"#f7f7ff\" stroke=\"#d0d0f0\" stroke-width=1 />")

    # walls (stroked lines)
    for wall in walls:
        pts = wall.get("points", [])
        if len(pts) < 2:
            continue
        path = _points_to_path(pts)
        svg_parts.append(f"<path d=\"{path}\" fill=\"none\" stroke=\"#000\" stroke-width=4 stroke-linecap=round />")

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def floorplan_to_dxf_bytes(data: Dict) -> bytes:
    try:
        import ezdxf
    except Exception as e:
        raise RuntimeError("ezdxf is required for dxf export") from e

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    walls = data.get("walls", [])
    rooms = data.get("rooms", [])

    # rooms as closed polylines
    for room in rooms:
        poly = room.get("polygon", [])
        if not poly:
            continue
        # ezdxf expects iterable of (x,y)
        msp.add_lwpolyline(poly, close=True)

    # walls as lines
    for wall in walls:
        pts = wall.get("points", [])
        if len(pts) < 2:
            continue
        for a, b in zip(pts[:-1], pts[1:]):
            msp.add_line(a, b)

    stream = BytesIO()
    doc.write(stream)
    stream.seek(0)
    return stream.read()
