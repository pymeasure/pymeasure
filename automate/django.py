from __future__ import absolute_import
from django.db import models

class Parameter(object):
    
    def __init__(self, unit=None):
        self.unit = unit

class CharParameter(Parameter, models.CharField):

    def __init__(self, *args, **kwargs):
        if 'unit' in kwargs:
            unit = kwargs.pop('unit')
        else:
            unit = None
        Parameter.__init__(self, unit)
        models.CharField.__init__(self, *args, **kwargs)

class IntegerParameter(models.IntegerField, Parameter):

    def __init__(self, *args, **kwargs):
        if 'unit' in kwargs:
            unit = kwargs.pop('unit')
        else:
            unit = None
        Parameter.__init__(self, unit)
        models.IntegerField.__init__(self, *args, **kwargs)

class DecimalParameter(Parameter, models.DecimalField):

    def __init__(self, *args, **kwargs):
        if 'unit' in kwargs:
            unit = kwargs.pop('unit')
        else:
            unit = None
        Parameter.__init__(self, unit)
        models.DecimalField.__init__(self, *args, **kwargs)
    
class FloatParameter(Parameter, models.FloatField):

    def __init__(self, *args, **kwargs):
        if 'unit' in kwargs:
            unit = kwargs.pop('unit')
        else:
            unit = None
        Parameter.__init__(self, unit)
        models.FloatField.__init__(self, *args, **kwargs)
    

class ExperimentModel(models.Model):
    """ Extends the model to provide a method for collecting up the parameters
    after validating them
    """
    
    class Meta:
        abstract = True
    
    def parameters(self):
        """ Collect all parameters and validate them
        """
        self.full_clean() # validate parameters
        cache = {}
        units = {}
        for field in self._meta.fields:
            if issubclass(type(field), Parameter):
                cache[field.name] = getattr(self, field.name)
                units[field.name] = field.unit
        cache['_units'] = units
        return cache
        
    def parameter_fields(self):
        cache = []
        for field in self._meta.fields:
            if issubclass(type(field), Parameter):
                cache.append(field.name)
        return cache
