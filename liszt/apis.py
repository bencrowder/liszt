from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core import serializers

from liszt.models import Item, List, Context

from liszt.utils import process_payload, get_or_create_context, get_or_create_list

@login_required
def add_items(request):
    """ Adds a sequence of items. """

    if request.method == 'GET':
        payload = request.GET.get('payload', '').strip()
        key = request.GET.get('key', '')
        d_context = request.GET.get('context', None)
        d_list = request.GET.get('list', None)
        d_parent_list = request.GET.get('parent_list', None)
    elif request.method == 'POST':
        payload = request.POST.get('payload', '').strip()
        key = request.POST.get('key', '')
        d_context = request.POST.get('context', None)
        d_list = request.POST.get('list', None)
        d_parent_list = request.POST.get('parent_list', None)

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
    if d_list:
        default_list = get_or_create_list(default_context, d_list, d_parent_list)
    else:
        default_list = get_or_create_list(default_context, 'inbox')

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
def search(request):
    """ Searches. """

    query = request.GET.get('q', '').strip()

    contexts = Context.objects.filter(name__icontains=query, status='active')[:5]
    lists = List.objects.filter(name__icontains=query, status='active')[:5]
    items = Item.objects.filter(text__icontains=query, checked=False)[:5]

    # Serialize it
    contexts = [{'id': c.id, 'name': c.get_name(), 'url': c.get_url(), 'num_lists': c.count_lists()} for c in contexts]
    lists = [{'id': l.id, 'name': l.get_name(), 'url': l.get_url(), 'num_items': l.count_items(), 'num_lists': l.count_sublists()} for l in lists]
    items = [{'id': i.id, 'name': i.text, 'notes': i.get_notes(), 'checked': i.checked, 'toggle_uri': i.get_toggle_uri(), 'context_name': i.parent_list.context.get_name() or i.parent_list.parent_list.context.get_name(), 'context_url': i.parent_list.context.get_url() or i.parent_list.parent_list.context.get_url(), 'list_name': i.parent_list.get_full_name(), 'list_url': i.parent_list.get_url()} for i in items]

    response = {
        'contexts': contexts,
        'lists': lists,
        'items': items,
    }

    # Return JSON response
    return JsonResponse(response)

@login_required
def sort_things(request, type):
    """ Toggles an item's checked state. """

    key = request.POST.get('key', '')
    id_list = [int(x) for x in request.POST.get('ids', '').split(',') if x != '']
    print(id_list)

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    try:
        # Get the class we need
        types = {
            'item': Item,
            'list': List,
            'context': Context,
        }

        cls = types[type]

        # Get the matching objects
        for i, id in enumerate(id_list):
            thing = cls.objects.get(id=id)
            thing.order = i
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

