# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('server', '0002_auto_20151001_1955'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_modified', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='alert',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='follow',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='note',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='paste',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='pin',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AlterField(
            model_name='privatemessage',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 21, 3, 6, 725000)),
        ),
        migrations.AddField(
            model_name='conversation',
            name='last_message',
            field=models.ForeignKey(to='server.PrivateMessage'),
        ),
        migrations.AddField(
            model_name='conversation',
            name='user1',
            field=models.ForeignKey(related_name='user1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversation',
            name='user2',
            field=models.ForeignKey(related_name='user2', to=settings.AUTH_USER_MODEL),
        ),
    ]
