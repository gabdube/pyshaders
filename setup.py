#!/usr/bin/env python

from distutils.core import setup
from sys import argv

import glob
from os.path import basename

extensions = []
if not '--no-extensions' in argv:
    for ext in glob.glob('pyshaders_extensions/*.py'):
        if 'create_mmo' in ext or '__init__' in ext:
            continue

        name = basename(ext).split('.')[0]
        extensions.append('pyshaders_extensions.'+name)        

else:
    argv.remove('--no-extensions')
   

setup(name='pyshaders',
      version='1.4.1',
      description='OpenGL shader wrapper for python',
      author='Gabriel Dubé',
      author_email='gdube@azanka.ca',
      license='MIT',
      url='https://github.com/gabdube/pyshaders',
      download_url='https://github.com/gabdube/pyshaders',
      py_modules=['pyshaders']+extensions,
     )
