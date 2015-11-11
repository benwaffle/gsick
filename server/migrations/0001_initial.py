# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'', max_length=100, null=True)),
                ('info1', models.CharField(default=b'', max_length=100, null=True)),
                ('info2', models.CharField(default=b'', max_length=100, null=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
            ],
        ),
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('ip', models.CharField(default=0, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default=None, max_length=4000, null=True)),
                ('num_likes', models.IntegerField(default=0)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
            ],
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('comment', models.ForeignKey(to='server.Comment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_modified', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('followed', models.ForeignKey(related_name='followed', to=settings.AUTH_USER_MODEL)),
                ('follower', models.ForeignKey(related_name='follower', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Paste',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default=None, max_length=100000)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
            ],
        ),
        migrations.CreateModel(
            name='Pin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default=None, max_length=4000, null=True)),
                ('num_likes', models.IntegerField(default=0)),
                ('num_comments', models.IntegerField(default=0)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('date_modified', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('channel', models.ForeignKey(to='server.Channel')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PrivateMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('message', models.TextField(default=None, max_length=4000, null=True)),
                ('hidden', models.BooleanField(default=False)),
                ('info1', models.CharField(default=b'', max_length=100, null=True)),
                ('info2', models.CharField(default=b'', max_length=100, null=True)),
                ('sender', models.ForeignKey(related_name='sender', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='receiver', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_registered', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('last_entrance', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('theme_background', models.CharField(default=b'0', max_length=20)),
                ('theme_text', models.CharField(default=b'0', max_length=20)),
                ('theme_link', models.CharField(default=b'0', max_length=20)),
                ('theme_input_background', models.CharField(default=b'0', max_length=20)),
                ('theme_input_text', models.CharField(default=b'0', max_length=20)),
                ('theme_input_border', models.CharField(default=b'0', max_length=20)),
                ('theme_input_placeholder', models.CharField(default=b'0', max_length=20)),
                ('theme_scroll_background', models.CharField(default=b'0', max_length=20)),
                ('embed_option', models.CharField(default=b'embed', max_length=20)),
                ('last_pm_read', models.IntegerField(default=0)),
                ('last_alert_read', models.IntegerField(default=0)),
                ('ip', models.CharField(default=0, max_length=50)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('channel', models.ForeignKey(to='server.Channel')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Visited',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel', models.CharField(default=b'', max_length=100)),
                ('count', models.IntegerField(default=0)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 11, 11, 10, 6, 0, 366000))),
                ('user', models.ForeignKey(related_name='user_visiting', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='pin',
            name='post',
            field=models.ForeignKey(to='server.Post'),
        ),
        migrations.AddField(
            model_name='pin',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
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
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='server.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='reply',
            field=models.ForeignKey(default=None, to='server.Comment', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='alert',
            name='comment1',
            field=models.ForeignKey(related_name='comment_1', to='server.Comment', null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='comment2',
            field=models.ForeignKey(related_name='comment_2', to='server.Comment', null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='post1',
            field=models.ForeignKey(related_name='post_1', to='server.Post', null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='post2',
            field=models.ForeignKey(related_name='post_2', to='server.Post', null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='user',
            field=models.ForeignKey(related_name='alerted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='alert',
            name='user2',
            field=models.ForeignKey(related_name='alert_user_2', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
