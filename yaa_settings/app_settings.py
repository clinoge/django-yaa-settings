"""
AppSettings class
"""
import sys

from django.utils import six
from django.conf import settings


Undefined = object()


class AppSettingsType(type):
    def __init__(self, name, bases, dct):
        super(AppSettingsType, self).__init__(name, bases, dct)

        if dct.get('abstract', False):
            return

        sys.modules[self.__module__] = self()


class AppSettings(six.with_metaclass(AppSettingsType)):
    abstract = True
    prefix = None

    def __getattribute__(self, attr):
        # Get reserved and private attributes directly
        if attr.startswith('_') or attr in ['abstract', 'prefix']:
            return super(AppSettings, self).__getattribute__(attr)

        dct = self.__class__.__dict__
        if attr in dct:
            # Look in Django settings for an override
            settings_attr = attr
            if self.prefix:
                settings_attr = '{}_{}'.format(self.prefix, attr)
            val = getattr(settings, settings_attr, Undefined)

            # Callables are called with the value from settings, or None
            if callable(dct[attr]):
                if val is Undefined:
                    val = None
                return dct[attr](self, val)

            # Handle a property (defined on the AppSettings subclass)
            if isinstance(val, property):
                return val.__get__(self, self.__class__)

            # If not overridden, return default value
            if val is Undefined:
                if isinstance(dct[attr], property):
                    return dct[attr].__get__(self, self.__class__)
                return dct[attr]

            return val

        raise AttributeError('No setting "{}"'.format(attr))