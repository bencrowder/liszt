from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect, resolve_url
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from liszt.models import Item, List, Context
from liszt.utils import get_all_contexts, get_list

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
def list_detail(request, context_slug, list_slugs):
    all_contexts = get_all_contexts()

    hidden = request.GET.get('hidden', None)

    # Process list slugs and get the list
    lists = list_slugs.split('/')
    cur_list = get_list(context_slug, lists)

    if cur_list:
        # Check if there's a parent
        if cur_list.parent_list:
            # Parent list
            parent_uri = resolve_url('list_detail', context_slug, cur_list.parent_list.slug)
        else:
            # No parent
            parent_uri = resolve_url('context_detail', context_slug)

        # Tell the list whether we're showing hidden items
        cur_list.hidden = hidden

        # Get the context
        ctx = Context.objects.get(slug=context_slug)

        # Get the parents
        parents = []
        parent_slug = None
        for list_slug in lists:
            c = List.objects.filter(slug=list_slug, parent_list__slug=parent_slug, context=ctx)[0]
            parents.append(c)
            parent_slug = list_slug

        context = {
            'title': '::{}/{} — Liszt'.format(context_slug, cur_list.get_full_text_slug()),
            'all_contexts': all_contexts,
            'context': ctx,
            'parents': parents,
            'pagetype': 'list',
            'list': cur_list,
            'key': settings.SECRET_KEY,
            'parent_uri': parent_uri,
        }

        return render_to_response('list.html',
                                context,
                                RequestContext(request),
                                )
    else:
        cur_list = None

        context = {
            'title': 'Not Found — Liszt',
            'all_contexts': all_contexts,
            'pagetype': 'list',
            'key': settings.SECRET_KEY,
        }

        return render_to_response('404.html',
                                context,
                                RequestContext(request),
                                )

@login_required
def context_detail(request, context_slug):
    all_contexts = get_all_contexts()

    # Get the context
    try:
        the_context = Context.objects.get(slug=context_slug)

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
    except Exception as e:
        context = {
            'title': 'Not Found — Liszt',
            'all_contexts': all_contexts,
            'pagetype': 'context',
            'key': settings.SECRET_KEY,
        }

        return render_to_response('404.html',
                                context,
                                RequestContext(request),
                                )
@login_required
def context_view(request, context_slug):
    all_contexts = get_all_contexts()

    # Get the context
    try:
        the_context = Context.objects.get(slug=context_slug)

        # Now get the main lists: current, upcoming, and inbox
        current = get_list(context_slug, ['current'])
        upcoming = get_list(context_slug, ['upcoming'])
        inbox = get_list(context_slug, ['inbox'])

        context = {
            'title': '::{} — Liszt'.format(context_slug),
            'pagetype': 'context',
            'ctext': the_context,
            'current': current,
            'upcoming': upcoming,
            'inbox': inbox,
            'all_contexts': all_contexts,
            'key': settings.SECRET_KEY,
            'parent_uri': resolve_url('home'),
        }

        return render_to_response('contextview.html',
                                context,
                                RequestContext(request),
                                )
    except Exception as e:
        context = {
            'title': 'Not Found — Liszt',
            'all_contexts': all_contexts,
            'pagetype': 'context',
            'key': settings.SECRET_KEY,
        }

        return render_to_response('404.html',
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

