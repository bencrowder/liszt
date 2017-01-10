from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField
from django.utils import timezone
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
    linked_list = models.ForeignKey('List', related_name="linked_items", null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True, default=timezone.now)

    def __str__(self):
        return self.text

    def get_toggle_uri(self):
        return resolve_url("toggle_item", self.id)

    def get_context(self):
        return self.parent_list.context or self.parent_list.parent_list.context

    def get_notes(self):
        if self.notes:
            return self.notes.replace('\\n', '<br/>')
        else:
            items = self.linked_list.get_active_items() if self.linked_list else None

            if self.linked_list and items and items.count() > 0:
                return self.linked_list.get_active_items().first().text
            else:
                return ''

    def get_target_date(self):
        if self.target_date:
            return self.target_date
        else:
            return ''

    def get_linked_list(self):
        if self.linked_list:
            return {
                'label': '{}{}'.format(self.linked_list.context.get_display_slug(), self.linked_list.get_full_display_slug()),
                'url': self.linked_list.get_url(),
            }
        else:
            return {}

    def get_text_with_notes(self):
        response = self.text
        if self.notes and self.notes != '':
            response += ' ::: {}'.format(self.notes)

        return response

    def get_html(self, sortable=True, show_context=False, show_list=False, editable=True):
        item_classes = []
        display_text = self.text

        if self.text[0:2] == '! ':
            item_classes.append('urgent')
            display_text = self.text[2:].strip()

        if "@waiting" in self.text or (self.notes and "@waiting" in self.notes):
            item_classes.append('waiting')

        html = '<li class="item {}" data-item-id="{}" data-item-uri="{}" data-star-item-uri="{}">\n'.format(' '.join(item_classes), self.id, resolve_url('toggle_item', self.id), resolve_url('toggle_starred_item', self.id))
        html += '\t<div class="checkbox {}" id="item-{}"></div>\n'.format('checked' if self.checked else '', self.id)
        html += '\t<div class="wrapper">\n'
        html += '\t\t<label>{}</label>\n'.format(display_text)

        if show_context or show_list:
            html += '<span class="subtitle selector">'
            if show_context:
                html += '<a class="context" href="{}">{}</a>'.format(self.get_context().get_url(), self.get_context().get_display_slug())
            if show_context and show_list:
                html += '&thinsp;'
            if show_list:
                html += '<a class="list" href="{}">{}</a></span>'.format(self.parent_list.get_url(), self.parent_list.get_full_display_slug())
            html += '</span>'

        notes = self.get_notes()
        if notes or self.target_date:
            html += '\t\t<span class="subtitle notes">'
            html += notes
            if self.target_date:
                if notes:
                    html += ' &mdash; '
                html += '{}'.format(self.get_target_date())
            html += '</span>\n'

        if self.linked_list:
            ll = self.get_linked_list()
            html += '\t\t<span class="subtitle list"><a href="{}">{}</a></span>\n'.format(ll['url'], ll['label'])

        html += '\t\t<div class="edit-controls" data-update-uri="{}">\n'.format(resolve_url('update_item', self.id))
        html += '\t\t\t<textarea class="item-text">{}</textarea>\n'.format(self.get_text_with_notes())

        html += '\t\t\t<textarea class="item-metadata">'
        lines = []
        lines.append('{}{}'.format(self.get_context().get_display_slug(html=False), self.parent_list.get_full_display_slug(html=False)))
        lines.append(':id {}'.format(self.id))
        if self.target_date:
            lines.append(':target {}'.format(self.target_date))
        if self.linked_list:
            lines.append(':link {}{}\n'.format(self.linked_list.context.get_display_slug(html=False), self.linked_list.get_full_display_slug(html=False)))
        html += '\n'.join(lines)
        html += '</textarea>\n'

        html += '\t\t\t<div class="meta">\n'
        html += '\t\t\t\t<div class="right"><span class="star {}"></span></div>\n'.format('selected' if self.starred else '')
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

    def get_starred_html(self):
        return self.get_html(sortable=True, show_context=True, show_list=True)


    class Meta:
        ordering = ['order']


class List(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    slug = models.CharField(max_length=100)

    order = models.IntegerField(default=0)
    starred = models.BooleanField(default=False)
    starred_order = models.IntegerField(default=0)

    for_review = models.BooleanField(default=False)

    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    parent_list = models.ForeignKey('List', related_name="sublists", blank=True, null=True)
    context = models.ForeignKey('Context', related_name="lists", blank=True, null=True)

    def __str__(self):
        return self.slug

    def get_url(self):
        if self.parent_list:
            slugs = []
            p = self.parent_list
            while p:
                slugs.append(p.slug)
                p = p.parent_list
            slugs.reverse()
            slugs.append(self.slug)

            return resolve_url('list_detail', self.context.slug, '/'.join(slugs))
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
            parents = []
            p = self.parent_list
            while p:
                parents.append(p.slug)
                p = p.parent_list

            # For sublists
            if html:
                parent_html = '<span class="selector">/</span>'.join(parents)
                return '{}<span class="selector">/</span>{}'.format(parent_html, self.slug)
            else:
                parent_text = '/'.join(parents)
                return '{}/{}'.format(parent_text, self.slug)
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
        hidden = getattr(self, 'hidden', None)
        if hidden is not None and hidden:
            return self.items.all().order_by('checked', 'order')
        else:
            return self.items.filter(checked=False)

    def count_items(self):
        return len(self.get_active_items())

    def get_active_sublists(self):
        return self.sublists.filter(status='active')

    def count_sublists(self):
        return len(self.get_active_sublists())

    def get_html(self, sortable=True, show_context=False, show_list=False):
        num_items = self.count_items()
        num_sublists = self.count_sublists()

        html = '<li class="list" data-object-id="{}" data-star-list-uri="{}">\n'.format(self.id, resolve_url('toggle_starred_list', self.id))
        html += '\t<div class="wrapper">\n'
        html += '\t\t<a href="{}">{}</a>\n'.format(self.get_url(), self.get_display_slug())

        html += '\t\t<span class="subtitle">'
        html += '{} item{}'.format(num_items, 's' if num_items != 1 else '')
        if num_sublists > 0:
            html += ', {} list{}'.format(num_sublists, 's' if num_sublists != 1 else '')
        html += '</span>\n'

        html += '\t\t<div class="edit-controls" data-update-uri="{}">\n'.format(resolve_url('update_list', self.id))
        html += '\t\t\t<textarea class="list-name">/{}</textarea>\n'.format(self.slug)
        html += '\t\t\t<textarea class="list-metadata">{}{}\n:id {}</textarea>\n'.format(self.get_context().get_display_slug(html=False), self.parent_list.get_full_display_slug(html=False) if self.parent_list else '', self.id)
        html += '\t\t\t<div class="meta">\n'
        html += '\t\t\t\t<div class="left"><span><input type="checkbox" name="for-review" class="for-review" {}/> <label for="for-review">Review</label></div></span> <span><input type="checkbox" name="archive" class="archive" /> <label for="archive">Archive</label></span>\n'.format('checked' if self.for_review else '')
        html += '\t\t\t\t<div class="right"><span class="star {}"></span></div>\n'.format('selected' if self.starred else '')
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

    def get_starred_html(self):
        return self.get_html(sortable=True, show_context=True, show_list=True)

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


