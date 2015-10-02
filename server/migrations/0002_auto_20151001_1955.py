# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('top_posts', models.TextField(max_length=1000)),
                ('top_posts_date', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='alert',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='follow',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='note',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='paste',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='pin',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
        migrations.AlterField(
            model_name='privatemessage',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 19, 55, 2, 534000)),
        ),
    ]
