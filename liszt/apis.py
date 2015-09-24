from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

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
