from django.conf import settings
from liszt.models import Item, List, Context, Tag

def parse_list_string(list_string):
    # Slice off initial / if it's there
    if list_string[0] == '/':
        list_string = list_string[1:]

    # Now see if there's a sublist
    if '/' in list_string:
        the_list, the_sublist = list_string.split('/')
    else:
        the_list = list_string
        the_sublist = None

    return the_list, the_sublist

def parse_selector(selector):
    context = None
    the_list = None
    the_sublist = None

    # Context
    if selector[0:2] == '::':
        # Initial context, strip off ::
        items = selector[2:].split('/')
        context = items[0]
    else:
        # No context, split lists
        items = selector.split('/')

    # List
    if len(items) > 1:
        the_list = items[1]

        if len(items) > 2:
            the_sublist = items[2]

    return context, the_list, the_sublist

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
            context.order = 0 # put at beginning
            context.save()
        except Exception as e:
            print("Couldn't create context", e)
            pass

    return context

def get_or_create_list(context, list_slug, parent_list_slug=None):
    # Get the list
    try:
        if parent_list_slug:
            try:
                parent_list = List.objects.get(slug=parent_list_slug, context=context, parent_list=None)
                the_list = List.objects.get(slug=list_slug, parent_list__slug=parent_list_slug, context=context)
            except Exception as e:
                # New sublist
                the_list = List()
                the_list.slug = list_slug
                the_list.order = 0 # put at beginning
                the_list.parent_list = parent_list
                the_list.context = context
                the_list.save()
        else:
            the_list = List.objects.get(slug=list_slug, context=context, parent_list=None)
    except Exception as e:
        # Not found, so create it
        try:
            the_list = List()
            the_list.slug = list_slug
            the_list.order = 0 # put at beginning
            the_list.context = context

            if parent_list_slug:
                # There's a parent list, so try to get it
                try:
                    parent_list = List.objects.get(slug=parent_list_slug, context=context, parent_list=None)
                except Exception as e:
                    # Parent list not found, so create it
                    parent_list = List()
                    parent_list.slug = parent_list_slug
                    parent_list.order = 0 # put at beginning
                    parent_list.context = context
                    parent_list.save()

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
    for group in [x.strip() for x in block.split('\n\n')]:
        group_response = {
            'list': None,
            'sublist': None,
            'context': None,
            'items': [],
        }

        for line in [x.strip() for x in group.split('\n') if x != '']:
            # If it starts with ::, it's a context
            if line[0:2] == '::':
                remainder = line[2:]

                # See if there's a list
                if '/' in remainder:
                    # Yes, there's a list
                    lists = remainder.split('/')

                    # Context
                    group_response['context'] = lists[0]

                    group_response['list'], group_response['sublist'] = parse_list_string('/'.join(lists[1:]))
                else:
                    # No list, just add the context
                    group_response['context'] = remainder
            elif line[0] == '/':
                # List (not a context)
                group_response['list'], group_response['sublist'] = parse_list_string(line)
            else:
                # Normal item

                # Get tags and notes
                label, tags, notes, starred, item_id = parse_item(line)

                group_response['items'].append({
                    'label': label,
                    'tags': tags,
                    'notes': notes,
                    'starred': starred,
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
            else:
                if block['context'] != None:
                    # Use inbox as default
                    b_list = get_or_create_list(b_context, 'inbox')

            # Get the number of items in b_list to use for ordering
            b_list_len = b_list.count_items()

            # Reorder existing items so the new ones show up in order
            b_num_items = len(b_items)
            list_items = b_list.get_active_items()
            for i in list_items:
                i.order += b_num_items
                i.save()

            # Add items to the specified context/list
            for i, item in enumerate(b_items):
                b_item = Item()
                b_item.parent_list = b_list
                b_item.text = item['label'].strip()

                if item['notes'] != '':
                    b_item.notes = item['notes']

                if item['starred']:
                    # Reorder the starred list
                    starred_items = Item.objects.filter(starred=True, checked=False).order_by('starred_order', 'parent_list__context__order', 'parent_list__order', 'parent_list__parent_list__order', 'order')

                    for i, starred_item in enumerate(starred_items):
                        starred_item.starred_order = i + 1
                        starred_item.save()

                    # And put this item at the top
                    b_item.starred_order = 0
                    b_item.starred = True

                b_item.order = i
                b_item.save()

                # Add tags
                for tag in item['tags']:
                    if tag != '':
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
    id = None
    starred = False

    # Check for starring at beginning or end
    if item[0:2] == '* ':
        starred = True
        item = item[2:]
    if item[-2:] == ' *':
        starred = True
        item = item[:-2]

    # Pull out notes if there
    if ':::' in item:
        item, notes = [x.strip() for x in item.split(':::')]

    # Now go through and get tags if any
    for token in item.split(' '):
        if token[0] == '#':
            # A tag
            tags.append(token[1:])
        elif token[0:3] == ":id":
            id = int(token[3:])
        else:
            # Not a tag
            label.append(token)

    return (' '.join(label).strip(), tags, notes, starred, id)

def get_all_contexts():
    return Context.objects.filter(status=Context.STATUS.active).order_by('slug')
