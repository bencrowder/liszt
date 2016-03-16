from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from liszt.models import Context, List, Item
from liszt.utils import process_payload

import sqlite3

class Command(BaseCommand):
    args = '<list file>'
    help = 'Unstars anything that is starred'

    def handle(self, *args, **options):
        try:
            starred = Item.objects.filter(starred=True)

            for item in starred:
                item.starred = False
                item.save()
        except Exception as e:
            print(e)
