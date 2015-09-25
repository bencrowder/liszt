from django.conf import settings
from liszt.models import Item, List, Context, Tag

def get_or_create_tag(tag_slug):
    tag = None

    # Try to get the context
    try:
        tag = Tag.objects.get(slug=tag_slug)
    except Exception as e:
        # Not found, so create it
        try:
            tag = Tag()
            tag.slug = tag_slug
            tag.save()
        except Exception as e:
            pass

    return tag

def get_or_create_context(context_slug):
    context = None

    # Try to get the context
    try:
        context = Context.objects.get(slug=context_slug)
    except Exception as e:
        # Not found, so create it
        try:
            context = Context()
            context.slug = context_slug
            context.save()
        except Exception as e:
            print("Couldn't create context", e)
            pass

    return context

def get_or_create_list(context, list_slug, parent_list_slug=None):
    # Get the list
    try:
        if parent_list_slug:
            the_list = List.objects.get(slug=list_slug, parent_list__slug=parent_list_slug, context=context)
        else:
            the_list = List.objects.get(slug=list_slug, context=context)
    except Exception as e:
        # Not found, so create it
        try:
            the_list = List()
            the_list.slug = list_slug
            the_list.context = context

            if parent_list_slug:
                # There's a parent list, so try to get it
                try:
                    parent_list = List.objects.get(slug=parent_list_slug)
                except Exception as e:
                    # Parent list not found, so create it
                    parent_list = List()
                    parent_list.slug = parent_list_slug
                    parent_list.context = context

                # Hook it up as the parent_list
                the_list.parent_list = parent_list

            the_list.save()
        except Exception as e:
            print("Couldn't create list", e)
            pass

    return the_list

def parse_block(block):
    """
Parse a block (a sequence of items with/without list/context specifiers.
    """
    response = []

    # Split into groups by newlines
    for group in [x.strip() for x in block.split('----')]:
        group_response = {
            'list': None,
            'sublist': None,
            'context': None,
            'items': [],
        }

        for line in [x.strip() for x in group.split('\n') if x != '']:
            # If it starts with /, it's a context
            if line[0] == '/':
                # See if there's a list
                if ':' in line[1:]:
                    # Yes, there's a list
                    lists = line[1:].split(':')

                    # Context
                    group_response['context'] = lists[0]

                    # List, now check for sublist
                    if len(lists) > 2:
                        # Yes, sublist
                        group_response['list'], group_response['sublist'] = lists[1], lists[2]
                    else:
                        group_response['list'] = lists[1]
                else:
                    # No list, just add the context
                    group_response['context'] = line[1:]
            elif line[0] == ':':
                # List, now check for sublist
                if ':' in line[1:]:
                    # Yes, sublist
                    group_response['list'], group_response['sublist'] = line[1:].split(':')
                else:
                    group_response['list'] = line[1:]
            else:
                # Normal item

                # Get tags and notes
                label, tags, notes = parse_item(line)

                group_response['items'].append({
                    'label': label,
                    'tags': tags,
                    'notes': notes,
                })

        response.append(group_response)

    return response

def process_payload(payload, default_context=None, default_list=None):
    """
Takes a payload, parses it into blocks, and then adds the items in it
to the appropriate contexts/lists.
    """
    status = 'success'
    message = ''

    blocks = parse_block(payload)

    for block in blocks:
        try:
            # Clear things out
            b_context = default_context
            b_list = default_list
            b_items = block['items']
            
            # Set the context if it's there, otherwise use default
            if block['context'] is not None:
                b_context = get_or_create_context(block['context'])

            # Set the list if it's there, otherwise use default
            if block['list'] is not None:
                if block['sublist'] is not None:
                    b_list = get_or_create_list(b_context, block['sublist'], block['list'])
                else:
                    b_list = get_or_create_list(b_context, block['list'])

            # Get the number of items in b_list to use for ordering
            b_list_len = b_list.count_items()
            
            # Add items to the specified context/list
            for i, item in enumerate(b_items):
                b_item = Item()
                b_item.parent_list = b_list
                b_item.text = item['label'].strip()
                if item['notes'] != '':
                    b_item.notes = item['notes']
                b_item.order = i + b_list_len # Add to the end of the list
                b_item.save()

                # Add tags
                for tag in item['tags']:
                    tag_obj = get_or_create_tag(tag)
                    b_item.tags.add(tag_obj)
                b_item.save()

        except Exception as e:
            status = 'error'
            message = e

    return status, message

def parse_item(item):
    """ Parses a line. Returns tuple with tagless string, tag list, and notes. """
    label = []
    tags = []
    notes = ''

    # Pull out notes if there
    if ':::' in item:
        item, notes = [x.strip() for x in item.split(':::')]

    # Now go through and get tags if any
    for token in item.split(' '):
        if token[0] == '#':
            # A tag
            tags.append(token[1:])
        else:
            # Not a tag
            label.append(token)

    return (' '.join(label).strip(), tags, notes)
