from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from liszt.models import Item, List, Context

@login_required
def home(request):
    contexts = Context.objects.all()

    context = {
        'title': 'Home',
        'contexts': contexts,
        'pagetype': 'home',
        'key': settings.SECRET_KEY,
    }

    return render_to_response('home.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def tag(request, tag):
    # Get everything with that tag

    context = {
        'title': '#{} — Tag'.format(tag),
        'pagetype': 'tag',
        'key': settings.SECRET_KEY,
    }

    return render_to_response('tag.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def list_detail(request, context_slug, list_slug):
    # Split out sublist if it's there
    if ':' in list_slug:
        parent_list_slug, list_slug = list_slug.split(':')
    else:
        parent_list_slug = None

    # Get the parent list (if it's a sublist)
    if parent_list_slug:
        parent_list = List.objects.get(slug=parent_list_slug, context__slug=context_slug)
        the_list = List.objects.get(slug=list_slug, parent_list__slug=parent_list_slug)
    else:
        # Normal list
        parent_list = None
        the_list = List.objects.get(slug=list_slug, context__slug=context_slug)

    context = {
        'title': ':{}'.format(list_slug),
        'pagetype': 'list',
        'list': the_list,
        'key': settings.SECRET_KEY,
    }

    if parent_list:
        context['parent_list'] = parent_list

    return render_to_response('list.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def context_detail(request, context_slug):
    # Get the context
    the_context = Context.objects.get(slug=context_slug)

    context = {
        'title': '/{}'.format(context_slug),
        'pagetype': 'context',
        'ctext': the_context,
        'key': settings.SECRET_KEY,
    }

    return render_to_response('context.html',
                              context,
                              RequestContext(request),
                              )
