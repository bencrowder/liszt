# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('liszt', '0004_item_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, populate_from='name', editable=False),
        ),
    ]
