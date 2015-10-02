# encoding: utf-8

import pdb
import random
import re
import datetime
import string
import json
import itertools
from unicodedata import normalize
from operator import attrgetter
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.utils.html import linebreaks
from django.utils.encoding import smart_str, smart_unicode
from django.db.models import Avg, Max, Min, Count, Q
from server.models import *
from server.magik import *

admin_list = ('madprops',)
forbidden_channels = ('top', 'new', 'chat', 'settings', 'alerts', 'posts', 'pins', 'random', 'stream')

def create_c(request):
	c = {}
	c.update(csrf(request))
	return c

def main(request, mode='start', info=''):
	c = create_c(request)
	if mode == 'start':
		if request.user.is_authenticated():
			c['mode'] = 'stream'
		else:
			c['mode'] = 'new'
	else:
		c['mode'] = mode
	c['info'] = info
	c['loggedin'] = 'no'
	c['username'] = ''
	c['background'] = ''
	c['text'] = ''
	c['link'] = ''
	c['input_background'] = ''
	c['input_text'] = ''
	c['input_border'] = ''
	c['input_placeholder'] = ''
	c['scroll_background'] = ''
	if request.user.is_authenticated():
		c['loggedin'] = 'yes'
		c['username'] = request.user.username
		p = get_profile(request.user)
		c['background'] = p.theme_background
		c['text'] = p.theme_text
		c['link'] = p.theme_link
		c['input_background'] = p.theme_input_background
		c['input_text'] = p.theme_input_text
		c['input_border'] = p.theme_input_border
		c['input_placeholder'] = p.theme_input_placeholder
		c['scroll_background'] = p.theme_scroll_background
		c['embed_option'] = p.embed_option
	return render_to_response('base.html', c, context_instance=RequestContext(request))	

def enter(request):
	auth_logout(request)
	if request.method == 'POST':
		if 'btnlogin' in request.POST:
			username = request.POST['username'].lower()
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth_login(request, user)
					return HttpResponseRedirect('../../')
			else:
				c = create_c(request)
				c['repetir'] = True
				return render_to_response('enter.html', c, context_instance=RequestContext(request))
		if 'btnregister' in request.POST:
			if error_register(request):
				c = {}
				c.update(csrf(request))
				c['repetir'] = True
				return render_to_response('enter.html', c, context_instance=RequestContext(request))
			else:
				username = clean_username(request.POST['register_username']).lower()
				password = request.POST['register_password']
				email = request.POST['register_email']
				user = User.objects.create_user(username, email, password)
				p = Profile(user=user)
				p.save()
				user.backend='django.contrib.auth.backends.ModelBackend'
				auth_login(request, user)
				return HttpResponseRedirect('/new')
	else:
		c = create_c(request)
		return render_to_response('enter.html', c, context_instance=RequestContext(request))

def error_register(request):
	username = request.POST['register_username'].lower()
	password = request.POST['register_password'] 
	email = request.POST['register_email'] 
	if not clean_username(username):
		return True
	if username.replace(" ", "") == "" or password.replace(" ", "") == "":
		return True
	if len(username) > 20 or len(password) > 50:
		return True
	try:
		User.objects.get(username=username)
		return True
	except:
		pass
	if '@' not in email:
		return True
	return False

@login_required
def themes(request):
	html = ''
	html = theme_to_html(request)
	data = {'html':html}
	return HttpResponse(json.dumps(data), content_type="application/json")

