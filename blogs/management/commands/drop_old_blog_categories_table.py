from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drops the old blogs_blog_categories table if it exists.'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS blogs_blog_categories;")
        self.stdout.write(self.style.SUCCESS('Dropped table blogs_blog_categories (if it existed).'))
