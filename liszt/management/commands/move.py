from django.core.management.base import BaseCommand, CommandError

from liszt.models import Context, List, Item
from liszt import utils

import sys

class Command(BaseCommand):
    args = '<src> <dest>'
    help = 'Moves lists to another context/list'

    def add_arguments(self, parser):
        parser.add_argument('src', nargs='+', type=str)
        parser.add_argument('dest', nargs='+', type=str)

    def handle(self, *args, **options):
        src = options['src'][0]
        dest = options['dest'][0]

        # Parse the source
        src_context_slug, src_list_slugs = utils.parse_selector(src)

        # If error (more than one context/list, can't find the context/list, etc.), exit
        src_context = utils.get_context(src_context_slug)

        if src_context is None:
            print("Error, source context doesn't exist")
            sys.exit(-1)

        # Check if src is context or list
        if len(src_list_slugs) == 0:
            # src is only a context, so source_set is all lists in that context
            source_set = src_context.get_active_lists()
        else:
            # src is a list, so source_set is that list
            source_set = [utils.get_list(src_context_slug, src_list_slugs)]

        print("Source set", source_set)


        # Parse destination
        dest_context_slug, dest_list_slugs = utils.parse_selector(dest)

        # If error (more than one context/list, can't find the context/list, etc.), exit
        dest_context = utils.get_context(dest_context_slug)

        if dest_context is None:
            print("Error, destination context doesn't exist")
            sys.exit(-1)

        # Check if dest is context or list
        if len(dest_list_slugs) == 0:
            # dest is a context
            for l in source_set:
                l.context = dest_context
                l.parent_list = None
                l.save()
        else:
            # dest is a list
            dest_list = utils.get_or_create_list(dest_context, dest_list_slugs)

            for l in source_set:
                l.context = dest_context
                l.parent_list = dest_list
                l.save()

        if len(src_list_slugs) == 0:
            # Cleanup if src is a context
            src_context.delete()
