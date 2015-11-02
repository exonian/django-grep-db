# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text_field', models.TextField(blank=True)),
                ('text_field_two', models.TextField(blank=True)),
                ('char_field', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestModelTwo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text_field', models.TextField(blank=True)),
                ('char_field', models.CharField(max_length=255, blank=True)),
                ('url', models.URLField(blank=True)),
            ],
        ),
    ]
