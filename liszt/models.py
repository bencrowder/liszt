from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from model_utils import Choices

class Item(models.Model):
    text = models.TextField()
    order = models.IntegerField(default=0)
    parent_list = models.ForeignKey('List', related_name="items")
    checked = models.BooleanField(default=False)
    # tags

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['order']


class List(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)

    order = models.IntegerField(default=0)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    parent_list = models.ForeignKey('List', related_name="sublists", blank=True, null=True)
    context = models.ForeignKey('Context', related_name="lists", blank=True, null=True)

    # Tags

    def __str__(self):
        return self.name

    def get_name(self):
        return ":{}".format(self.name)

    def get_full_slug(self):
        if self.parent_list:
            # For sublists
            return '{}:{}'.format(self.parent_list.slug, self.slug)
        else:
            # Normal lists
            return self.slug

    def get_active_items(self):
        return self.items.filter(checked=False)

    def count_items(self):
        return len(self.get_active_items())

    def get_active_sublists(self):
        return self.sublists.filter(status=active)

    def count_sublists(self):
        return len(self.get_active_sublists())

    class Meta:
        ordering = ['order', 'name']


class Context(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)

    order = models.IntegerField(default=0)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)

    def __str__(self):
        return self.name

    def get_name(self):
        return "/{}".format(self.name)

    def get_active_lists(self):
        return self.lists.filter(status='active')

    def count_lists(self):
        return len(self.get_active_lists())

    class Meta:
        ordering = ['order', 'name']
