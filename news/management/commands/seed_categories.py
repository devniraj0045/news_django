from django.core.management.base import BaseCommand
from news.models import Category

class Command(BaseCommand):
    help = 'Populates the database with standard news categories'

    def handle(self, *args, **options):
        categories = [
            'Politics',
            'Business',
            'Economy',
            'Sports',
            'Entertainment',
            'Technology',
            'Health',
            'Education',
            'World',
            'Tourism',
            'Opinion',
            'Lifestyle',
            'Society',
            'Interview',
            'Literature',
            'Science',
            'Auto',
            'Employment',
            'Crime',
            'Weather',
            'Diaspora' # Prabas
        ]

        self.stdout.write('Seeding categories...')
        
        count = 0
        for name in categories:
            cat, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {name}'))
                count += 1
            else:
                self.stdout.write(f'Skipped: {name} (Already exists)')

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new categories.'))
