# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', django_extensions.db.fields.AutoSlugField(unique=True, blank=True, populate_from='name', editable=False)),
                ('order', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('active', 'Active'), ('archived', 'Archived')], max_length=20, default='active')),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('text', models.TextField()),
                ('order', models.IntegerField(default=0)),
                ('checked', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', django_extensions.db.fields.AutoSlugField(unique=True, blank=True, populate_from='name', editable=False)),
                ('order', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('active', 'Active'), ('archived', 'Archived')], max_length=20, default='active')),
                ('context', models.ForeignKey(blank=True, related_name='lists', null=True, to='liszt.Context')),
                ('parent_list', models.ForeignKey(blank=True, related_name='sublists', null=True, to='liszt.List')),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='item',
            name='parent_list',
            field=models.ForeignKey(related_name='items', to='liszt.List'),
        ),
    ]
