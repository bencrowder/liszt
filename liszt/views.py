from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect, resolve_url
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from liszt.models import Item, List, Context
from liszt.utils import get_all_contexts

@login_required
def home(request):
    all_contexts = get_all_contexts()
    contexts = Context.objects.all()

    context = {
        'title': 'Liszt',
        'contexts': contexts,
        'all_contexts': all_contexts,
        'pagetype': 'home',
        'key': settings.SECRET_KEY,
    }

    return render_to_response('home.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def list_detail(request, context_slug, list_slug, sublist_slug=None):
    # Get the parent list (if it's a sublist)
    if sublist_slug:
        parent_list = List.objects.get(slug=list_slug, context__slug=context_slug, parent_list=None)
        the_list = List.objects.filter(slug=sublist_slug, context__slug=context_slug, parent_list__slug=list_slug).select_related('context').order_by('id')[0]

        parent_uri = resolve_url('list_detail', context_slug, parent_list.slug)
    else:
        # Normal list
        parent_list = None
        the_list = List.objects.filter(slug=list_slug, context__slug=context_slug, parent_list=None).select_related('context').order_by('id')[0]

        parent_uri = resolve_url('context_detail', context_slug)

    all_contexts = get_all_contexts()

    context = {
        'title': '::{}/{} — Liszt'.format(context_slug, the_list.get_full_text_slug()),
        'all_contexts': all_contexts,
        'pagetype': 'list',
        'list': the_list,
        'key': settings.SECRET_KEY,
        'parent_uri': parent_uri,
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

    all_contexts = get_all_contexts()

    context = {
        'title': '::{} — Liszt'.format(context_slug),
        'pagetype': 'context',
        'ctext': the_context,
        'all_contexts': all_contexts,
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('context.html',
                              context,
                              RequestContext(request),
                              )
@login_required
def starred(request):
    items = Item.objects.filter(starred=True, checked=False).order_by('starred_order', 'parent_list__context__order', 'parent_list__order', 'parent_list__parent_list__order', 'order').select_related('parent_list', 'parent_list__context')

    all_contexts = get_all_contexts()

    context = {
        'title': 'Starred — Liszt',
        'items': items,
        'all_contexts': all_contexts,
        'pagetype': 'starred',
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('starred.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def overview(request):
    all_contexts = get_all_contexts()
    entries = []

    contexts = Context.objects.filter(status=Context.STATUS.active).order_by('order')

    for c in contexts:
        entries.append({
            'url': resolve_url('context_detail', c.slug),
            'label': c.get_display_slug(),
            'indent': 0,
            'type': 'context',
        })

        for l in c.get_active_lists():
            entries.append({
                'url': resolve_url('list_detail', c.slug, l.slug),
                'label': l.get_full_display_slug(),
                'indent': 1,
                'type': 'list',
                'num_items': l.count_items(),
            })

            for s in l.get_active_sublists():
                entries.append({
                    'url': resolve_url('list_detail', c.slug, '{}:{}'.format(l.slug, s.slug)),
                    'label': s.get_display_slug(),
                    'indent': 2,
                    'type': 'list sublist',
                    'num_items': s.count_items(),
                })

    review_lists = List.objects.filter(for_review=True, status=List.STATUS.active).order_by('order')

    context = {
        'title': 'Overview — Liszt',
        'entries': entries,
        'review_lists': review_lists,
        'all_contexts': all_contexts,
        'pagetype': 'overview',
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('overview.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def review(request):
    all_contexts = get_all_contexts()

    context = {
        'title': 'Review — Liszt',
        'all_contexts': all_contexts,
        'pagetype': 'review',
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('review.html',
                              context,
                              RequestContext(request),
                              )

