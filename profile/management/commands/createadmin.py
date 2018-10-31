"""
Sets an account to be an admin.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Sets an existing user to be an admin"

    def add_arguments(self, parser):
        parser.add_argument(
            'email', type=str, help='Email address of the user to set as admin')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = User.objects.get(email=email)
        except:
            raise CommandError(
                'User "%s" does not exist. Did you login with that email first?' % email)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully set %s as an admin' % email))
