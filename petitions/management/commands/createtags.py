"""
Generates Tags specified in config.yml
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

from petitions.models import Tag


class Command(BaseCommand):
    help = "Creates Tag entries specified in config.yml"

    def handle(self, *args, **options):
        CONFIG = settings.CONFIG
        tags = CONFIG['tags']

        num_tags = len(tags)
        if num_tags == 0:
            raise CommandError("No tags specified in config.yml")

        self.stdout.write('Generating %d Tag objects' % num_tags)
        try:
            with transaction.atomic():
                for tag in tags:
                    name = tag['name']
                    if name == "":
                        raise CommandError(
                            "Empty Tag found.")

                    tag_obj = Tag(name=name)
                    tag_obj.save()
        except:
            self.stdout.write(self.style.ERROR(
                'Failed to create Tag objects.'))
            return
        self.stdout.write(self.style.SUCCESS(
            'Successfully created Tag objects'))
