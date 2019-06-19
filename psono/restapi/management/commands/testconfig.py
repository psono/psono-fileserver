from django.core.management.base import BaseCommand

from restapi.utils import test_config

class Command(BaseCommand):
    help = 'Tests your fileserver config.'

    def handle(self, *args, **options):

        result = test_config()

        if 'error' in result:
            self.stdout.write(result['error'])
            return

        self.stdout.write('Successfully completed. (Don\'t forget to restart your fileserver if you have modified your settings.yaml.)' )