from django.db import models

'''
Created on Jan 7, 2014

@author: Andrew Oberlin
'''

'''
    Model that we can use to get rid of the Django stuff, but still use the model
    concept while coding.
'''
class CassaModel(models.Model):
    '''
        Overriding the default save method to remove Django operation.
        
        This save will do nothing and will not be used.
    '''
    def save(self):
        pass
    
    '''
        Updates this user with the values put into the map.
        
        @param other: The map of values to use for updating the model.
    '''
    def update(self, other):
        for attrKey in self.__dict__.keys():
            if attrKey in other:
                setattr(self, attrKey, other[attrKey])
    
    '''
        Overriding the default delete method to remove Django operation.
        
        This delete will do nothing and will not be used.
    '''
    def delete(self):
        pass
    
    class Meta:
        app_label = u'users'