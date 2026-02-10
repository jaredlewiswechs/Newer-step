from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Floorplan
from .serializers import ProjectSerializer, FloorplanSerializer

# Try to reuse Kernel SVG demo for an on-server SVG preview
try:
    from Kernel.demo import server as kernel_server
except Exception:
    kernel_server = None


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class FloorplanViewSet(viewsets.ModelViewSet):
    queryset = Floorplan.objects.all()
    serializer_class = FloorplanSerializer

    @action(detail=False, methods=["get"])
    def svg_preview(self, request):
        """Return an SVG preview (uses Kernel demo if available)."""
        if kernel_server is None:
            return Response({"error": "Kernel demo server not available"}, status=503)
        try:
            # call the svg_demo() function to get an SVG Response
            resp = kernel_server.svg_demo()
            # Starlette Response has .body or .content
            body = getattr(resp, "body", None) or getattr(resp, "content", None)
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            return HttpResponse(body, content_type="image/svg+xml")
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=["get"], url_path="export_svg")
    def export_svg(self, request, pk=None):
        """Export the stored Floorplan as SVG (simple renderer)."""
        try:
            from .geometry import floorplan_to_svg
        except Exception:
            return Response({"error": "Geometry helper not available"}, status=500)

        fp = self.get_object()
        svg = floorplan_to_svg(fp.data or {})
        return HttpResponse(svg, content_type="image/svg+xml")

    @action(detail=True, methods=["get"], url_path="export_dxf")
    def export_dxf(self, request, pk=None):
        """Export the stored Floorplan as a DXF file attachment."""
        try:
            from .geometry import floorplan_to_dxf_bytes
        except Exception:
            return Response({"error": "DXF export helper not available"}, status=500)

        fp = self.get_object()
        try:
            data = floorplan_to_dxf_bytes(fp.data or {})
        except RuntimeError as e:
            return Response({"error": str(e)}, status=500)

        resp = HttpResponse(data, content_type="application/dxf")
        resp["Content-Disposition"] = f"attachment; filename=\"floorplan_{fp.id}.dxf\""
        return resp
