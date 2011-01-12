from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^checkin/', include('checkin.urls')),
)
