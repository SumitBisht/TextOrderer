from distutils.core import setup
import py2exe

windows = [{'script': "ReOrderer.py"}]
options = {
    'py2exe': {
        'dll_excludes': ['MSVCP90.dll'],
        'excludes': ['.git'],
        'includes': ['lxml.etree', 'lxml._elementpath', 'gzip'],
     }
}

setup(windows=['ReOrderer.py'], data_files = None, options = options)
