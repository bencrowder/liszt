from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, redirect, resolve_url
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from liszt.models import Item, List, Context, Tag
from liszt.utils import get_all_contexts

@login_required
def home(request):
    all_contexts = get_all_contexts()

    tags = [x.get_html() for x in Tag.objects.all()]

    context = {
        'title': 'Home',
        'all_contexts': all_contexts,
        'tags': tags,
        'pagetype': 'home',
        'key': settings.SECRET_KEY,
    }

    return render_to_response('home.html',
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

        parent_uri = resolve_url('list_detail', context_slug, parent_list.slug)
    else:
        # Normal list
        parent_list = None
        the_list = List.objects.get(slug=list_slug, context__slug=context_slug)

        parent_uri = resolve_url('context_detail', context_slug)

    all_contexts = get_all_contexts()

    context = {
        'title': ':{}'.format(list_slug),
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
        'title': '/{}'.format(context_slug),
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
def tag(request, tag):
    # Get the tag
    tag = Tag.objects.get(slug=tag)

    items = tag.get_active_items()
    lists = tag.get_active_lists()
    contexts = {}
    all_contexts = get_all_contexts()

    def get_context(the_list):
        # Get the context and initialize it
        this_context = the_list.context or the_list.parent_list.context

        if this_context.slug not in contexts:
            # Modify the parent function's contexts variable
            contexts[this_context.slug] = {
                'context': this_context,
                'lists': [],
                'items': [],
            }

        return this_context

    # Go through the lists first
    for l in lists:
        # Get the context and initialize it
        this_context = get_context(l)

        # And append the list
        contexts[this_context.slug]['lists'].append(l)

    # Now go through the items
    for i in items:
        # Get the context and initialize it
        this_context = get_context(i.parent_list)

        # And append the list
        contexts[this_context.slug]['items'].append(i.get_html(show_list=True))

    # Sort contexts by context order
    sorted_contexts = [contexts[k] for k in sorted(contexts, key=lambda k: contexts[k]['context'].order)]

    context = {
        'title': '#{} — Tag'.format(tag),
        'tag': tag,
        'all_contexts': sorted_contexts,
        'pagetype': 'tag',
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('tag.html',
                              context,
                              RequestContext(request),
                              )

@login_required
def starred(request):
    items = Item.objects.filter(starred=True, checked=False).order_by('parent_list__order', 'parent_list__parent_list__order', 'order')
    contexts = {}
    all_contexts = get_all_contexts()

    def get_context(the_list):
        # Get the context and initialize it
        this_context = the_list.context or the_list.parent_list.context

        if this_context.slug not in contexts:
            # Modify the parent function's contexts variable
            contexts[this_context.slug] = {
                'context': this_context,
                'lists': [],
                'items': [],
            }

        return this_context

    # Go through the lists first
    #for l in lists:
    #    # Get the context and initialize it
    #    this_context = get_context(l)

    #    # And append the list
    #    contexts[this_context.slug]['lists'].append(l)

    # Now go through the items
    for i in items:
        # Get the context and initialize it
        this_context = get_context(i.parent_list)

        # And append the list
        contexts[this_context.slug]['items'].append(i.get_html(show_list=True, sortable=False))

    # Sort contexts by context order
    sorted_contexts = [contexts[k] for k in sorted(contexts, key=lambda k: contexts[k]['context'].order)]

    context = {
        'title': 'Starred',
        'contexts': sorted_contexts,
        'all_contexts': all_contexts,
        'pagetype': 'starred',
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('tag.html',
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

    context = {
        'title': 'Overview',
        'entries': entries,
        'all_contexts': all_contexts,
        'pagetype': 'overview',
        'key': settings.SECRET_KEY,
        'parent_uri': resolve_url('home'),
    }

    return render_to_response('overview.html',
                              context,
                              RequestContext(request),
                              )

