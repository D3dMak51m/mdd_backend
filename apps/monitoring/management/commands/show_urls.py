# apps/monitoring/management/commands/show_urls.py

from django.core.management.base import BaseCommand
from django.urls import get_resolver

class Command(BaseCommand):
    help = 'Displays all of the projects URL patterns.'

    def handle(self, *args, **options):
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        self.stdout.write(self.style.SUCCESS("URL Patterns:"))
        self._print_patterns(url_patterns)

    def _print_patterns(self, patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                # Это URLResolver (include)
                self._print_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                # Это URLPattern
                self.stdout.write(f"/{prefix}{str(pattern.pattern)}\t{pattern.callback.__module__}.{pattern.callback.__name__}\t{pattern.name}")