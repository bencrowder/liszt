from django.conf import settings
from liszt.models import Item, List, Context

def parse_list_string(list_string):
    """
    Takes a string like "projects/liszt" or "/work/services/redesign/tools"
    and returns it in list form.
    """

    # Slice off initial / if it's there
    if list_string[0] == '/':
        list_string = list_string[1:]

    return list_string.split('/')

def parse_selector(selector):
    context = None
    the_list = None
    the_sublist = None

    # Context
    if selector[0:2] == '::':
        # Initial context, strip off ::
        items = selector[2:].split('/')
        context = items[0]
        lists = items[1:]
    else:
        # No context, split lists
        lists = parse_list_string(selector)

    return context, lists

def get_context(context_slug):
    context = None

    # Try to get the context
    try:
        context = Context.objects.get(slug=context_slug)
    except Exception as e:
        pass

    return context

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

def get_list(context_slug, lists):
    # Check for empty lists
    if len(lists) == 0:
        return None

    cur_list = None
    parent_slug = None
    parent_list = None
    parent_id = None

    for list_slug in lists:
        try:
            if parent_slug:
                parent_list = List.objects.filter(slug=parent_slug, id=parent_id, context__slug=context_slug).select_related('context')[0]
                cur_list = List.objects.filter(slug=list_slug, parent_list=parent_list, context__slug=context_slug).select_related('context')[0]
            else:
                cur_list = List.objects.filter(slug=list_slug, parent_list=None, context__slug=context_slug).select_related('context')[0]

            # Now set it to be the parent of the next list
            parent_slug = list_slug
            parent_id = cur_list.id
        except Exception as e:
            print("Couldn't find list", list_slug, "exception=", e)

    # At this point, cur_list is the list we want to return
    return cur_list

def get_or_create_list(context, lists):
    # Check for empty lists
    if len(lists) == 0:
        return None

    parent_slug = None
    parent_list = None
    parent_id = None

    for list_slug in lists:
        try:
            if parent_slug:
                parent_list = List.objects.filter(slug=parent_slug, id=parent_id, context=context)[0]
                cur_list = List.objects.filter(slug=list_slug, parent_list=parent_list, context=context)[0]
            else:
                cur_list = List.objects.filter(slug=list_slug, parent_list=None, context=context)[0]
        except Exception as e:
            # Reorder existing lists so the new one shows up in order
            for index, lst in enumerate(List.objects.filter(context=context, parent_list=parent_list)):
                lst.order = index + 1
                lst.save()

            try:
                # Create a new list
                cur_list = List()
                cur_list.slug = list_slug
                cur_list.order = 0 # put at beginning
                cur_list.context = context

                if parent_list:
                    cur_list.parent_list = parent_list

                # Actually create it
                cur_list.save()
            except Exception as e:
                print("Couldn't create list", e)

        # Now set it to be the parent of the next list
        parent_slug = list_slug
        parent_id = cur_list.id

    # At this point, cur_list is the list we want to return
    return cur_list

def parse_block(block):
    """
    Parse a block (a sequence of items with/without list/context specifiers.
    """
    response = []

    # Split into groups by newlines
    for group in [x.strip() for x in block.split('\n\n')]:
        group_response = {
            'lists': None,
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
                    items = remainder.split('/')
                    group_response['lists'] = parse_list_string('/'.join(items[1:]))
                    group_response['context'] = items[0]
                else:
                    # No list, just add the context
                    group_response['context'] = remainder
            elif line[0] == '/':
                # List (not a context)
                group_response['lists'] = parse_list_string(line)
            else:
                # Normal item

                # Get info and notes
                label, notes, starred, item_id = parse_item(line)

                group_response['items'].append({
                    'label': label,
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
        print("block", block)
        try:
            # Clear things out
            b_context = default_context
            b_list = default_list
            b_items = block['items']

            # Set the context if it's there, otherwise use default
            if block['context'] is not None:
                b_context = get_or_create_context(block['context'])

            # Set the list if it's there, otherwise use default
            if block['lists'] is not None:
                b_list = get_or_create_list(b_context, block['lists'])
            else:
                if block['context'] != None:
                    # Use inbox as default
                    b_list = get_or_create_list(b_context, ['inbox'])

            # Get the number of items in b_list to use for ordering
            b_list_len = b_list.count_items()

            # Reorder existing items so the new ones show up in order
            b_num_items = len(b_items)
            list_items = b_list.get_active_items()
            for index, item in enumerate(list_items):
                item.order = b_num_items + index
                item.save()

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

        except Exception as e:
            status = 'error'
            message = e

    return status, message

def parse_item(item):
    """ Parses a line. Returns tuple with string and notes. """
    label = []
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

    # Now go through and get metadata if any
    for token in item.split(' '):
        if token[0:3] == ":id":
            id = int(token[3:])
        else:
            # Not metadata
            label.append(token)

    return (' '.join(label).strip(), notes, starred, id)

def get_all_contexts():
    return Context.objects.filter(status=Context.STATUS.active).order_by('slug').values()
