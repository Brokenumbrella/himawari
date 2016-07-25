# -*- coding: utf-8 -*-
"""
Definition of urls for himawari.
"""

from django.conf.urls import include, url
from django.contrib import admin
import django.contrib.auth.views
import app.views
from django.contrib.auth import views as auth_views
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views
import app.views
from django.contrib.auth import views as auth_views
from django.conf import settings

urlpatterns = [
    url(r'^$', app.views.home, name='home'),
    url(r'^about/$', app.views.about, name='about'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout' ),
    url(r'^accounts/profile/$', app.views.login_after, name='login_after'),
    url(r'^accounts/(?P<member_id>[0-9]+)/profile/$', app.views.AccountView.detail, name='account_detail'),
    url(r'^accounts/(?P<member_id>[0-9]+)/edit/$', app.views.AccountView.edit, name='account_edit'),
    url(r'^memberlist/$', app.views.MemberView.list, name='member_list'),
    url(r'^member/(?P<member_id>[0-9]+)/$', app.views.MemberView.detail, name='member_detail'),
    url(r'^member/new/$', app.views.MemberView.new, name='member_new'),
    url(r'^member/(?P<member_id>[0-9]+)/edit/$', app.views.MemberView.edit, name='member_edit'),
    url(r'^member/(?P<member_id>[0-9]+)/delete/$', app.views.MemberView.delete, name='member_delete'),
    url(r'^articlelist/$', app.views.ArticleView.list, name='article_list'),
    url(r'^article/(?P<article_id>[0-9]+)/$', app.views.ArticleView.detail, name='article_detail'),
    url(r'^article/(?P<article_id>[0-9]+)/edit/$', app.views.ArticleView.edit, name='article_edit'),
    url(r'^article/new/$', app.views.ArticleView.new, name='article_new'),
    url(r'^article/(?P<article_id>[0-9]+)/delete/$', app.views.ArticleView.delete, name='article_delete'),

    url(r'^entrylist/$', app.views.EntryView.list, name='entry_list'),
    url(r'^entry/(?P<entry_id>[0-9]+)/$', app.views.EntryView.detail, name='entry_detail'),
    url(r'^entry/(?P<member_id>[0-9]+)/member/$', app.views.EntryView.entry_member, name='entry_member'),
    url(r'^entry/new/$', app.views.EntryView.new, name='entry_new'),
    url(r'^entry/(?P<entry_id>[0-9]+)/edit/$', app.views.EntryView.edit, name='entry_edit'),
    url(r'^entry/(?P<entry_id>[0-9]+)/delete/$', app.views.EntryView.delete, name='entry_delete'),

    url(r'^entry/(?P<entry_id>[0-9]+)/like/$', app.views.EntryView.like_entry, name='like_entry'),
    url(r'^entry/(?P<member_id>[0-9]+)/voted/$', app.views.EntryView.voted_entry, name='voted_entry'),
    url(r'^entry/(?P<entry_id>[0-9]+)/unlike/$', app.views.EntryView.unlike_entry, name='unlike_entry'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$','django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
]
