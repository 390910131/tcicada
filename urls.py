from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from cicada.mvc.feed import RSSRecentNotes, RSSUserRecentNotes
from django.contrib import admin
admin.autodiscover()

rss_feeds = {
    'recent':RSSRecentNotes,
}
rss_user_feeds = {
    'recent':RSSUserRecentNotes,
}

urlpatterns = patterns('',
    # Example:
    # (r'^cicada/', include('cicada.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$','cicada.mvc.views.index'),
    (r'^admin/', include(admin.site.urls)),
    (r'^p/(?P<_page_index>\d+)/$','cicada.mvc.views.index_page'),
    (r'^user/$','cicada.mvc.views.index_user_self'),
    (r'^user/(?P<_username>[a-zA-Z\-_\d]+)/$','cicada.mvc.views.index_user'),
    (r'^user/(?P<_username>[a-zA-Z\-_\d]+)/(?P<_page_index>\d+)/$','cicada.mvc.views.index_user_page'),
    (r'^users/$','cicada.mvc.views.user_index'),
    (r'^users/(?P<_page_index>\d+)/$','cicada.mvc.views.users_list'),
    (r'^signin/$','cicada.mvc.views.signin'),
    (r'^signout/$','cicada.mvc.views.signout'),
    (r'^signup/$','cicada.mvc.views.signup'),
    (r'^settings/$','cicada.mvc.views.settings'),
    (r'^message/(?P<_id>\d+)/$','cicada.mvc.views.detail'),
    (r'^message/(?P<_id>\d+)/delete/$','cicada.mvc.views.detail_delete'),
    (r'^friend/add/(?P<_username>[a-zA-Z\-_\d]+)','cicada.mvc.views.friend_add'),
    (r'^friend/remove/(?P<_username>[a-zA-Z\-_\d]+)','cicada.mvc.views.friend_remove'),
    (r'^api/note/add/','cicada.mvc.views.api_note_add'),
    # Uncomment this for admin:    
    (r'^feed/rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': rss_feeds}),
    (r'^user/feed/rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': rss_user_feeds}),
    (r'^styles/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './statics/styles'}),
    (r'^scripts/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './statics/scripts'}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './statics/images'}),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './statics/uploads'}),
    
)
