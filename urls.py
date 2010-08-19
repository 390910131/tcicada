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
)
