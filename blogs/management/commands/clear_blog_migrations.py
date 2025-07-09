from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Clears the migration history for the blogs app'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app = 'blogs'")
        self.stdout.write(self.style.SUCCESS('Successfully cleared blog migration history.'))