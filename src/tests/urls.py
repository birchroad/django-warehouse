from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^warehouse/', include('warehouse.urls')),
)
