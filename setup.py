#!/usr/bin/env python
# encoding=utf-8

from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(name='wikidataeditor',
      version='0.0.1',
      description='Wikidata API client',
      long_description=README,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7'
      ],
      keywords='mediawiki wikidata',
      author='Dan Michael O. Heggø',
      author_email='danmichaelo@gmail.com',
      url='https://github.com/danmichaelo/wikidataeditor',
      license='Unlicense',
      packages=['wikidataeditor'],
      install_requires=['requests']
      )
