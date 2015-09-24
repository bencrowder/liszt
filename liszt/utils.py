from django.conf import settings
from liszt.models import Item, List, Context

def get_or_create_context(context_name):
    context = None

    # Try to get the context
    try:
        context = Context.objects.get(name=context_name)
    except Exception as e:
        # Not found, so create it
        try:
            context = Context()
            context.name = context_name
            context.save()
        except Exception as e:
            pass

    return context

def get_or_create_list(context, list_name, parent_list_name=None):
    # Get the list
    try:
        if parent_list_name:
            the_list = List.objects.get(name=list_name, parent_list__name=parent_list_name)
        else:
            the_list = List.objects.get(name=list_name)
    except Exception as e:
        # Not found, so create it
        try:
            the_list = List()
            the_list.name = list_name
            the_list.context = context

            if parent_list_name:
                # There's a parent list, so try to get it
                try:
                    parent_list = List.objects.get(name=parent_list_name)
                except Exception as e:
                    # Parent list not found, so create it
                    parent_list = List()
                    parent_list.name = parent_list_name
                    parent_list.context = context

                # Hook it up as the parent_list
                the_list.parent_list = parent_list

            the_list.save()
        except Exception as e:
            pass
    
    return the_list
