# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liszt', '0002_auto_20150924_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='items', to='liszt.Tag'),
        ),
        migrations.AlterField(
            model_name='list',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='lists', to='liszt.Tag'),
        ),
    ]
