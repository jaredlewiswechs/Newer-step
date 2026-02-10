from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Floorplan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="floorplans")
    name = models.CharField(max_length=200)
    data = models.JSONField(default=dict)  # stores geometry/room defs as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name}: {self.name}"
