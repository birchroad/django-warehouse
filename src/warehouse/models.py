from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from django.contrib.auth.models import User

from managers import LocationManager, ItemManager, BomEntryManager

INVENTORY = 0
MOVEMENT = 1
SALES = 2
PURCHASE = 3

class Location(models.Model):
    code = models.CharField(_('code'), max_length=25, unique=True)
    description = models.CharField(_('description'), max_length=100)
    lon = models.FloatField(_('longitude'), blank=True, null=True)
    lat = models.FloatField(_('latitude'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    updated_by = models.ForeignKey(User)
    objects = LocationManager()
    
    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
    
    def __unicode__(self):
        return u'%s:%s' % (self.code, self.description)
    
    def natural_key(self):
        return (self.code,)
 
    
class Item(models.Model):
    code = models.CharField(_('code'), max_length=25, unique=True)
    description = models.CharField(_('description'), max_length=100)
    #identifier=models.CharField(_('identifier'), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    updated_by = models.ForeignKey(User)
    objects = ItemManager()
    
    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('code',)
    
    def __unicode__(self):
        return u"%s:%s" % (self.code, self.description)
    
    def natural_key(self):
        return (self.code,)

    def inventory(self, location=None):
        if location:
            sum = self.item_entries.filter(location=location).aggregate(Sum('qty'))['qty__sum']
        else:
            sum = self.item_entries.all().aggregate(Sum('qty'))['qty__sum']
        if sum:
            return sum
        else:
            return 0


class BomEntry(models.Model):
    parent = models.ForeignKey(Item, related_name='bom')
    item = models.ForeignKey(Item)
    qty = models.FloatField(_('qty'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    updated_by = models.ForeignKey(User)
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


class ItemJournalManager(models.Manager):
    #TODO: howto ensure all this is done as a transaction?
    def move(self, item, from_location, to_location, qty, updated_by_id):
        journal = ItemJournal(journal_type=ItemJournal.TYPE_CHOICES[MOVEMENT][0], updated_by_id=updated_by_id)
        journal.save()
        journal.change(item, from_location, qty * -1)
        journal.change(item, to_location, qty)
        return journal
    
    def change(self, type_no, item, at_location, qty, updated_by_id):
        journal = ItemJournal(journal_type=ItemJournal.TYPE_CHOICES[type_no][0], updated_by_id=updated_by_id)
        journal.save()
        journal.change(item, at_location, qty)
        return journal

class ItemJournal(models.Model):
    TYPE_CHOICES = (
        ('INVENTORY', _('Inventory')),
        ('MOVEMENT', _('Movement')),
        ('SALES', _('Sales')),
        ('PURCHASE', _('Purchase')),
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    journal_type = models.CharField(_('journal type'), max_length=10, choices=TYPE_CHOICES)
    note = models.CharField(_('note'), max_length=100)
    updated_by = models.ForeignKey(User)
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
    
 
class ItemEntry(models.Model):
    journal = models.ForeignKey(ItemJournal, related_name='entries')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    item = models.ForeignKey(Item, related_name='item_entries')
    location = models.ForeignKey(Location)
    qty = models.FloatField(_('qty'), default=1)
    related_item = models.ForeignKey(Item, related_name='related_entries', blank=True, null=True)
    updated_by = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'%s;%s;%s;%s' % (self.journal, self.item.code, self.location.code, self.qty)
    
