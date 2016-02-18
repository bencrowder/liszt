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
    starred_order = models.IntegerField(default=0)
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

        return ' '.join(['#{}'.format(t.slug) for t in self.tags.all()])

    def get_context(self):
        return self.parent_list.context or self.parent_list.parent_list.context

    def get_notes(self):
        if self.notes:
            return self.notes.replace('\\n', '<br/>')
        else:
            return ''

    def get_text_with_notes(self):
        response = self.text
        if self.notes and self.notes != '':
            response += ' ::: {}'.format(self.notes)

        return response

    def get_html(self, sortable=True, show_context=False, show_list=False, show_star=True):
        html = '<li class="item" data-item-id="{}" data-item-uri="{}" data-star-item-uri="{}">\n'.format(self.id, resolve_url('toggle_item', self.id), resolve_url('toggle_starred_item', self.id))
        html += '\t<input id="item-{}" type="checkbox" {} />\n'.format(self.id, 'checked="true"' if self.checked else '')
        html += '\t<div class="wrapper">\n'
        html += '\t\t<label>{}</label>\n'.format('{} {}'.format(self.text, ' '.join([t.get_html() for t in self.tags.all()])).strip())

        if self.notes:
            html += '\t\t<span class="subtitle notes">{}</span>\n'.format(self.get_notes())

        if show_context or show_list:
            html += '<span class="subtitle selector">'
            if show_context:
                html += '<a class="context" href="{}">{}</a>'.format(self.get_context().get_url(), self.get_context().get_display_slug())
            if show_context and show_list:
                html += '&thinsp;'
            if show_list:
                html += '<a class="list" href="{}">{}</a></span>'.format(self.parent_list.get_url(), self.parent_list.get_full_display_slug())
            html += '</span>'

        html += '\t\t<div class="edit-controls" data-update-uri="{}">\n'.format(resolve_url('update_item', self.id))
        html += '\t\t\t<textarea class="item-text">{}</textarea>\n'.format(self.get_text_with_notes())
        html += '\t\t\t<textarea class="item-metadata">{}{}\n:tags {}\n:id {}</textarea>\n'.format(self.get_context().get_display_slug(html=False), self.parent_list.get_full_display_slug(html=False), self.get_tags(), self.id)

        html += '\t\t\t<div class="buttons">\n'
        html += '\t\t\t\t<a class="save button" href="">Save</a>\n'
        html += '\t\t\t\t<a class="cancel button" href="">Cancel</a>\n'
        html += '\t\t\t</div>\n'

        html += '\t\t</div>\n'
        html += '\t</div>\n'

        if show_star:
            html += '\t<span class="star{}">&#x2605;</span>\n'.format(' hide' if not self.starred else '')

        if sortable:
            html += '\t<span class="handle">=</span>\n'

        html += '</li>'

        return html

    def get_starred_html(self):
        return self.get_html(sortable=True, show_context=True, show_list=True, show_star=False)


    class Meta:
        ordering = ['order']


class List(models.Model):
    STATUS = Choices(

        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    slug = models.CharField(max_length=100)

    order = models.IntegerField(default=0)
    starred_order = models.IntegerField(default=0)

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
            return resolve_url('list_detail', self.parent_list.context.slug, self.parent_list.slug, self.slug)
        else:
            return resolve_url('list_detail', self.context.slug, self.slug)

    def get_context(self):
        return self.context or self.parent_list.context

    def get_display_slug(self, html=True):
        if html:
            return '<span class="selector">/</span>{}'.format(self.slug)
        else:
            return '/{}'.format(self.slug)

    def get_full_slug(self, html=True):
        if self.parent_list:
            # For sublists
            if html:
                return '{}<span class="selector">/</span>{}'.format(self.parent_list.slug, self.slug)
            else:
                return '{}/{}'.format(self.parent_list.slug, self.slug)
        else:
            # Normal lists
            return self.slug

    def get_full_text_slug(self):
        return self.get_full_slug(html=False)

    def get_full_display_slug(self, html=True):
        if html:
            return '<span class="selector">/</span>{}'.format(self.get_full_slug())
        else:
            return '/{}'.format(self.get_full_slug(html=False))

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

    def get_display_slug(self, html=True):
        if html:
            return '<span class="selector">::</span>{}'.format(self.slug)
        else:
            return '::{}'.format(self.slug)

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
        return '<span class="selector">#</span>{}'.format(self.slug)

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
