import zipfile
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Unpack archived realTinyTalk into frontend/blueprint/public/realtinytalk/"

    def handle(self, *args, **options):
        base = Path(__file__).resolve().parents[4]
        archive_zip = base / "_archive" / "realtinytalk_old" / "selling.zip"
        target = base / "frontend" / "blueprint" / "public" / "realtinytalk"
        if not archive_zip.exists():
            self.stderr.write("Archive not found: %s" % archive_zip)
            return
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_zip, "r") as zf:
            zf.extractall(target)
        self.stdout.write(self.style.SUCCESS(f"Extracted realTinyTalk to {target}"))
