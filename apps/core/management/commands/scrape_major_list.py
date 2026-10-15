from django.core.management.base import BaseCommand

from core.scraper import scrape_major_list


class Command(BaseCommand):
    help = "Scrape major list"

    def handle(self, *args, **kwargs):
        scrape_major_list()
