from django.contrib import admin
from .models import Project, Floorplan

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")


@admin.register(Floorplan)
class FloorplanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "created_at", "updated_at")