def chat(request):
	data = ''
	status = 'ok'
	username = ''
	posts = ''
	s = ''
	try:
		username = request.GET.get('username',0)
		peer = User.objects.get(username=username)
		username = peer.username
		posts = chat_to_html(request, get_chat_history(request, peer))
	except:
		status = 'error'
	data = {'posts':posts, 'username':username, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def view_chat(request):
	data = ''
	status = 'error'
	posts = ''
	s = ''
	try:
		posts = chat_to_html(request, get_chat_messages(request), 'chatall')
		status = 'ok'
	except:
		posts = ''
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_alerts(request):
	alerts = Alert.objects.filter(user=request.user).order_by('-id')[:20]
	return alerts

@login_required
def view_alerts(request):
	data = ''
	status = 'error'
	alerts = ''
	xalerts = get_alerts(request)
	if len(xalerts) > 0:
		alerts = alerts_to_html(request, xalerts)
		p = get_profile(request.user)
		lalerts = list(xalerts)
		p.last_alert_read = lalerts[0]
		p.save()
		status = 'ok'
	data = {'alerts':alerts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def sent_messages(request):
	data = ''
	status = 'error'
	posts = ''
	s = ''
	try:
		posts = chat_to_html(request, get_sent_messages(request), 'sent')
		status = 'ok'
	except:
		pass
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_chat_history(request, peer, last_pm_id=None):
	if last_pm_id:
		pmr = PrivateMessage.objects.filter(user=request.user, sender=peer, id__lt=last_pm_id)
		pms = PrivateMessage.objects.filter(sender=request.user, user=peer, id__lt=last_pm_id).exclude(info1='welcome')
		pmx = sorted(itertools.chain(pmr, pms), key=attrgetter('id'), reverse=True)[:20]
	else:
		pmr = PrivateMessage.objects.filter(user=request.user, sender=peer)
		pms = PrivateMessage.objects.filter(sender=request.user, user=peer).exclude(info1='welcome')
		pmx = sorted(itertools.chain(pmr, pms), key=attrgetter('id'), reverse=True)[:20]
	return pmx

def refresh_channel(request):
	id = request.GET.get('id',0)
	channel_name = request.GET.get('channel_name',0)
	channel = Channel.objects.get(name=channel_name)
	posts = Post.objects.filter(channel=channel, id__gt=id).order_by('-id')
	posts = posts_to_html(request,posts)
	status = 'ok'
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def refresh_user(request):
	id = request.GET.get('id',0)
	username = request.GET.get('username',0)
	if id == 0:
		user = User.objects.get(username=username)
		posts = Post.objects.filter(user=user, id__gt=id).order_by('-id')
	else:
		post = Post.objects.get(id=id)
		posts = Post.objects.filter(user=post.user, id__gt=id).order_by('-id')
	posts = posts_to_html(request,posts,'user')
	status = 'ok'
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def refresh_chat(request):
	data = ''
	status = ''
	username = request.GET['username']
	first_chat_id = request.GET.get('first_chat_id',0)
	peer = User.objects.get(username=username)
	pmr = PrivateMessage.objects.filter(user=request.user, sender=peer, id__gt=first_chat_id)
	pms = PrivateMessage.objects.filter(sender=request.user, user=peer, id__gt=first_chat_id)
	pmx = sorted(itertools.chain(pmr, pms), key=attrgetter('date'), reverse=True)
	p = get_profile(request.user)
	last_pm_read = p.last_pm_read
	for x in pmr:
		if x.id > last_pm_read.id:
			last_pm_read = x
	p.last_pm_read = last_pm_read
	p.save()
	posts = chat_to_html(request, pmx)
	status = 'ok'
	data = {'posts':posts, 'username':username, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def refresh_chatall(request):
	data = ''
	status = ''
	first_chat_id = request.GET.get('first_chat_id', 0)
	convs = Conversation.objects.filter(Q(user1=request.user) | Q(user2=request.user), last_message_id__gt=first_chat_id).order_by('-date_modified')[:20]
	msgs = []
	for conv in convs:
		msgs.append(conv.last_message)
	if len(msgs) > 0:
		p = get_profile(request.user)
		p.last_pm_read = msgs[0]
		p.save()
	messages = chat_to_html(request, msgs, 'chatall')
	status = 'ok'
	data = {'messages':messages, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def refresh_sent(request):
	data = ''
	status = 'error'
	first_chat_id = request.GET.get('first_chat_id',0)
	pms = PrivateMessage.objects.filter(sender=request.user, id__gt=first_chat_id).exclude(info1='welcome')
	messages = chat_to_html(request, pms, 'sent')
	status = 'ok'
	data = {'messages':messages, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

@login_required		
def note(request):
	data = 'no'
	note = stripper(request.POST['note'].strip())
	if error_note(note):
		return HttpResponse(json.dumps(data), content_type="application/json")
	else:
		pm = Note(user=request.user, content=note, date=datetime.datetime.now())
		pm.save()
		data = 'yes'
		return HttpResponse(json.dumps(data), content_type="application/json")

def error_note(note):
	if len(note) > 2000:
		return True
	if len(note) == 0:
		return True
	return False

def seen(request):
	data = ''
	date = ''
	try:
		user = User.objects.get(username=request.GET['uname'].replace(" ",""))
		pdate = pmdate = cdate = logindate = user.date_joined
	except:
		pass
	try:
		logindate = user.last_login
	except:
		pass
	try:	
		post = Post.objects.filter(user=user).order_by('-date')[0]
		pdate = post.date
	except:
		pass
	try:
		pm = PrivateMessage.objects.filter(sender=user).order_by('-date')[0]
		pmdate = pm.date
	except:
		pass
	try:
		dates = [pdate,pmdate,cdate,logindate]
		date = max(dates)
		date = radtime(date)
		data = {'date':date, 'uname':user.username}
	except:
		pass
	return HttpResponse(json.dumps(data), content_type="application/json")

def mail_inbox(request):
	try:
		inbox = ""
		inbox = inbox + "<div>"
		inbox = inbox + ""
		inbox = inbox + "</div>"
	except:
		pass
	arrows = 'none';
	data = {'inbox':inbox, 'arrows':arrows}
	return HttpResponse(json.dumps(data), content_type="application/json")	

def whoami(request):
	data = ''
	try:
		data = request.user.username
	except:
		pass
	return HttpResponse(json.dumps(data), content_type="application/json")

def find_mentions(request, input):
	l = []
	words = input.split()
	for w in words:
		if w.startswith('@'):
			l.append(w[1:])
	return l

@login_required
def post_comment(request):
	content = stripper(request.POST.get('content',0).strip())
	id = request.POST.get('id',0)
	status = error_comment(request,content,id)
	cname = ''
	if status == 'ok':
		post = Post.objects.get(id=id)
		cname = post.channel.name
		comment = Comment(user=request.user,content=content,date=datetime.datetime.now(),post=post)
		comment.save()
		if post.user != request.user:
			mentions = find_mentions(request, content)
			for m in mentions:
				try:
					auser = User.objects.get(username=m)
					alert = Alert(user=auser, type='mention', info1=request.user.username, info2=post.id, info3=comment.id, date=datetime.datetime.now())
					alert.save()
				except:
					continue
			if post.user.username not in mentions:
				alert = Alert(user=post.user, type='comment', info1=request.user.username, info2=post.id, info3=comment.id, date=datetime.datetime.now())
				alert.save()
	data = {'status':status, 'cname':cname}
	return HttpResponse(json.dumps(data), content_type="application/json")	

def error_comment(request, content, id):
	post = Post.objects.get(id=id)
	if content == '':
		return 'empty'
	if len(content) > 2000:
		return 'toobig'
	return 'ok'

def open_post(request, id=None):
	if not id:
		id = request.GET.get('id',0)
	post = Post.objects.get(id=id)
	cname = post.channel.name
	comments = Comment.objects.filter(post=post).order_by('id')[:50]
	post = post_to_html(request, post)
	comments = comments_to_html(request,comments)
	status = 'ok'
	data = {'post':post, 'comments':comments, 'status':status, 'cname':cname}
	return HttpResponse(json.dumps(data), content_type="application/json")

def save_top_posts():
	# days and num_pins__gte should be changed as the site grows in users 
	# days is how old can a post be to be considered for top
	# num_pins__gte is the minimum amount of pins (appreciations) to be considered for top
	posts = Post.objects.annotate(num_pins=Count('pin')).filter(date__gte=(datetime.datetime.now() - datetime.timedelta(days=100))).filter(num_pins__gte='1').order_by('-num_pins', '-date')[:10]
	s = ''
	for p in posts:
		s += str(p.id)
		s += ','
	s = s[:-1]
	info = Info.objects.first()
	info.top_posts = s
	info.top_posts_date = datetime.datetime.now()
	info.save()
	return posts
		
def get_top_posts():
	info = Info.objects.first()
	if info == None:
		info = Info(top_posts='', top_posts_date=datetime.datetime.now())
		info.save()
		return save_top_posts()
	if datetime.datetime.now() - info.top_posts_date > datetime.timedelta(minutes=5):
		return save_top_posts()
	else:
		ids = map(int, info.top_posts.split(','))
		posts = Post.objects.filter(id__in=ids)
		post_list = list(posts)
		post_list.sort(key=lambda x: ids.index(x.id))
		return post_list

def top_posts(request):
	posts = ''
	status = ''
	try:
		posts = get_top_posts()
		posts = posts_to_html(request, posts, 'new')
		status = 'ok'
	except:
		pass
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_channel_posts_by_user(request, user, channel):
	posts = Post.objects.filter(user=user, channel=channel).order_by('-id')[:10]
	return posts

def user_on_channel(request):
	data = ''
	uname = ''
	cname = ''
	posts = ''
	status = 'error'
	try:
		input = request.GET['input']
		words = input.split()
		uname = words[0]
		cname = words[2]
		user = User.objects.get(username=uname)
		channel = Channel.objects.get(name=cname)
		posts = get_channel_posts_by_user(request, user, channel)
		posts = posts_to_html(request,posts)
		if posts != '':
			status = 'ok'
	except:
		pass
	data = {'posts':posts, 'status':status, 'uname':uname, 'cname':cname}
	return HttpResponse(json.dumps(data), content_type="application/json")

def new_posts(request):
	posts = ''
	posts = get_new_posts(request)
	posts = posts_to_html(request, posts,'new')
	status = 'ok'
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_new(request):
	posts = ''
	status = ''
	try:
		id = request.GET.get('id',0)
		posts = get_more_new_posts(request,id)
		posts = posts_to_html(request,posts,'new')
		status = 'ok'
	except:
		pass
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_alerts(request):
	posts = ''
	status = ''
	try:
		id = request.GET.get('id',0)
		xalerts = Alert.objects.filter(user=request.user, id__lt=id).order_by('-id')[:20]
		alerts = alerts_to_html(request,xalerts)
		status = 'ok'
	except:
		pass
	data = {'alerts':alerts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_comments(request):
	comments = ''
	status = ''
	id = request.GET.get('id',0)
	last_id = request.GET.get('last_id',0)
	post = Post.objects.get(id=id)
	comments = Comment.objects.filter(post=post, id__gt=last_id).order_by('id')[:50]
	comments = comments_to_html(request,comments)
	status = 'ok'
	data = {'comments':comments, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def reply_to_comment(request):
	status = 'error'
	comment_id = request.POST['comment_id']
	content = request.POST['msg'].strip()
	comment_replied = Comment.objects.get(id=comment_id)
	status = error_comment(request, content, comment_replied.post.id)
	if status == 'ok':
		post = comment_replied.post
		comment = Comment(user=request.user, content=content, post=post, reply=comment_replied, date=datetime.datetime.now())
		comment.save()
		if request.user != comment_replied.user:
			alert = Alert(user=comment_replied.user, type='reply', info1=request.user, info2=post.id, info3=comment.id, date=datetime.datetime.now())
			alert.save()
		status = 'ok'
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_new_posts(request):
	posts = Post.objects.all().order_by('-id')[:10]
	return posts

def get_more_new_posts(request, id):
	posts = Post.objects.filter(id__lt=id).order_by('-id')[:10]
	return posts

def get_users():
	return User.objects.all()

def get_user(request):
	uname = request.GET['uname']
	post = ''
	data = ''
	if uname == "me" and request.user.is_authenticated():
		user = request.user
	else:
		user = User.objects.get(username=uname)
	posts = get_user_posts(request, user)
	posts = posts_to_html(request,posts,'user')
	following = ''
	if request.user.is_authenticated():
		try:
			f = Follow.objects.get(followed=User.objects.get(username=uname), follower=request.user)
			following = 'unfollow'
		except:
			following = 'follow'
	data = {'uname': user.username, 'posts':posts, 'following': following}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_user_posts(request, user):
	posts = Post.objects.filter(user=user).order_by('-id')[:10]
	return posts

def toggle_follow(request):
	status = ''
	if request.user.is_authenticated():
		followed = User.objects.get(username=request.POST['uname'])
		try:
			f = Follow.objects.get(followed=followed, follower=request.user)
			f.delete()
			status = 'unfollowed'
		except:
			f = Follow(followed=followed, follower=request.user, date=datetime.datetime.now())
			f.save()
			try:
				a = Alert.objects.get(user=followed, type='follow', info1=request.user.username)
			except:
				alert = Alert(user=followed, type='follow', info1=request.user.username, date=datetime.datetime.now())
				alert.save()
			status = 'followed'
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_stream(request):
	posts = ''
	if request.user.is_authenticated():
		followed = []
		for f in Follow.objects.filter(follower=request.user):
			followed.append(f.followed)
		posts = Post.objects.filter(user__in=followed).order_by('-id')[:10]
		posts = posts_to_html(request, posts, 'stream')
	if posts == '':
		posts = '<center>follow people to see their posts here</center>'
	data = {'posts':posts}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_stream(request):
	posts = ''
	status = ''
	try:
		id = request.GET.get('id',0)
		followed = []
		for f in Follow.objects.filter(follower=request.user):
			followed.append(f.followed)
		posts = Post.objects.filter(user__in=followed, id__lt=id).order_by('-id')[:10]
		posts = posts_to_html(request, posts, 'stream')
		status = 'ok'
	except:
		pass
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")
	
def error_channel(cname):
	if cname.replace(" ","") == "":
		return True
	if len(cname) > 111:
		return True
	return False

def check_new_pms(request):
	status = 'no'
	id = ''
	uname = ''
	p = get_profile(request.user)
	try:
		last_pm = PrivateMessage.objects.filter(user=request.user).order_by('-id')[0]
		num = PrivateMessage.objects.filter(user=request.user, id__gt=p.last_pm_read.id).order_by('-id').count()
		if last_pm.id > p.last_pm_read.id:
			status = 'yes'
			id = last_pm.id
			uname = last_pm.sender.username
	except:
		pass
	data = {'status': status, 'id':id, 'uname':uname, 'num':num}
	return HttpResponse(json.dumps(data), content_type="application/json")

def check_new_alerts(request):
	status = 'no'
	id = ''
	uname = ''
	p = get_profile(request.user)
	last_alert = Alert.objects.filter(user=request.user).order_by('-id')[0]
	num = Alert.objects.filter(user=request.user, id__gt=p.last_alert_read.id).order_by('-id').count()
	if last_alert.id > p.last_alert_read.id:
		status = 'yes'
		id = last_alert.id
	data = {'status': status, 'id':id, 'num':num}
	return HttpResponse(json.dumps(data), content_type="application/json")

def remove_duplicate_senders(request, pmr, welcome=True):
	l = []
	a = False
	for p in pmr:
		a = True
		if welcome:
			if p.sender.username in ['note'] or p.info1=='welcome':
				l.append(p)
				continue
		else:
			if p.sender.username in ['note']:
				l.append(p)
				continue	
		for px in l:
			if (p.sender.username == px.sender.username and p.sender.username != request.user.username) or (p.sender.username == request.user.username and p.user == px.user):
				a = False
				break
		if a:
			l.append(p)
	return l

def get_senders_list(request, l):
	bl = []
	for x in l:
		u = x.sender.username
		if u in (['note'] + bl):
			continue
		else:
			bl.append(u)
	return bl

def get_receivers_list(request, l):
	bl = []
	for x in l:
		u = x.user.username
		if u in ([request.user.username,''] + bl):
			continue
		else:
			bl.append(u)
	return bl

def get_private_messages(request):
	ss = Silenced.objects.filter(user=request.user)
	last_pm_id = None
	n = 20
	bl = []
	senders = []
	receivers = []
	y = 0
	while True:
		if last_pm_id:	
			pmr = PrivateMessage.objects.filter(user=request.user,hidden=False,id__lt=last_pm_id).exclude(sender__username__in=[s.brat.username for s in ss] + senders).order_by('-id')[:n]
			pms = PrivateMessage.objects.filter(sender=request.user, hidden=False, id__lt=last_pm_id).exclude(user__username__in=receivers).exclude(info1='welcome').order_by('-id')[:n]
		else:	
			pmr = PrivateMessage.objects.filter(user=request.user,hidden=False).exclude(sender__username__in=[s.brat.username for s in ss] + senders).order_by('-id')[:n]
			pms = PrivateMessage.objects.filter(sender=request.user, hidden=False).exclude(user__username__in=receivers).exclude(info1='welcome').order_by('-id')[:n]
		pmx = sorted(itertools.chain(pmr, pms), key=attrgetter('date'), reverse=True)[:n]
		l = list(pmx)
		bl = bl + l
		bl = bl[:n]
		bl = remove_duplicate_senders(request, bl)
		senders = get_senders_list(request,bl)
		receivers = receivers + get_receivers_list(request,bl)
		last_pm_id = bl[-1].id
		y = y + 1
		if y > 30:
			return pm_to_html(request,bl)
		if len(bl) >= 20 or not pmx:
			break
	messages = pm_to_html(request,bl)
	return HttpResponse(messages)

def get_chat_messages(request, last_pm_id=None):
	if last_pm_id != None:
		convs = Conversation.objects.filter(Q(user1=request.user) | Q(user2=request.user), last_message_id__lt=last_pm_id).order_by('-date_modified')[:20]
	else:
		convs = Conversation.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-date_modified')[:20]
	msgs = []
	for conv in convs:
		msgs.append(conv.last_message)
	if len(msgs) > 0:
		p = get_profile(request.user)
		p.last_pm_read = msgs[0]
		p.save()
	return msgs

def get_sent_messages(request, last_pm_id=None):
	ss = Silenced.objects.filter(user=request.user)
	n = 20
	bl = []
	senders = []
	receivers = []
	y = 0
	while True:
		if last_pm_id:	
			pms = PrivateMessage.objects.filter(sender=request.user, hidden=False, id__lt=last_pm_id).exclude(user__username__in=receivers).exclude(info1='welcome').order_by('-id')[:n]
		else:	
			pms = PrivateMessage.objects.filter(sender=request.user, hidden=False).exclude(user__username__in=receivers).exclude(info1='welcome').order_by('-id')[:n]
		l = list(pms)
		bl = bl + l
		bl = bl[:n]
		bl = remove_duplicate_senders(request, bl)
		senders = get_senders_list(request,bl)
		receivers = receivers + get_receivers_list(request,bl);
		last_pm_id = bl[-1].id
		y = y + 1
		if y > 30:
			break
		if len(bl) >= 20 or not pms:
			break
	return bl

def check_pm_limit(request):
	num_pms = PrivateMessage.objects.filter(sender=request.user, date__gte=(datetime.datetime.now() - datetime.timedelta(days=1))).count()
	if num_pms < 200:
		return True
	return False

@login_required
def post_to_channel(request):
	data = ''
	post = ''
	status = ''
	id = ''
	status = error_post(request)
	if status == 'ok':
		cname = request.POST['channel'].lower()
		cname = request.POST['channel'].replace('_', '')
		try:
			channel = Channel.objects.get(name=cname)
		except:
			channel = Channel(name=cname)
			channel.save()
		content = stripper(request.POST['content']).strip()
		post = Post(content=content, channel=channel, user=request.user, date=datetime.datetime.now())
		post.save()
		id = post.id
	data = {'status':status, 'id':id}
	return HttpResponse(json.dumps(data), content_type="application/json") 

@csrf_exempt
def doggo_post_to_channel(request):
	data = ''
	post = ''
	status = ''
	id = ''
	status = doggo_error_post(request)
	if status == 'ok':
		cname = request.POST['channel'].lower()
		cname = request.POST['channel'].replace('_', '')
		try:
			channel = Channel.objects.get(name=cname)
		except:
			channel = Channel(name=cname)
			channel.save()
		content = stripper(request.POST['content']).strip()
		usernames = ['doggo', 'normie', 'atros', 'raphael', 'sytrus', 'dickiev', 'alexis', 'amalek']
		post = Post(content=content, channel=channel, user=User.objects.get(username=random.choice(usernames)), date=datetime.datetime.now())
		post.save()
		id = post.id
	data = {'status':status, 'id':id}
	return HttpResponse(json.dumps(data), content_type="application/json")

def doggo_error_post(request):
	cname = request.POST['channel'].lower()
	cname = request.POST['channel'].replace('_', '')
	content = stripper(request.POST['content'].strip())
	if cname in forbidden_channels:
		return 'forbiddenchannel'
	if len(cname) > 25:
		return 'cnametoolong'
	if content == "":
		return 'empty'
	if len(content) > 2000:
		return 'toobig'
	return 'ok'

def error_post(request):
	cname = request.POST['channel'].lower()
	cname = request.POST['channel'].replace('_', '')
	content = stripper(request.POST['content'].strip())
	if cname in forbidden_channels:
		return 'forbiddenchannel'
	num_posts = Post.objects.filter(user=request.user, date__gte=(datetime.datetime.now() - datetime.timedelta(days=1))).count()
	if num_posts > 100:
		return 'toomuchposts'
	num_posts = Post.objects.filter(channel__name=cname, user=request.user, date__gte=(datetime.datetime.now() - datetime.timedelta(hours=12))).count()
	# if num_posts >= 1 and request.user.username != 'madprops':
	# 	return 'wait'
	if content == "":
		return 'empty'
	if len(content) > 2000:
		return 'toobig'
	try:
		media = get_media_url(content)
		uposts = Post.objects.filter(user=request.user)
		for p in uposts:
			if media:
				if get_media_url(p.content) == media:
					return 'postduplicate'
			else:
				if p.content == content:
					return 'postduplicate'
	except:
		pass
	try:
		media = get_media_url(content)
		uposts = Post.objects.filter(channel__name=cname)
		for p in uposts:
			if media:
				if get_media_url(p.content) == media:
					return 'channelduplicate'
			else:
				if p.content == content:
					return 'channelduplicate'
	except:
		pass
	return 'ok'

@login_required
def send_message(request):
	data = ''
	username = ''
	status = ''
	try:
		content = request.POST['content']
		matches = get_inbox_match(content)
		receiver = matches.group(1)
		message = stripper(matches.group(2))
	except:
		return HttpResponse(data)
	status = error_message(request, content, receiver, message)
	if status =='ok':
		receiver = User.objects.get(username=receiver)
		username = receiver.username
		pm = PrivateMessage(user=receiver, sender=request.user, date=datetime.datetime.now(), message=stripper(message))
		pm.save()
		if username < request.user.username:
			user1 = receiver;
			user2 = request.user
		else:
			user1 = request.user
			user2 = receiver
		try:
			conv = Conversation.objects.get(user1=user1, user2=user2)
			conv.last_message = pm
			conv.date_modified = datetime.datetime.now()
			conv.save()
		except:
			conv = Conversation(user1=user1, user2=user2, last_message=pm, date_modified=datetime.datetime.now())
			conv.save()
	data = {'username':username, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json") 
	
def error_message(request, content, receiver, message):
	not_allowed = ['root', 'global']
	if not request.user.is_authenticated():
		return 'nologin'
	if not content.startswith("@"):
		return 'format'
	if content.replace(" ", "") == "":
		return 'empty'
	if len(content) > 2000:
		return 'toobig'
	if receiver == "":
		return 'empty'
	if message == "":
		return 'empty'
	try:
		User.objects.get(username=receiver)
	except:
		return 'noreceiver'
	if receiver == request.user.username:
		return 'sameuser'
	if receiver in not_allowed:
		return 'notallowed'
	return 'ok'

def check_inbox_limit(request):
	num_inbox = PrivateMessage.objects.filter(sender=request.user, date__gte=(datetime.datetime.now() - datetime.timedelta(days=1))).count()
	if num_inbox < 200:
		return False
	return True 

def get_inbox_match(content):
	match = re.search('^@([^ ]+)\s(.*)', content)
	return match

def get_new_pms(request):
	sender = request.GET['sender']
	pmu = User.objects.get(username=sender)
	pms = PrivateMessage.objects.filter(user=request.user, sender=pmu, read=False)
	for pm in pms:
		if pm.user == request.user and not pm.read:
			pm.read = True
			pm.save()
	if pms:
		return HttpResponse(pm_posts_to_html(request, pms))
	else:
		return HttpResponse()
	
def check_login(request):
	xlogin = 'no'
	uname = ''
	background = ''
	text = ''
	link = ''
	if request.user.is_authenticated():
		xlogin = 'yes'
		uname = request.user.username
		p = get_profile(request.user)
		background = p.theme_background
		text = p.theme_text
		link = p.theme_link
		input_background = p.theme_input_background
		input_text = p.theme_input_text
		input_border = p.theme_input_border
		input_placeholder = p.theme_input_placeholder
	data = {'login':xlogin,'uname':uname,'background':background,'text':text,'link':link,'input_background':input_background,'input_text':input_text,'input_border':input_border,'input_placeholder':input_placeholder}
	return HttpResponse(json.dumps(data), content_type="application/json")

def logout(request):
	data = ''
	auth_logout(request)
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_first_channel_post(request, cname):
	ch = Channel.objects.get(name=cname)
	post = Post.objects.filter(channel=ch).order_by('-date')[0]
	return posts_to_html(request, post)
	
def get_first_channel_post_raw(request, cname):
	ch = Channel.objects.get(name=cname)
	post = Post.objects.filter(channel=ch).order_by('-date')[0]
	return post

def random_post(request):
	post = Post.objects.all().order_by('?')[0]
	return open_post(request, id=post.id)

def random_channel(request):
	current = request.GET.get('current',0)
	while True:		
		cname = random_channel_name()
		if cname != current:
			break
	return get_channel(request, cname)

def random_channel_name():
	while True:
		random = Channel.objects.order_by('?')[0].name
		if random not in forbidden_channels:
			break
	return random

def get_post(idPost):
	return Post.objects.get(id=idPost)

def show_useronchannel(request,uname, cname):
	return main(request, mode='useronchannel', info=uname +' on ' + cname)

def show_pins(request,uname):
	return main(request, mode='pins', info=uname)

def show_alerts(request):
	return main(request, mode='alerts')

def show_random(request):
	return main(request, mode='random')

def show_stream(request):
	return main(request, mode='stream')

def show_channel(request,channel):
	return main(request, mode='channel', info=channel)

def show_user(request, id):
	return main(request, mode='user', info=id)

def show_new(request):
	return main(request, mode='new')

def show_chat(request, uname):
	return main(request, mode='chat', info=uname)

def show_notes(request):
	return main(request, mode='notes')

def show_inbox(request):
	return main(request, mode='inbox')

def show_chatall(request):
	return main(request, mode='chatall')

def show_sent(request):
	return main(request, mode='sent')

def show_help(request):
	return main(request, mode='help')

def show_settings(request):
	return main(request, mode='settings')

def show_post(request,id):
	return main(request, mode='post', info=id)

def show_top(request):
	return main(request, mode='top')

def show_last_comments(request):
	id = request.GET.get('id',0)
	post = Post.objects.get(id=id)
	cname = post.channel.name
	comments = Comment.objects.filter(post=post).order_by('-id')[:50]
	length = comments.count()
	comments = reversed(list(comments))
	c = comments_to_html(request,comments)
	p = "<input type=\"hidden\" value=\"" + str(post.id) + "\" class=\"post_id\">"
	if length < 20:
		p = post_to_html(request,post)
	comments = p + c
	data = {'comments':comments,'cname':cname}
	return HttpResponse(json.dumps(data), content_type="application/json")

def show_older_comments(request):
	id = request.GET.get('id',0)
	comment = Comment.objects.get(id=id)
	comments = Comment.objects.filter(post=comment.post,id__lt=id).order_by('-id')[:20]
	length = comments.count()
	comments = reversed(list(comments))
	c = comments_to_html(request,comments)
	p = "<input type=\"hidden\" value=\"" + str(comment.post.id) + "\" class=\"post_id\">"
	if length < 20 and length > 0:
		p = post_to_html(request,comment.post)
	comments = p + c
	data = {'comments':comments}
	return HttpResponse(json.dumps(data), content_type="application/json")

def pin_post(request):
	status = ''
	id = request.POST.get('id',0)
	post = Post.objects.get(id=id)
	try:
		pin = Pin.objects.get(user=request.user,post=post)
	except:
		pin = Pin(user=request.user,post=post,date=datetime.datetime.now())
		pin.save()
		if post.user != request.user:
			try:
				a = Alert.objects.get(user=post.user, type='pin', info1=request.user.username, info2=post.id)
			except:
				alert = Alert(user=post.user, type='pin', info1=request.user.username, info2=post.id, date=datetime.datetime.now())
				alert.save()
	num_pins = Pin.objects.filter(post=post).count()
	status = 'ok'
	data = {'status':status, 'num_pins':num_pins}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_pins(request):
	status = ''
	uname = ''
	uname = request.GET.get('uname',0)
	user = User.objects.get(username=uname)
	pins = Pin.objects.filter(user=user).order_by('-id')[:10]
	pins = pins_to_html(request, pins)
	status = 'ok'
	following = ''
	if request.user.is_authenticated():
		try:
			f = Follow.objects.get(followed=User.objects.get(username=uname), follower=request.user)
			following = 'unfollow'
		except:
			following = 'follow'
	data = {'status':status, 'pins':pins, 'uname':uname, 'following':following}
	return HttpResponse(json.dumps(data), content_type="application/json")

def open_new_post(request):
	status = ''
	post = ''
	cname = ''
	arrows = ''
	try:
		post_id = request.GET['post_id']
		post = Post.objects.filter(id=post_id)[0]
		arrows = get_new_arrows(request, post)
		cname = 'new'
		post = posts_to_html(request, post, 'new')
		status = 'ok'
	except:
		pass
	data = {'post':post, 'cname':cname, 'arrows':arrows, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def open_top_post(request):
	status = ''
	post = ''
	cname = ''
	arrows = ''
	try:
		post_id = request.GET['post_id']
		post = Post.objects.filter(id=post_id)[0]
		arrows = get_top_arrows(request,post)
		cname = 'top'
		post = posts_to_html(request,post,'top')
		status = 'ok'
	except:
		pass
	data = {'post':post, 'cname':cname, 'arrows':arrows, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def open_user_post(request):
	status = ''
	post = ''
	cname = ''
	arrows = ''
	try:
		post_id = request.GET['post_id']
		post = Post.objects.filter(id=post_id)[0]
		arrows = get_user_arrows(post)
		cname = post.user.username
		post = posts_to_html(request,post,'user')
		status = 'ok'
	except:
		pass
	data = {'post':post, 'cname':cname, 'arrows':arrows, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_channel(request, cname=''):
	if cname == '':
		cname = slugify(request.GET['cname'])
	if cname in forbidden_channels:
		cname = random_channel_name()
	posts = ''
	status = 'ok'
	if request.user.is_authenticated():
		try:
			v = Visited.objects.get(user=request.user, channel=cname)
			v.count = v.count + 1
			v.save()
		except:
			v = Visited(user=request.user, channel=cname, count=1)
			v.save()
	try:
		channel = Channel.objects.get(name=cname)
		posts = get_channel_posts(request, channel)
	except:
		pass
	if cname.strip() == '':
		status = 'empty'
	data = {'cname': cname, 'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_channel_posts(request, channel):
	posts = Post.objects.filter(channel=channel).order_by('-id')[:10]
	return posts_to_html(request, posts)

def get_channel_list(request):
	status = 'ok'
	if request.user.is_authenticated():
		channels = visited_channels_to_html(request);
	else:
		channels = random_channels_to_html()
	data = {'status':status, 'channels': channels}
	return HttpResponse(json.dumps(data), content_type="application/json")
	
def get_user_arrows(post):
	arrows = 'none'
	arrow_prev = False
	arrow_next = False
	try:
		prev_post = Post.objects.filter(user=post.user, id__gt=post.id).order_by('date')[0]
		arrow_prev = True
	except:
		pass
	try:
		next_post = Post.objects.filter(user=post.user, id__lt=post.id).order_by('-date')[0]
		arrow_next = True
	except:
		pass
	if arrow_prev and arrow_next:
		arrows = 'both'
	if arrow_prev and not arrow_next:
		arrows = 'prev'
	if arrow_next and not arrow_prev:
		arrows = 'next'
	return arrows
		
def next_channel_post(request):
	data = ''
	try:
		post_id = request.GET['post_id']
		post = Post.objects.get(id=post_id)
		next_post = Post.objects.filter(channel=post.channel, id__lt=post.id).order_by('-date')[0]
		post = posts_to_html(request, next_post)
		arrows = get_channel_arrows(next_post)
		data = {'post':post, 'arrows':arrows}
	except:
		pass
	return HttpResponse(json.dumps(data), content_type="application/json") 

def prev_channel_post(request):
	data = ''
	try:
		post_id = request.GET['post_id']
		post = Post.objects.get(id=post_id)
		prev_post = Post.objects.filter(channel=post.channel, id__gt=post.id).order_by('date')[0]
		post = posts_to_html(request, prev_post)
		arrows = get_channel_arrows(prev_post)
		data = {'post':post, 'arrows':arrows}
	except:
		pass
	return HttpResponse(json.dumps(data), content_type="application/json")
	
def next_user_post(request):
	data = ''
	arrows = 'none'
	try:
		post_id = request.GET['post_id']
		post = Post.objects.get(id=post_id)
		next_post = Post.objects.filter(user=post.user, date__lt=post.date).order_by('-date')[0]
		arrows = get_user_arrows(next_post)
		next_post = posts_to_html(request, next_post, 'history')
		data = {'post':next_post, 'arrows':arrows}
	except:
		pass
	return HttpResponse(json.dumps(data), content_type="application/json") 

def prev_user_post(request):
	data = ''
	try:
		post_id = request.GET['post_id']
		post = Post.objects.get(id=post_id)
		prev_post = Post.objects.filter(user=post.user, date__gt=post.date).order_by('date')[0]
		arrows = get_user_arrows(prev_post)
		prev_post = posts_to_html(request, prev_post, 'history')
		data = {'post':prev_post, 'arrows':arrows}
	except:
		pass
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_pms(request):
	data = ''
	last_pm_id = request.GET.get('last_pm_id',0)
	ss = Silenced.objects.filter(user=request.user)
	n = 20
	bl = []
	senders = []
	while True:
		pmr = PrivateMessage.objects.filter(user=request.user,hidden=False,id__lt=last_pm_id).exclude(sender__username__in=[s.brat for s in ss] + senders).order_by('-id')[:n]
		pms = PrivateMessage.objects.filter(sender=request.user, hidden=False, id__lt=last_pm_id).exclude(info1='welcome').order_by('-id')[:n]
		pmx = sorted(itertools.chain(pmr, pms), key=attrgetter('date'), reverse=True)[:n]
		l = list(pmx)
		bl = bl + l
		bl = remove_duplicate_senders(request, bl)
		senders = get_senders_list(request,bl)
		last_pm_id = bl[-1].id
		if len(bl) >= 20 or pmr.count() == 0:
			break
	pms = pm_to_html(request, bl)
	status = 'ok'
	data = {'pms':pms, 'status':status,'count':len(bl)}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_chatall(request):
	data = ''
	messages = ''
	status = 'error'
	last_pm_id = request.GET.get('last_pm_id', 0)
	if last_pm_id != 0:
		messages = get_chat_messages(request, last_pm_id)
		messages = chat_to_html(request,messages,'chatall')
		status = 'ok'
	data = {'messages':messages, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_channel(request):
	data = ''
	messages = ''
	status = 'error'
	id = request.GET.get('id', 0)
	post = Post.objects.get(id=id)
	posts = Post.objects.filter(channel=post.channel, id__lt=id).order_by('-id')[:10]
	posts = posts_to_html(request,posts)
	if posts != '':
		status = 'ok'
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_useronchannel(request):
	data = ''
	messages = ''
	status = 'error'
	id = request.GET.get('id',0)
	post = Post.objects.get(id=id)
	posts = Post.objects.filter(user=post.user,channel=post.channel, id__lt=post.id).order_by('-id')[:10]
	posts = posts_to_html(request,posts)
	if posts != '':
		status = 'ok'
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_user(request):
	data = ''
	messages = ''
	status = 'error'
	id = request.GET.get('id',0)
	post = Post.objects.get(id=id)
	posts = Post.objects.filter(user=post.user, id__lt=id).order_by('-id')[:10]
	posts = posts_to_html(request,posts,'user')
	if posts != '':
		status = 'ok'
	data = {'posts':posts, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_pins(request):
	status = 'error'
	id = request.GET.get('id',0)
	pin = Pin.objects.get(id=id)
	pins = Pin.objects.filter(user=pin.user,id__lt=id).order_by('-id')[:10]
	pins = pins_to_html(request,pins)
	status = 'ok'
	data = {'pins':pins, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_chat(request):
	data = ''
	messages = ''
	status = 'error'
	last_pm_id = request.GET.get('last_pm_id',0)
	if last_pm_id != 0:
		pm = PrivateMessage.objects.get(id=last_pm_id)
		if pm.user.username == request.user.username:
			peer = pm.sender
		else:
			peer = pm.user
		messages = get_chat_history(request, peer, last_pm_id)
		messages = chat_to_html(request,messages)
		status = 'ok'
	data = {'messages':messages, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_sent(request):
	data = ''
	messages = ''
	status = 'error'
	last_pm_id = request.GET.get('last_pm_id',0)
	if last_pm_id != 0:
		messages = get_sent_messages(request, last_pm_id)
		messages = chat_to_html(request,messages,'sent')
		status = 'ok'
	data = {'messages':messages, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_notes(request):
	notes = Note.objects.filter(user=request.user).order_by('-id')[:20]
	notes = notes_to_html(request,notes)
	status = 'ok'
	data = {'notes':notes, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def load_more_notes(request):
	data = ''
	notes = ''
	status = 'error'
	last_note_id = request.GET.get('last_note_id',0)
	if last_note_id != 0:
		notes = Note.objects.filter(user=request.user, id__lt=last_note_id).order_by('-id')[:20]
		notes = notes_to_html(request,notes)
		status = 'ok'
	data = {'notes':notes, 'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def delete_note(request):
	status = ''
	id = request.GET['id']
	note = PrivateMessage.objects.get(id=id)
	note.delete()
	status = 'ok'
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def set_theme(request):
	background = request.POST['theme_background']
	text = request.POST['theme_text']
	link = request.POST['theme_link']
	input_background = request.POST['theme_input_background']
	input_text = request.POST['theme_input_text']
	input_border = request.POST['theme_input_border']
	input_placeholder = request.POST['theme_input_placeholder']
	scroll_background = request.POST['theme_scroll_background']
	embed_option = request.POST['embed_option']
	p = get_profile(request.user)
	p.theme_background = background
	p.theme_text = text
	p.theme_link = link
	p.theme_input_background = input_background
	p.theme_input_text = input_text
	p.theme_input_border = input_border
	p.theme_input_placeholder = input_placeholder
	p.theme_scroll_background = scroll_background
	p.embed_option = embed_option
	p.save()
	status = 'ok'
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def silence(request):
	status = ''
	uname = request.GET['uname']
	brat = User.objects.get(username=uname)
	ss = Silenced.objects.filter(brat=brat)
	if not ss:
		s = Silenced(user=request.user,brat=brat)
		s.save()
	status = 'ok'
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def unsilence(request):
	status = ''
	uname = request.GET['uname']
	brat = User.objects.get(username=uname)
	ss = Silenced.objects.filter(brat=brat);
	for s in ss:
		s.delete()
	status = 'ok'
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json")

def silenced(request):
	status = ''
	ss = Silenced.objects.filter(user=request.user)
	html = silenced_to_html(request, ss)
	status = 'ok'
	data = {'status':status,'html':html}
	return HttpResponse(json.dumps(data), content_type="application/json")
	
def slugify(name):
	name = name.strip(' ')
	name = name[0:25]
	name = name.lower()
	name = re.sub('[^a-z0-9ñ]', '', name.encode('utf8'))
	return name
	
def clean_username(username):
	try:
		p = re.compile(r"[a-zA-Z0-9]+")
		strlist = p.findall(username)
		if strlist:
			s = ''.join(strlist)
			if s == username:
				return s
			else:
				return False
		return False
	except:
		return False

def stripper(value):
	return value.replace("<", "")

def admin_users(request):
	if request.user.username in admin_list:
		if request.method == 'POST':
			delete_list = request.POST.getlist('delete_list')
			for uname in delete_list:
				u = User.objects.get(username=uname)
				u.delete()
			return HttpResponseRedirect('.') 
		else:
			c = create_c(request)
			c['users'] = get_users()
			return render_to_response('admin_users.html', c, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/../../../../../../../') 

def delete_user(request, uname):
	if request.user.username in admin_list:
		u = User.objects.get(username=uname)
		u.delete()
	return HttpResponse('ok')

def delete_channel(request):
	data = ''
	if request.user.username in admin_list:
		cname = request.GET['cname']
		channel = Channel.objects.get(name=cname)
		channel.delete()
		data = random_channel_name()
	return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def delete_post(request):
	status = 'ok'
	post_id = request.POST['id']
	post = Post.objects.get(id=post_id)
	channel = post.channel
	if request.user.username in admin_list or request.user == post.user:
		try:
			Comment.objects.filter(post=post)[0]
			status = 'commented'
		except:
			try:
				post.delete()
				if Post.objects.filter(channel=channel).count() <= 0:
					channel.delete()
				status = 'ok'
			except:
				pass
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json") 

@login_required
def delete_comment(request):
	status = 'ok'
	comment_id = request.POST['id']
	comment = Comment.objects.get(id=comment_id)
	if request.user.username in admin_list or request.user == comment.user:
		try:
			Comment.objects.filter(reply=comment)[0]
			status = 'replied'
		except:
			try:
				comment.delete()
				status = 'ok'
			except:
				pass
	data = {'status':status}
	return HttpResponse(json.dumps(data), content_type="application/json") 

def send_global_pm(request):
	if request.user.username in admin_list:
		message = request.GET['message']
		sender = User.objects.get(username='global')
		users = get_users()
		for u in users:
			pm = PrivateMessage(user=u, sender=sender, message=message, date=datetime.datetime.now())
			pm.save()
	return HttpResponse('ok')

def error(request):
	return render_to_response('error.html')

def get_profile(user):
	return Profile.objects.get(user=user)

def get_embed_option(user):
	try:
		return get_profile(user).embed_option
	except:
		return 'embed'

def post_to_html(request, post):
	s = ""
	eo = get_embed_option(request.user)
	s = s + "<div class='post_parent'>"
	s = s + 	"<div class='container'>"
	s = s + 	    "<input type=\"hidden\" value=\"" + str(post.id) + "\" class=\"post_id\">"
	num_pins = Pin.objects.filter(post=post).count()
	if request.user.is_authenticated():
		if Pin.objects.filter(post=post, user=request.user).count() > 0:
			pins = "<a class='pins_status' onClick='pin(\""+str(post.id)+"\"); return false;' href='#'>appreciated (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
		else:
			pins = "<a class='pins_status' onClick='pin(\""+str(post.id)+"\"); return false;' href='#'>appreciate (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
	else:
		pins = "<a class='pins_status' onClick='pin(\""+str(post.id)+"\"); return false;' href='#'>appreciate (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
	if request.user.username in admin_list or request.user == post.user:
		s = s + 	    "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + post.user.username + "\");return false;' href=\"#\">" + post.user.username + "</a></div><div style='text-align:right;display:table-cell'><a id='delete_post_" + str(post.id) + "' onClick='delete_post(\""+str(post.id)+"\");return false;' href='#'>delete</a>&nbsp;&nbsp;&nbsp;" + pins + "<a onClick='go_to_bottom();return false;'href='#'>bottom</a></div></div>"
	else:
		s = s + 	    "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + post.user.username + "\");return false;' href=\"#\">" + post.user.username + "</a></div><div style='text-align:right;display:table-cell'>" + pins + "<a onClick='go_to_bottom();return false;'href='#'>bottom</a></div></div>"
	s = s + 	    "<time datetime='" + post.date.isoformat()+"-00:00" + "' class='timeago date'>"+ str(radtime(post.date)) +"</time>"
	if eo == 'embed':
		s = s + 		"<div class='post_content text1'>" + linebreaks(ultralize(post.content)) + "</div>"
	else:
		s = s + 		"<div class='post_content text1'>" + linebreaks(urlize(post.content)) + "</div>"
	s = s + 	"</div>"
	s = s + "</div>"
	return s

def posts_to_html(request, posts, mode="channel"):
	s = ''
	eo = get_embed_option(request.user)
	for p in posts:
		num_comments = Comment.objects.filter(post=p).count()
		post = ""
		if request.user.username in admin_list or request.user == p.user:
			delete = "<a id='delete_post_" + str(p.id) + "' onClick='delete_post(\""+str(p.id)+"\");return false;' href='#'>delete</a>&nbsp;&nbsp;&nbsp;"
		else:
			delete = ""
		num_pins = Pin.objects.filter(post=p).count()
		if request.user.is_authenticated():
			if Pin.objects.filter(post=p, user=request.user).count() > 0:
				pins = "<a class='pins_status' onClick='pin(\""+str(p.id)+"\"); return false;' href='#'>appreciated (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
			else:
				pins = "<a class='pins_status' onClick='pin(\""+str(p.id)+"\"); return false;' href='#'>appreciate (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
		else:
			pins = "<a class='pins_status' onClick='pin(\""+str(p.id)+"\"); return false;' href='#'>appreciate (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
		if mode == "channel":
			nav_link = "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + p.user.username + "\");return false;' href=\"#\">" + p.user.username + "</a></div><div style='text-align:right;display:table-cell'>" + delete + pins + "<a onClick='open_post(\""+str(p.id)+"\");return false' href='#'>comments (" + str(num_comments) + ")</a></div></div>"
		elif mode == "new":
			nav_link = "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + p.user.username + "\");return false;' href=\"#\">" + p.user.username + "</a> &nbsp;on&nbsp; <a onClick='change_channel(\"" + p.channel.name + "\");return false;' href=\"#\">" + p.channel.name + "</a></div><div style='text-align:right;display:table-cell'>" + delete + pins + "<a class='commentslink' id='cl_" + str(p.id) + "' onClick='open_post(\""+str(p.id)+"\");return false' href='#'>comments (" + str(num_comments) + ")</a></div></div>"
		else:
			nav_link = "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + p.user.username + "\");return false;' href=\"#\">" + p.user.username + "</a> &nbsp;on&nbsp; <a onClick='change_channel(\"" + p.channel.name + "\");return false;' href=\"#\">" + p.channel.name + "</a></div><div style='text-align:right;display:table-cell'>" + delete + pins + "<a class='commentslink' id='cl_" + str(p.id) + "' onClick='open_post(\""+str(p.id)+"\");return false' href='#'>comments (" + str(num_comments) + ")</a></div></div>"
		date = "<time datetime='" + p.date.isoformat() +"-00:00" +  "' class='timeago date'>"+ str(radtime(p.date)) +"</time>"
		post = post + "<div class='post_parent' id='post_" + str(p.id) + "'>"
		post = post + 	"<div class='post_container'>"
		post = post + 		  "<div style='width:100%'>"
		post = post + 		  "<input type=\"hidden\" value=\"" + str(p.id) + "\" id='channel_post' class=\"post_id\">"
		post = post + 		  "<div style='padding-bottom:0px' class='details' id='details'>" + nav_link + date + "</div>"
		post = post + 		  "<input type='hidden' value='" + p.user.username + "' class='username'>"
		post = post + 		  "</div>"
		if eo == 'embed':
			post = post + 		  "<div class='post_content text1'>" + linebreaks(ultralize(p.content)) + "</div>"
		else:
			post = post + 		  "<div class='post_content text1'>" + linebreaks(urlize(p.content)) + "</div>"
		post = post + 	"</div>"
		post = post + "</div>"
		s = s + post
	return s

def pins_to_html(request, posts, mode="channel"):
	s = ''
	eo = get_embed_option(request.user)
	for p in posts:
		num_comments = Comment.objects.filter(post=p.post).count()
		post = ""
		if request.user.username in admin_list or request.user == p.post.user:
			delete = "<a id='delete_post_" + str(p.post.id) + "' onClick='delete_post(\""+str(p.post.id)+"\");return false;' href='#'>delete</a>&nbsp;&nbsp;&nbsp;"
		else:
			delete = ""
		num_pins = Pin.objects.filter(post=p.post).count()
		if request.user.is_authenticated():
			if Pin.objects.filter(post=p.post, user=request.user).count() > 0:
				pins = "<a class='pins_status' onClick='pin(\""+str(p.post.id)+"\"); return false;' href='#'>appreciated (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
			else:
				pins = "<a class='pins_status' onClick='pin(\""+str(p.post.id)+"\"); return false;' href='#'>appreciate (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
		else:
			pins = "<a class='pins_status' onClick='pin(\""+str(p.post.id)+"\"); return false;' href='#'>appreciate (" + str(num_pins) + ")</a>&nbsp;&nbsp;&nbsp;"
		nav_link = "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + p.post.user.username + "\");return false;' href=\"#\">" + p.post.user.username + "</a> &nbsp;on&nbsp; <a onClick='change_channel(\"" + p.post.channel.name + "\");return false;' href=\"#\">" + p.post.channel.name + "</a></div><div style='text-align:right;display:table-cell'>" + delete + pins + "<a onClick='open_post(\""+str(p.post.id)+"\")' href='#'>comments (" + str(num_comments) + ")</a></div></div>"
		date = "<time datetime='" + p.post.date.isoformat()+"-00:00" + "' class='timeago date'>"+ str(radtime(p.post.date)) +"</time>"
		post = post + "<div class='post_parent' id='post_" + str(p.post.id) + "'>"
		post = post + 	"<div class='post_container'>"
		post = post + 		  "<div style='width:100%'>"
		post = post + 		  "<input type=\"hidden\" value=\"" + str(p.id) + "\" class=\"pin_id\">"
		post = post + 		  "<div style='padding-bottom:0px' class='details' id='details'>" + nav_link + date + "</div>"
		post = post + 		  "<input type='hidden' value='" + p.post.user.username + "' class='username'>"
		post = post + 		  "</div>"
		if eo == 'embed':
			post = post + 		  "<div class='post_content text1'>" + linebreaks(ultralize(p.post.content)) + "</div>"
		else:
			post = post + 		  "<div class='post_content text1'>" + linebreaks(urlize(p.post.content)) + "</div>"
		post = post + 	"</div>"
		post = post + "</div>"
		s = s + post
	return s

def comments_to_html(request,comments):
	s = ""
	for c in comments:
		s = s + "<div class='post_parent' id='comment_" + str(c.id) + "'>"
		s = s +  "<div class='container'>"
		s = s +   "<input type=\"hidden\" value=\"" + str(c.id) + "\" class=\"comment_id\">"
		if request.user.username in admin_list or request.user == c.user:
			s = s +   "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + c.user.username + "\");return false;' href=\"#\">" + c.user.username + "</a></div><div style='text-align:right;display:table-cell'><a id='delete_comment_" + str(c.id) + "' onClick='delete_comment(\""+str(c.id)+"\");return false;' href='#'>delete</a>&nbsp;&nbsp;&nbsp;<a onClick='reply_to("+str(c.id)+");return false;'href='#'>reply</a></div></div>"
		else:
			s = s +   "<div style='width:100%;display:table'><div style='text-align:left;display:table-cell'><a onClick='change_user(\"" + c.user.username + "\");return false;' href=\"#\">" + c.user.username + "</a></div><div style='text-align:right;display:table-cell'><a onClick='reply_to("+str(c.id)+");return false;'href='#'>reply</a></div></div>"
		s = s +   "<time datetime='" + c.date.isoformat()+"-00:00" + "' class='timeago date'>"+ str(radtime(c.date)) +"</time>"
		if c.reply:
			s = s + "<div class='quote_body'>"
			s = s + "<span> quote by </span>" + "<a class='quote_username' onClick='change_user(\"" + c.reply.user.username + "\");return false;' href=\"#\">" + c.reply.user.username + "</a>"
			s = s + "<div style='width:100%' class='comment_content reply'>" + linebreaks(urlize(c.reply.content)) + "</div>"
			s = s + "</div>"
			s = s + "<div style='padding-bottom:8px'></div>"
		s = s +   "<div class='comment_content text2'>" + linebreaks(urlize(c.content)) + "</div>"
		s = s +  "</div>"
		s = s + "</div>"
	return s

def chat_to_html(request, posts, mode='default'):
	s = ""
	eo = get_embed_option(request.user)
	for p in posts:
		s = s + "<div class='post_parent'>"
		s = s + "<div class='chat_container'>"
		if p.sender.username == 'note':
			s = s + "<div class='details_note'>"
			s = s + "<a onClick='"
		else:
			s = s + "<div class='details'>"
			if mode=='sent':
				s = s + "<a onClick='chat(\"" + p.user.username + "\");"
			elif mode=='inbox':
				s = s + "<a onClick='chat(\"" + p.sender.username + "\");"
			elif mode=='chatall':
				if p.sender == request.user:
					s = s + "<a onClick='chat(\"" + p.user.username + "\");"
				else:
					s = s + "<a onClick='chat(\"" + p.sender.username + "\");"
			else:
				s = s + "<a onClick='change_user(\"" + p.sender.username + "\");"
		s = s + "return false;' href=\"#\">"
		if mode in ['sent','chatall']:
			if p.sender.username == request.user.username:
				s = s + 'sent to ' + p.user.username
			else:
				s = s + p.sender.username
		else:
			s = s + p.sender.username 
		s = s + "</a></div>"
		s = s + "<time datetime='" + p.date.isoformat()+"-00:00" + "' class='timeago date'>"+ str(radtime(p.date)) +"</time>"
		if eo == 'embed':
			s = s + "<div class='text1'>" + linebreaks(ultralize(p.message)) + "</div>"
		else:
			s = s + "<div class='text1'>" + linebreaks(urlize(p.message)) + "</div>"
		s = s + "<input type='hidden' value='" + str(p.id) + "' id='chat_post' class='id'>"
		s = s + "<input type='hidden' value='" + p.sender.username + "' class='username'>"
		s = s + "<input type='hidden' value='" + p.user.username + "' class='receiver'>"
		s = s + "</div>"
		s = s + "</div>"
	return s

def silenced_to_html(request, ss):
	s = ""
	s = s + "<div id='postscroller' class='scroller'>"
	s = s + "<div id='#silenced_holder'>"
	for si in ss:
		s = s + "<div class='silenced_container'>"
		s = s +  "<div style='font-size:20px;padding-bottom:20px'>" + si.brat.username + "</div>"
		s = s + "</div>"
	s = s + "</div>"
	s = s + "</div>"
	return s

def theme_to_html(request):
	s = "<center>"
	s = s + "<select id='embed_select'><option value='embed'>embed links</option><option value='noembed'>don't embed links (faster)</option></select><br><br>"
	s = s + '<div id="background_picker" class="theme_picker unselectable">background color</div>'
	s = s + '<div id="text_picker" class="theme_picker unselectable">text color</div>'
	s = s + '<div id="link_picker" class="theme_picker unselectable">link color</div>'
	s = s + '<div id="input_background_picker" class="theme_picker unselectable">textbox background color</div>'
	s = s + '<div id="input_text_picker" class="theme_picker unselectable">textbox text color</div>'
	s = s + '<div id="input_border_picker" class="theme_picker unselectable">textbox border color</div>'
	s = s + '<div id="input_placeholder_picker" class="theme_picker unselectable">textbox placeholder color</div>'
	s = s + '<div id="input_scroll_background_picker" class="theme_picker unselectable">scrollbar color</div>'
	s = s + "<br><br> <a href='#' style='font-size:20px' onclick='set_default_theme();return false'> default theme </a>"
	s = s + "<br><br><br><br> <a href='#' style='font-size:20px' onclick='login();return false'> logout </a> <br><br><br><br>"
	s = s + "</center>"
	return s
	
def alerts_to_html(request, alerts):
	ss = ''
	for a in alerts:
		s = ''
		try:
			s = s + "<div class='post_parent'>"
			s = s + '<div class="alert">'
			s = s + "<input type='hidden' value='" + str(a.id) + "' class='alert_id'>"
			s = s + "<time style='padding-bottom:6px' datetime='" + a.date.isoformat()+"-00:00" + "' class='timeago alertdate'>"+ str(radtime(a.date)) +"</time>"
			if a.type == 'pin':	
				s = s + '<a onClick="change_user(\''+ str(a.info1) + '\'); return false();" href="#">' + str(a.info1) + '</a>'
				s = s + ' appreciated your '
				s = s + '<a onClick="open_post('+ str(a.info2) + '); return false();" href="#">post on ' + Post.objects.get(id=int(a.info2)).channel.name + '</a>'
			if a.type == 'follow':	
				s = s + '<a onClick="change_user(\''+ str(a.info1) + '\'); return false();" href="#">' + str(a.info1) + '</a>'
				s = s + ' started following you'
			if a.type == 'comment':
				comment = Comment.objects.get(id=int(a.info3))
				s = s + '<a onClick="change_user(\''+ str(a.info1) + '\'); return false();" href="#">' + str(a.info1) + '</a>'
				s = s + ' commented on your '
				s = s + '<a onClick="open_post('+ str(a.info2) + '); return false();" href="#">post on ' + Post.objects.get(id=int(a.info2)).channel.name + '</a>'		
				s = s + '<div class="text2" style="padding-top:5px">' + linebreaks(urlize(comment.content)) + '</div>'	
				s = s + "<div style='padding-top:10px'></div>"
				s = s + "<input placeholder='reply' type='text' class='alert_reply_input' onkeydown='if(event.keyCode == 13){reply_to_comment(this.value, " + str(comment.id) + ",false);}'>"	
			if a.type == 'mention':
				comment = Comment.objects.get(id=int(a.info3))
				s = s + '<a onClick="change_user(\''+ str(a.info1) + '\'); return false();" href="#">' + str(a.info1) + '</a>'
				s = s + ' mentioned you in a '
				s = s + '<a onClick="open_post('+ str(a.info2) + '); return false();" href="#">post on ' + Post.objects.get(id=int(a.info2)).channel.name + '</a>'
				s = s + '<div class="text2" style="padding-top:5px">' + linebreaks(urlize(comment.content)) + '</div>'
				s = s + "<div style='padding-top:10px'></div>"
				s = s + "<input placeholder='reply' type='text' class='alert_reply_input' onkeydown='if(event.keyCode == 13){reply_to_comment(this.value, " + str(comment.id) + ",false);}'>"	
			if a.type == 'reply':
				comment = Comment.objects.get(id=int(a.info3))
				s = s + '<a onClick="change_user(\''+ str(a.info1) + '\'); return false();" href="#">' + str(a.info1) + '</a>'
				s = s + ' replied to you in a '
				s = s + '<a onClick="open_post('+ str(a.info2) + '); return false();" href="#">post on ' + Post.objects.get(id=int(a.info2)).channel.name + '</a>'
				s = s + "<div style='padding-top:8px'></div>"
				s = s + "<div class='reply'>"
				s = s + "------------------------ <span style='font-style:italic;font-size:12px'> you said </span> ------------------------<br>"
				s = s + linebreaks(urlize(comment.reply.content))
				s = s + "<br> ---------------------------------------------------------"
				s = s + "</div>"
				s = s + "<div style='padding-bottom:4px'></div>"
				s = s + "<div class='text2' style=''>" + linebreaks(urlize(comment.content)) + "</div>"
				s = s + "<div style='padding-top:10px'></div>"
				s = s + "<input placeholder='reply' type='text' class='alert_reply_input' onkeydown='if(event.keyCode == 13){reply_to_comment(this.value, " + str(comment.id) + ",false);}'>"	
			s = s + '</div>'
			s = s + '</div>'
			ss = ss + s
		except:
			continue
	return ss

def random_channels_to_html():
	channels = Channel.objects.all().order_by('?')[:50]
	s = ""
	for c in channels:
		s = s + "<a href='#' onclick='hide_overlay();change_channel(\"" + c.name + "\");return false;'class='channels_item'>" + c.name + "</a>"
	return s

def visited_channels_to_html(request):
	visited = Visited.objects.filter(user=request.user).order_by('-count')[:50]
	s = ""
	for v in visited:
		s = s + "<a href='#' onclick='hide_overlay();change_channel(\"" + v.channel + "\");return false;'class='channels_item'>" + v.channel + "</a>"
	return s

@csrf_exempt
def paste_form(request):
	if request.method == 'POST':
		text = request.POST['text']
		if len(text) > 100000 or len(text.strip()) < 1:
			c = create_c(request)
			return render_to_response('paste_form.html', c, context_instance=RequestContext(request))	
		paste = Paste(content=text, date=datetime.datetime.now())
		paste.save()
		return HttpResponseRedirect('/paste/' + str(paste.id))
	else:
		c = create_c(request)
		return render_to_response('paste_form.html', c, context_instance=RequestContext(request))

def show_paste(request, id):
	c = create_c(request)
	paste = Paste.objects.get(id=id)
	c['paste'] = paste
	return render_to_response('paste.html', c, context_instance=RequestContext(request))