'''
Created on Jan 12, 2011

@author: peterm
'''
from django.db.models import Manager

__all__ = ['LocationManager', 'ItemManager', 'BomEntryManager']

class LocationManager(Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)
    
class ItemManager(Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)
    
class BomEntryManager(Manager):
    def get_by_natural_key(self, parent_code, item_code):
        return self.get(parent__code=parent_code, item__code=item_code)
