from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

from liszt.models import Item, List, Context

from liszt.utils import process_payload, get_or_create_list

@login_required
def add_items(request):
    """ Adds a sequence of items. """

    payload = request.GET.get('payload', '').strip()
    key = request.GET.get('key', '')
    callback = request.GET.get('callback', '')

    # Make sure we have the secret key
    if key != settings.SECRET_KEY:
        return JsonResponse({})

    # Get default context/list
    default_context = Context.objects.filter(status='active').first()
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
