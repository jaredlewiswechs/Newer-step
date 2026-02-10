from rest_framework import serializers
from .models import Project, Floorplan


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "created_at"]


class FloorplanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floorplan
        fields = ["id", "project", "name", "data", "created_at", "updated_at"]
