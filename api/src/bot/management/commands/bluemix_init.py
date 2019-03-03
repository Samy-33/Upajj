from django.conf import settings
from django.core.management.base import BaseCommand
import sys

class Command(BaseCommand):

    args = ''
    help = 'Django deployment script - IBM Cloud'

    def add_arguments(self, parser):

        parser.add_argument('application_name', type=str)

    def handle(self, *args, **kwargs):
        super().handle(*args, **kwargs)