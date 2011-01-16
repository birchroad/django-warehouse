'''
Created on Jan 12, 2011

@author: peterm
'''
from models import Item
from django.forms import ModelForm

class ItemForm(ModelForm):
    class Meta:
        model = Item
        exclude = ('updated_by')