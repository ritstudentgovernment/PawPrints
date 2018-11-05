class Command(BaseCommand):
    help = "Manage failed backgroud Huey tasks"

    def handle(self, *args, **options):
        