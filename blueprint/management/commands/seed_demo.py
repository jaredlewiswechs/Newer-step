from django.core.management.base import BaseCommand
from blueprint.models import Project, Floorplan


class Command(BaseCommand):
    help = "Seed a demo project and floorplan"

    def handle(self, *args, **options):
        proj, _ = Project.objects.get_or_create(name="Demo Project")
        fp_data = {
            "walls": [
                {"points": [[50, 50], [450, 50]]},
                {"points": [[450, 50], [450, 300]]},
                {"points": [[450, 300], [50, 300]]},
                {"points": [[50, 300], [50, 50]]},
            ],
            "rooms": [
                {"polygon": [[60, 60], [440, 60], [440, 290], [60, 290]]}
            ],
        }
        floorplan, created = Floorplan.objects.get_or_create(project=proj, name="Demo Floorplan", defaults={"data": fp_data})
        if not created:
            floorplan.data = fp_data
            floorplan.save()
        self.stdout.write(self.style.SUCCESS(f"Seeded project {proj.id} and floorplan {floorplan.id}"))
