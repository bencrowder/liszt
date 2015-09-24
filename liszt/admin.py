from django.contrib import admin
from .models import Item, List, Context, Tag

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('checked', 'text', 'order', 'parent_list',)
    pass

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'order', 'parent_list', 'context',)
    pass

@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'order',)
    pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    pass
