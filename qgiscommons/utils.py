import os
from PyQt4.QtCore import *
import inspect

#==============

def _callerName():
    stack = inspect.stack()
    parentframe = stack[2][0]
    name = []
    module = inspect.getmodule(parentframe)
    name.append(module.__name__)
    if 'self' in parentframe.f_locals:
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':
        name.append( codename )
    del parentframe
    return  ".".join(name)

#=============

def set_plugin_setting(name, value):
    namespace = _callerName.split(".")[0]
    QSettings().setValue(namespace + "/" + name, value)

def plugin_setting(name):
    namespace = _callerName.split(".")[0]
    v = QSettings().value(namespace + "/" + name, None)
    if isinstance(v, QPyNullVariant):
        v = None
    return v

#=================
