# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table(u'server_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('theme_background', self.gf('django.db.models.fields.CharField')(default='0', max_length=20)),
            ('theme_text', self.gf('django.db.models.fields.CharField')(default='0', max_length=20)),
            ('theme_link', self.gf('django.db.models.fields.CharField')(default='0', max_length=20)),
            ('last_pm_read', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_alert_read', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'server', ['Profile'])

        # Adding model 'Channel'
        db.create_table(u'server_channel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'server', ['Channel'])

        # Adding model 'Post'
        db.create_table(u'server_post', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Channel'])),
            ('content', self.gf('django.db.models.fields.TextField')(default=None, max_length=4000, null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 2, 0, 0))),
        ))
        db.send_create_signal(u'server', ['Post'])

        # Adding model 'Comment'
        db.create_table(u'server_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Post'])),
            ('content', self.gf('django.db.models.fields.TextField')(default=None, max_length=4000, null=True)),
            ('reply', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['server.Comment'], null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 2, 0, 0))),
        ))
        db.send_create_signal(u'server', ['Comment'])

        # Adding model 'Pin'
        db.create_table(u'server_pin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Post'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 2, 0, 0))),
        ))
        db.send_create_signal(u'server', ['Pin'])

        # Adding model 'Note'
        db.create_table(u'server_note', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content', self.gf('django.db.models.fields.TextField')(default=None, max_length=4000, null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 2, 0, 0))),
        ))
        db.send_create_signal(u'server', ['Note'])

        # Adding model 'PrivateMessage'
        db.create_table(u'server_privatemessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='receiver', to=orm['auth.User'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender', to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 2, 0, 0))),
            ('message', self.gf('django.db.models.fields.TextField')(default=None, max_length=4000, null=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('info1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True)),
            ('info2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True)),
        ))
        db.send_create_signal(u'server', ['PrivateMessage'])

        # Adding model 'Silenced'
        db.create_table(u'server_silenced', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='who_wants_silence', to=orm['auth.User'])),
            ('brat', self.gf('django.db.models.fields.related.ForeignKey')(related_name='who_to_be_silenced', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'server', ['Silenced'])

        # Adding model 'Alert'
        db.create_table(u'server_alert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alerted', to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True)),
            ('info1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True)),
            ('info2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True)),
            ('info3', self.gf('django.db.models.fields.TextField')(default='', max_length=100, null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 2, 0, 0))),
        ))
        db.send_create_signal(u'server', ['Alert'])


    def backwards(self, orm):
        # Deleting model 'Profile'
        db.delete_table(u'server_profile')

        # Deleting model 'Channel'
        db.delete_table(u'server_channel')

        # Deleting model 'Post'
        db.delete_table(u'server_post')

        # Deleting model 'Comment'
        db.delete_table(u'server_comment')

        # Deleting model 'Pin'
        db.delete_table(u'server_pin')

        # Deleting model 'Note'
        db.delete_table(u'server_note')

        # Deleting model 'PrivateMessage'
        db.delete_table(u'server_privatemessage')

        # Deleting model 'Silenced'
        db.delete_table(u'server_silenced')

        # Deleting model 'Alert'
        db.delete_table(u'server_alert')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'server.alert': {
            'Meta': {'object_name': 'Alert'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 2, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'info2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'info3': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerted'", 'to': u"orm['auth.User']"})
        },
        u'server.channel': {
            'Meta': {'object_name': 'Channel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'server.comment': {
            'Meta': {'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '4000', 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 2, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['server.Post']"}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['server.Comment']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'server.note': {
            'Meta': {'object_name': 'Note'},
            'content': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '4000', 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 2, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'server.pin': {
            'Meta': {'object_name': 'Pin'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 2, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['server.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'server.post': {
            'Meta': {'object_name': 'Post'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['server.Channel']"}),
            'content': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '4000', 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 2, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'server.privatemessage': {
            'Meta': {'object_name': 'PrivateMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 2, 0, 0)'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'info2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '4000', 'null': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'to': u"orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receiver'", 'to': u"orm['auth.User']"})
        },
        u'server.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_alert_read': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_pm_read': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'theme_background': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '20'}),
            'theme_link': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '20'}),
            'theme_text': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'server.silenced': {
            'Meta': {'object_name': 'Silenced'},
            'brat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'who_to_be_silenced'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'who_wants_silence'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['server']