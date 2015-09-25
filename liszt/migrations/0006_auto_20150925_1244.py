# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liszt', '0005_auto_20150925_1239'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='context',
            options={'ordering': ['order', 'slug']},
        ),
        migrations.AlterModelOptions(
            name='list',
            options={'ordering': ['order', 'slug']},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['slug']},
        ),
        migrations.RemoveField(
            model_name='context',
            name='name',
        ),
        migrations.RemoveField(
            model_name='list',
            name='name',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='name',
        ),
        migrations.AlterField(
            model_name='context',
            name='slug',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='list',
            name='slug',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.CharField(max_length=100),
        ),
    ]
