from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from liszt.models import Item, List, Context

from liszt.utils import *

@csrf_exempt
def add_items(request):
    """ Adds a sequence of items. """

    if request.method == 'GET':
        payload = request.GET.get('payload', '').strip()
        key = request.GET.get('key', '')
        d_context = request.GET.get('context', None)
        d_lists = request.GET.get('lists', None)
    elif request.method == 'POST':
        payload = request.POST.get('payload', '').strip()
        key = request.POST.get('key', '')
        d_context = request.POST.get('context', None)
        d_lists = request.POST.get('lists', None)

    callback = request.GET.get('callback', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    # Get default context/list
    if d_context:
        default_context = get_or_create_context(d_context)
    else:
        # Get the first active context
        default_context = Context.objects.filter(status='active').first()

    # Get default list
    if d_lists:
        lists = d_lists.split(',')
        default_list = get_or_create_list(default_context, lists)
    else:
        default_list = get_or_create_list(default_context, ['inbox'])

    # Add the sequence
    status, message = process_payload(payload, default_context, default_list)

    response = {
        'status': status,
        'message': message,
    }

    if callback:
        # Redirect to callback
        response = HttpResponse("", status=302)
        response['Location'] = callback
        return response
    else:
        # Return JSON response
        return JsonResponse(response)

@login_required
def toggle_item(request, item_id):
    """ Toggles an item's checked state. """

    key = request.GET.get('key', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    try:
        item = Item.objects.get(id=item_id)
        item.checked = not item.checked
        item.save()

        status = 'success'
        message = ''
    except Exception as e:
        status = 'error'
        message = e

    response = {
        'status': status,
        'message': message,
    }

    # Return JSON response
    return JsonResponse(response)

@login_required
def toggle_starred_item(request, item_id):
    """ Toggles an item's starred state. """

    key = request.GET.get('key', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    try:
        item = Item.objects.get(id=item_id)
        item.starred = not item.starred

        # If starring the item, put it at the top of the list and reorder
        if item.starred:
            # Reorder the list
            starred_items = Item.objects.filter(starred=True, checked=False).order_by('starred_order', 'parent_list__context__order', 'parent_list__order', 'parent_list__parent_list__order', 'order')

            for i, starred_item in enumerate(starred_items):
                starred_item.starred_order = i + 1
                starred_item.save()

            # And put this item at the top
            item.starred_order = 0

        item.save()

        status = 'success'
        message = ''
    except Exception as e:
        status = 'error'
        message = e

    response = {
        'status': status,
        'message': message,
    }

    # Return JSON response
    return JsonResponse(response)

@login_required
def toggle_starred_list(request, listid):
    """ Toggles an list's starred state. """

    key = request.GET.get('key', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    try:
        list = List.objects.get(id=list_id)
        list.starred = not list.starred

        # If starring the list, put it at the top of the starred list and reorder
        if list.starred:
            # Reorder the list
            starred_lists = List.objects.filter(starred=True, status=List.STATUS.active).order_by('starred_order', 'parent_list__context__order', 'parent_list__order', 'order')

            for i, starred_list in enumerate(starred_lists):
                starred_list.starred_order = i + 1
                starred_list.save()

            # And put this item at the top
            list.starred_order = 0

        list.save()

        status = 'success'
        message = ''
    except Exception as e:
        status = 'error'
        message = e

    response = {
        'status': status,
        'message': message,
    }

    # Return JSON response
    return JsonResponse(response)

@login_required
def search(request):
    """ Searches. """

    query = request.GET.get('q', '').strip()

    contexts = []
    lists = []
    items = []
    ctext = None

    # If you search for something like work/inbox, prepend ::
    if '/' in query and query[0] != ':':
        query = '::{}'.format(query)

    # Selector
    if query[0] == ':':
        the_context, the_list, the_sublist = parse_selector(query)

        if the_context:
            # Yes context
            if the_list:
                # List specified, so get exact context
                try:
                    ctext = Context.objects.get(slug=the_context, status='active')
                except:
                    return JsonResponse({})
            else:
                # Get list of contexts that match
                contexts = Context.objects.filter(slug__istartswith=the_context, status='active')[:5]

        if the_list:
            # List specified
            if ctext:
                # Context specified
                lists = List.objects.filter(slug__istartswith=the_list, context=ctext, status='active')[:5]
            else:
                # Context not specified
                lists = List.objects.filter(slug__istartswith=the_list, status='active')[:5]

        if the_sublist:
            # Sublist specified
            if ctext:
                # Context specified
                lists = List.objects.filter(slug__istartswith=the_sublist, parent_list__slug=the_list, context=ctext, status='active')[:5]
            else:
                # Context not specified
                lists = List.objects.filter(slug__istartswith=the_sublist, parent_list__slug=the_list, status='active')[:5]
    else:
        contexts = Context.objects.filter(slug__icontains=query, status='active')[:5]
        lists = List.objects.filter(slug__icontains=query, status='active')[:5]
        items = Item.objects.filter(text__icontains=query, checked=False)[:5]

    # Serialize it
    try:
        contexts = [{'id': c.id, 'slug': c.get_display_slug(), 'url': c.get_url(), 'num_lists': c.count_lists()} for c in contexts]
        lists = [{'id': l.id, 'slug': l.get_display_slug(), 'url': l.get_url(), 'num_items': l.count_items(), 'num_lists': l.count_sublists(), 'context_slug': l.get_context().get_display_slug(), 'context_url': l.get_context().get_url(), 'parent_list_slug': l.parent_list.get_display_slug() if l.parent_list else None, 'parent_list_url': l.parent_list.get_url() if l.parent_list else None} for l in lists]
        items = [{'id': i.id, 'html': i.get_html(sortable=False, show_context=True, show_list=True), 'name': i.text, 'notes': i.get_notes(), 'checked': i.checked, 'toggle_uri': i.get_toggle_uri(), 'context_slug': i.get_context().get_display_slug(), 'context_url': i.get_context().get_url(), 'list_slug': i.parent_list.get_full_display_slug(), 'list_url': i.parent_list.get_url()} for i in items]
    except Exception as e:
        print(e)

    response = {
        'contexts': contexts,
        'lists': lists,
        'items': items,
    }

    # Return JSON response
    return JsonResponse(response)

@login_required
def sort_things(request, type):
    """ Sorts contexts, lists, and items. """

    key = request.POST.get('key', '')
    list_slug = request.POST.get('list', '')
    id_list = [int(x) for x in request.POST.get('ids', '').split(',') if x != '']

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    try:
        # Get the class we need
        types = {
            'item': Item,
            'list': List,
            'context': Context,
            'starred': Item,
        }

        cls = types[type]

        # Get the matching objects
        for i, id in enumerate(id_list):
            thing = cls.objects.get(id=id)

            if type == 'starred':
                thing.starred_order = i
            else:
                thing.order = i

            if list_slug != '':
                # Possibly dragging between lists in contextview
                ctx = thing.parent_list.context
                new_list = List.objects.filter(slug=list_slug, context=ctx)[0]
                thing.parent_list = new_list

            thing.save()

        status = 'success'
        message = ''
    except Exception as e:
        status = 'error'
        message = e

    response = {
        'status': status,
        'message': message,
    }

    # Return JSON response
    return JsonResponse(response)

@login_required
def update_item(request, item_id):
    """ Updates an item. """

    key = request.POST.get('key', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    new_text = request.POST.get('text', '').strip()
    new_selector = request.POST.get('selector', '').strip()
    new_id = request.POST.get('id', '').strip()
    new_target_date = request.POST.get('target', '').strip()
    new_linked_list = request.POST.get('link', '').strip()

    # Review mode
    review_mode = request.POST.get('review_mode', False)
    if review_mode:
        try:
            item = Item.objects.get(id=item_id)

            checked = request.POST.get('checked', None)
            if checked == 'false':
                checked = False
            item.checked = checked

            starred = request.POST.get('starred', None)
            if starred == 'false':
                starred = False
            item.starred = starred

            someday = request.POST.get('someday', False)
            if someday != 'false' and someday != False:
                someday_list = get_or_create_list(item.parent_list.context, ['someday'])
                item.parent_list = someday_list

            to_list = request.POST.get('to_list', '')
            if to_list != '':
                the_context, the_lists = parse_selector(to_list)

                the_context = get_or_create_context(the_context)
                to_list = get_or_create_list(the_context, the_lists)

                if to_list != item.parent_list:
                    item.parent_list = to_list
                    item.order = -1

            item.save()

            response = {
                'status': 'success',
                'message': '',
            }

        except Exception as e:
            response = {
                'status': 'error',
                'message': e,
            }
            print(e)

        # Return JSON response
        return JsonResponse(response)

    new_context, new_lists = parse_selector(new_selector)

    try:
        item = Item.objects.get(id=item_id)

        # Update the text if it's changed
        response = parse_item(new_text)

        if 'label' in response and response['label'] != '' and item.text != response['label']:
            item.text = response['label']

        # Update the notes
        if 'notes' in response and response['notes']:
            item.notes = response['notes']
        else:
            item.notes = None

        # Update starred
        if 'starred' in response and response['starred']:
            item.starred = response['starred']
        else:
            item.starred = False

        # Get target date
        if new_target_date != '' or ('target_date' in response and response['target_date']):
            if new_target_date:
                item.target_date = new_target_date
            else:
                item.target_date = response['target_date']
        else:
            item.target_date = None

        # Get linked list
        if new_linked_list != '' or ('linked_list' in response and response['linked_list']):
            if new_linked_list:
                sel = new_linked_list
            else:
                sel = response['linked_list']

            linked_context, linked_lists = parse_selector(sel)
            item.linked_list = get_list(linked_context, linked_lists)
        else:
            item.linked_list = None

        # Get or create the context
        if new_context != '':
            # Strip off initial /
            if new_context[0] == '/':
                new_context = new_context[1:]

            ctx = get_or_create_context(new_context)
        else:
            # Get it from the item
            ctx = item.get_context()

        # Get or create the list
        if len(new_lists) > 0 and new_lists is not None:
            lst = get_or_create_list(ctx, new_lists)

            # Assign
            item.parent_list = lst

        # Save it
        item.save()

        status = 'success'
        message = ''
    except Exception as e:
        status = 'error'
        message = e

    response = {
        'status': status,
        'message': message,
    }

    if status == 'success':
        response['item'] = {
            'label': item.text,
            'notes': item.get_notes(),
            'starred': item.starred,
        }

        if item.linked_list:
            response['linked_list'] = '{}{}'.format(item.linked_list.context.get_display_slug(), item.linked_list.get_full_display_slug(html=False))

        if item.target_date:
            response['target_date'] = item.target_date

    # Return JSON response
    return JsonResponse(response)

@login_required
def update_list(request, list_id):
    """ Updates a list. """

    key = request.POST.get('key', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    new_name = request.POST.get('name', '').strip()
    new_selector = request.POST.get('selector', '').strip()
    new_id = request.POST.get('id', '').strip()
    starred = request.POST.get('starred', False)
    for_review = request.POST.get('for_review', False)
    archive = request.POST.get('archive', False)

    if starred == 'false':
        starred = False
    else:
        starred = True

    if for_review == 'false':
        for_review = False
    else:
        for_review = True

    if archive == 'false':
        archive = False
    else:
        archive = True

    new_context, new_lists = parse_selector(new_selector)

    try:
        the_list = List.objects.get(id=list_id)

        if archive:
            # Archive the list
            the_list.status = List.STATUS.archived
            the_list.save()

            return JsonResponse({})

        # Update the text if it's changed
        if new_name != '' and the_list.slug != new_name:
            # Strip off initial /
            if new_name[0] == '/':
                new_name = new_name[1:]

            the_list.slug = new_name

        # Update starred
        the_list.starred = starred

        # Update for review
        the_list.for_review = for_review

        # Get or create the context
        if new_context != '':
            # Strip off initial /
            if new_context[0] == '/':
                new_context = new_context[1:]

            ctx = get_or_create_context(new_context)

            # Update order (since we're changing contexts)
            the_list.order = 0

            # Set the new context
            the_list.context = ctx
        else:
            # Get it from the list
            ctx = the_list.get_context()

        # Get or create the list
        if len(new_lists) > 0 and new_lists is not None:
            lst = get_or_create_list(ctx, new_lists)

            # Assign
            the_list.parent_list = lst

        # Save it
        the_list.save()

        status = 'success'
        message = ''

        response = {
            'status': status,
            'message': message,
            'list': {
                'slug': the_list.slug,
                'for_review': the_list.for_review,
                'starred': the_list.starred,
            },
        }

        # Return JSON response
        return JsonResponse(response)
    except Exception as e:
        status = 'error'
        message = e

        response = {
            'status': status,
            'message': message,
        }

        # Return JSON response
        return JsonResponse(response, status=500)

@login_required
def get_review_items(request):
    """ Returns a list of items in all the for_review lists. """

    key = request.GET.get('key', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    try:
        items = Item.objects.filter(parent_list__for_review=True, checked=False)
        items = items.select_related('parent_list', 'parent_list__context', 'parent_list__parent_list')
        items = items.order_by('parent_list__order', 'parent_list__context__order')

        # Sort into contexts
        contexts = {}
        for item in items:
            # Extract slugs
            context_slug = item.parent_list.context.slug
            list_slug = item.parent_list.slug
            if item.parent_list.parent_list:
                sublist_slug = list_slug
                list_slug = item.parent_list.parent_list.slug

            if context_slug not in contexts:
                contexts[context_slug] = { 'order': item.parent_list.context.order, 'lists': {} }
            
            if list_slug not in contexts[context_slug]['lists']:
                contexts[context_slug]['lists'][list_slug] = { 'order': item.parent_list.order, 'items': {} }

            contexts[context_slug]['lists'][list_slug]['items'][item.order] = item

        # Now sort and flatten the list
        flattened_items = []

        sorted_contexts = sorted(contexts, key=lambda slug: contexts[slug]['order'])
        for c in sorted_contexts:
            # Sort lists
            sorted_lists = sorted(contexts[c]['lists'], key=lambda k: contexts[c]['lists'][k]['order'])

            for l in sorted_lists:
                the_list = contexts[c]['lists'][l]
                sorted_items = sorted(the_list['items'])

                for item in sorted_items:
                    flattened_items.append(the_list['items'][item])

        # Serialize it
        items = [{'id': i.id, 'html': i.get_html(sortable=False, show_context=True, show_list=True), 'name': i.text, 'notes': i.get_notes(), 'checked': i.checked, 'starred': i.starred, 'toggle_uri': i.get_toggle_uri(), 'context_slug': i.get_context().get_display_slug(), 'context_url': i.get_context().get_url(), 'list_slug': i.parent_list.get_full_display_slug(), 'list_url': i.parent_list.get_url(), 'order': '{}{}-{}'.format(i.get_context().order, i.parent_list.order, i.order)} for i in flattened_items]

        status = 'success'
        message = ''
    except Exception as e:
        status = 'error'
        message = e

    response = {
        'status': status,
        'message': message,
    }

    if status == 'success':
        response['items'] = items

    # Return JSON response
    return JsonResponse(response)
