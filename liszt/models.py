from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from model_utils import Choices
from django.shortcuts import resolve_url


class Item(models.Model):
    text = models.TextField()
    order = models.IntegerField(default=0)
    parent_list = models.ForeignKey('List', related_name="items")
    checked = models.BooleanField(default=False)
    starred = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    tags = models.ManyToManyField('Tag', blank=True, related_name="items")

    def __str__(self):
        return self.text

    def get_toggle_uri(self):
        return resolve_url("toggle_item", self.id)

    def get_tags(self):
        """ Returns tags in form "#tag1 #tag2" """

        return ' '.join([t.get_display_slug() for t in self.tags.all()])

    def get_context(self):
        return self.parent_list.context or self.parent_list.parent_list.context

    def get_notes(self):
        if self.notes:
            return self.notes.replace('\\n', '<br/>')
        else:
            return ''

    def get_html(self, sortable=True, show_parents=False):
        html = '<li class="item" data-item-id="{}" data-item-uri="{}" data-star-item-uri="{}">\n'.format(self.id, resolve_url('toggle_item', self.id), resolve_url('toggle_starred_item', self.id))
        html += '\t<input id="item-{}" type="checkbox" {} />\n'.format(self.id, 'checked="true"' if self.checked else '')
        html += '\t<div class="wrapper">\n'
        html += '\t\t<label>{} {}</label>\n'.format(self.text, ' '.join([t.get_html() for t in self.tags.all()]))

        if self.notes:
            html += '\t\t<span class="subtitle">{}</span>\n'.format(self.get_notes())

        if show_parents:
            html += '<span class="subtitle"><a class="context" href="{}">{}</a>&thinsp;<a class="list" href="{}">{}</a></span>'.format(self.get_context().get_url(), self.get_context().get_display_slug(), self.parent_list.get_url(), self.parent_list.get_full_display_slug())

        html += '\t\t<div class="edit-controls" data-update-uri="{}">\n'.format(resolve_url('update_item', self.id))
        html += '\t\t\t<textarea>{}</textarea>\n'.format(self.text)

        html += '\t\t\t<div class="group list">\n'
        html += '\t\t\t\t<label>List</label>\n'
        html += '\t\t\t\t<input name="list" type="text" value="{}" />\n'.format(self.parent_list.get_full_display_slug())
        html += '\t\t\t</div>\n'

        html += '\t\t\t<div class="group tag">\n'
        html += '\t\t\t\t<label>Tags</label>\n'
        html += '\t\t\t\t<input name="tags" type="text" value="{}" />\n'.format(self.get_tags())
        html += '\t\t\t</div>\n'

        html += '\t\t\t<div class="group context">\n'
        html += '\t\t\t\t<label>Context</label>\n'
        html += '\t\t\t\t<input name="context" type="text" value="{}" />\n'.format(self.get_context().get_display_slug())
        html += '\t\t\t</div>\n'

        html += '\t\t\t<div class="buttons">\n'
        html += '\t\t\t\t<a class="save button" href="">Save</a>\n'
        html += '\t\t\t\t<a class="cancel button" href="">Cancel</a>\n'
        html += '\t\t\t</div>\n'
        
        html += '\t\t</div>\n'
        html += '\t</div>\n'

        html += '\t<span class="star{}">&#x2605;</span>\n'.format(' hide' if not self.starred else '')
        
        if sortable:
            html += '\t<span class="handle">=</span>\n'

        html += '</li>'

        return html


    class Meta:
        ordering = ['order']


class List(models.Model):
    STATUS = Choices(

        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    slug = models.CharField(max_length=100)

    order = models.IntegerField(default=0)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    parent_list = models.ForeignKey('List', related_name="sublists", blank=True, null=True)
    context = models.ForeignKey('Context', related_name="lists", blank=True, null=True)

    tags = models.ManyToManyField('Tag', blank=True, related_name="lists")

    def __str__(self):
        return self.slug

    def get_url(self):
        if self.parent_list:
            return resolve_url('list_detail', self.parent_list.context.slug, self.get_full_slug())
        else:
            return resolve_url('list_detail', self.context.slug, self.slug)

    def get_context(self):
        return self.context or self.parent_list.context

    def get_display_slug(self):
        return ':{}'.format(self.slug)

    def get_full_slug(self):
        if self.parent_list:
            # For sublists
            return '{}:{}'.format(self.parent_list.slug, self.slug)
        else:
            # Normal lists
            return self.slug

    def get_full_display_slug(self):
        return ':{}'.format(self.get_full_slug())

    def get_active_items(self):
        return self.items.filter(checked=False)

    def count_items(self):
        return len(self.get_active_items())

    def get_active_sublists(self):
        return self.sublists.filter(status='active')

    def count_sublists(self):
        return len(self.get_active_sublists())

    class Meta:
        ordering = ['order', 'slug']


class Context(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    slug = models.CharField(max_length=100)

    order = models.IntegerField(default=0)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)

    def __str__(self):
        return self.slug

    def get_url(self):
        return resolve_url('context_detail', self.slug)

    def get_display_slug(self):
        return "/{}".format(self.slug)

    def get_active_lists(self):
        return self.lists.filter(status='active', parent_list=None)

    def count_lists(self):
        return len(self.get_active_lists())

    class Meta:
        ordering = ['order', 'slug']


class Tag(models.Model):
    slug = models.CharField(max_length=100)

    def __str__(self):
        return self.slug

    def get_display_slug(self):
        return '#{}'.format(self.slug)

    def get_url(self):
        return resolve_url('tag', self.slug)

    def get_html(self):
        if self.slug != '':
            html = '<a class="tag" href="{}">{}</a>'.format(resolve_url('tag', self.slug), self.get_display_slug())
        else:
            html = ''
        return html

    def get_active_items(self):
        return self.items.filter(checked=False)

    def get_active_lists(self):
        return self.lists.filter(status='active')

    class Meta:
        ordering = ['slug']
