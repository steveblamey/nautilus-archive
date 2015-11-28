#!/usr/bin/env python
# coding: utf-8
from os import path
from distutils.core import setup

PROJECT_DIR = path.dirname(__file__)

extension = [
    ('/usr/share/nautilus-python/extensions',
     [path.join(PROJECT_DIR, 'extension', 'nautilus-archive.py')]),

    ('/usr/share/icons/hicolor/48x48/emblems',
     [path.join(PROJECT_DIR, 'extension', 'emblems', 'emblem-red-tag.png')]),
     
    ('/usr/share/icons/hicolor/scalable/emblems',
     [path.join(PROJECT_DIR, 'extension', 'emblems', 'emblem-red-tag.svg')]),
     
    ('/usr/share/icons/hicolor/48x48/emblems',
     [path.join(PROJECT_DIR, 'extension', 'emblems', 'emblem-green-tag.png')]),
     
    ('/usr/share/icons/hicolor/scalable/emblems',
     [path.join(PROJECT_DIR, 'extension', 'emblems', 'emblem-green-tag.svg')]),
     
    ('/usr/sbin',
     [path.join(PROJECT_DIR, 'scripts', 'tracker-archive-tagged')]),
]

setup(name='nautilus-archive',
      version='0.2',
      description='A file archiving extension for the Nautilus file manager',
      long_description=open('README.rst').read(),
      author='Steve Blamey',
      author_email='sblamey@gmail.com',
      url='http://www.python.org/',
      license='GPL-3',
      platforms=['Linux'],
      data_files=extension,
      py_modules=['trackertag']
     )
