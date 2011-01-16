from django.db.models import Model, CharField, FloatField, DateTimeField, ForeignKey, BooleanField
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from managers import LocationManager, ItemManager, BomEntryManager 
from managers import ItemJournalManager
from constants import *

__all__ = ['Location', 'Item', 'BomEntry', 'ItemJournal', 'ItemEntry']

class Location(Model):
    code = CharField(_('code'), max_length=25, unique=True)
    description = CharField(_('description'), max_length=100)
    lon = FloatField(_('longitude'), blank=True, null=True)
    lat = FloatField(_('latitude'), blank=True, null=True)
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User)
    objects = LocationManager()
    
    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
    
    def __unicode__(self):
        return u'%s:%s' % (self.code, self.description)
    
    def natural_key(self):
        return (self.code,)
 
    
class Item(Model):
    code = CharField(_('code'), max_length=25, unique=True)
    description = CharField(_('description'), max_length=100)
    #identifier=CharField(_('identifier'), max_length=50, blank=True, null=True)
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User)
    blocked = BooleanField(default=False)
    objects = ItemManager()
    
    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('code',)
    
    def __unicode__(self):
        return u"%s:%s" % (self.code, self.description)
    
    def natural_key(self):
        return (self.code,)
    
    def get_absolute_url(self):
        return reverse('warehouse_item_detail', kwargs={'item_code':self.code})

    def inventory(self, location=None):
        '''
        returns items in inventory for a location (if given) or all.
        '''
        if location:
            sum = self.item_entries.filter(location=location).aggregate(Sum('qty'))['qty__sum']
        else:
            sum = self.item_entries.all().aggregate(Sum('qty'))['qty__sum']
        if sum:
            return sum
        else:
            return 0
    
    def location_inventory(self):
        '''
        Return Locations for the item and it's aggregated .qty_sum
        for self
        '''
        #from warehouse.db import SumCase
        #locations = Location.objects.aggregate(qty_sum=SumCase('item_entries__qty',  when=self.id ))
        
        #TODO: Fixa och använd SumCase eller möjligtvis .extra i stället
        sql = """SELECT loc.*, 
            Sum(CASE WHEN (ie.item_id=%(item)s) THEN ie.qty ELSE 0 END) as qty_sum
            FROM warehouse_location loc LEFT JOIN 
             warehouse_itementry ie ON ie.location_id = loc.id
             GROUP BY ie.location_id
             ORDER BY loc.code
        """
        locations = Location.objects.raw(sql % {'item': self.id})
        return locations

class BomEntry(Model):
    parent = ForeignKey(Item, related_name='bom')
    item = ForeignKey(Item)
    qty = FloatField(_('quantity'))
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    updated_by = ForeignKey(User)
    objects = BomEntryManager()
    
    class Meta:
        verbose_name = _('BOM entry')
        verbose_name_plural = _('BOM entries')
        unique_together = (('parent', 'item'),)
    
    def __unicode__(self):
        return u'%s %s(%d)' % (self.parent, self.item, self.qty)
    
    def natural_key(self):
        return self.parent.natural_key() + self.item.natural_key()
    natural_key.dependencies = ['warehouse.item']




class ItemJournal(Model):
    TYPE_CHOICES = (
        ('INVENTORY', _('Inventory')),
        ('MOVEMENT', _('Movement')),
        ('SALES', _('Sales')),
        ('PURCHASE', _('Purchase')),
    )
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    journal_type = CharField(_('journal type'), max_length=10, choices=TYPE_CHOICES)
    note = CharField(_('note'), max_length=100)
    updated_by = ForeignKey(User)
    objects = ItemJournalManager()
    
    class Meta:
        verbose_name = _('item journal')
        verbose_name_plural = _('item journals')
    
    def __unicode__(self):
        return u'%s' % (self.journal_type)
        
    
    def change(self, item, at_location, qty):    
        bom_list = item.bom.all()
        if len(bom_list) > 0:    
            for bom in bom_list:
                if bom.item.bom.all().count() > 0:
                    self.change(bom.item, at_location, (bom.qty * qty))
                else:
                    self.entries.create(item=bom.item, location=at_location, qty=(bom.qty * qty), related_item=item, updated_by_id=self.updated_by_id)
        else:        
            self.entries.create(item=item, location=at_location, qty=qty, updated_by_id=self.updated_by_id)
    
 
class ItemEntry(Model):
    journal = ForeignKey(ItemJournal, related_name='entries')
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    item = ForeignKey(Item, related_name='item_entries')
    location = ForeignKey(Location, related_name='item_entries')
    qty = FloatField(_('quantity'), default=1)
    related_item = ForeignKey(Item, related_name='related_entries', blank=True, null=True)
    updated_by = ForeignKey(User)
    
    def __unicode__(self):
        return u'%s;%s;%s;%s' % (self.journal, self.item.code, self.location.code, self.qty)
    
