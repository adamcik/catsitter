import os

registry = []

def decode(string):
    if isinstance(string, unicode) or string is None:
        return string

    for encoding in ['utf-8', 'iso-8859-1']:
        try:
            return string.decode(encoding)
        except UnicodeDecodeError:
            pass
    return string

def register(regexp):
    def wrapper(func):
        registry.append((regexp, func))
        return func
    return wrapper

def get_data_file(name):
    return os.path.join('data', name)
