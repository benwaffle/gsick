# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_auto_20151001_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 911000)),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 901000)),
        ),
        migrations.AlterField(
            model_name='follow',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 911000)),
        ),
        migrations.AlterField(
            model_name='note',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 911000)),
        ),
        migrations.AlterField(
            model_name='paste',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 911000)),
        ),
        migrations.AlterField(
            model_name='pin',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 911000)),
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 901000)),
        ),
        migrations.AlterField(
            model_name='privatemessage',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 22, 55, 31, 911000)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_alert_read',
            field=models.ForeignKey(to='server.Alert'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_pm_read',
            field=models.ForeignKey(to='server.PrivateMessage'),
        ),
    ]
