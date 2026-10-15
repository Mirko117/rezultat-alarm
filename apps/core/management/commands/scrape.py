import logging

from django.core.management.base import BaseCommand

from core.models import Major
from core.scraper import scrape_from_major

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Scrape data from all majors"

    def handle(self, *args, **kwargs):
        majors = Major.objects.all()
        if len(majors) > 0:
            for major in majors:
                scrape_from_major(major)
        else:
            logger.warning("No majors to scrape found!")
