from django.contrib import admin
from .models import Item, List, Context, Tag

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'checked', 'order', 'parent_list',)
    list_display_links = ('text',)
    pass

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('slug', 'status', 'order', 'parent_list', 'context',)
    pass

@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ('slug', 'status', 'order',)
    pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug',)
    pass
