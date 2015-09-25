# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liszt', '0003_auto_20150924_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
