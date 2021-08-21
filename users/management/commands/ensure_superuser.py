import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()
        username, password, email = (
            os.environ['DJANGO_SUPERUSER_USERNAME'],
            os.environ['DJANGO_SUPERUSER_PASSWORD'],
            os.environ['DJANGO_SUPERUSER_EMAIL'],
        )
        if not User.objects.filter(username=username, email=email).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
