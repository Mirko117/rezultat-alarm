from django.core.management.base import BaseCommand

from core.models import Major
from core.scraper import scrape_from_major


class Command(BaseCommand):
    help = "Scrape data from the school site"

    def handle(self, *args, **kwargs):
        # Must add one major manually in the admin panel before running this command
        major = Major.objects.all().first()
        if major:
            scrape_from_major(major)
