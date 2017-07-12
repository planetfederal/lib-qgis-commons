import os
import inspect

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


def _callerPath():
    stack = inspect.stack()
    parentframe = stack[2][0]
    name = []
    module = inspect.getmodule(parentframe)
    return module.__file__
