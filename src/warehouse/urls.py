
from django.conf.urls.defaults import *

urlpatterns = patterns('warehouse.views',
     url(r'^$', 'index', name='warehouse_index'),
     
     url(r'^item/$', 'item_list', name='warehouse_item_index'),
     url(r'^item/(?P<item_code>\w+)/$', 'item_detail', name='warehouse_item_detail'),
     
 #   url(r'^booking/$', 'booking_index', name='checkin_booking_index'),
    
#    url(r'^booking/new/$', 'booking', {'booking_id':0},
#            name='checkin_booking_new'),
#    
#    url(r'^booking/(?P<booking_id>\d+)/$',
#            'booking', name='checkin_booking_detail'),
    
#    url(r'^booking/(?P<booking_id>\d+)/contact/new/$',
#            'contact', {'contact_id':0}, 'checkin_contact_new'),
    
#    url(r'^message/$', 'message', name="checkin_message_index"),
#    url(r'^message/new/$', 'message_new', name="checkin_message_new"),

)
