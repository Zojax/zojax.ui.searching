##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Setup for zojax.ui.searching package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0.2.1dev'


setup(name = 'zojax.ui.searching',
      version = version,
      author = 'Nikolay Kim',
      author_email = 'fafhrd91@gmail.com',
      description = "Search form for zojax",
      long_description = (
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      url='http://zojax.net/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['zojax','zojax.ui'],
      install_requires = ['setuptools',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
                          'zope.traversing',
                          'zope.app.security',
                          'zope.app.component',
                          'zojax.catalog',
                          'zojax.portlet',
                          'zojax.batching',
                          'zojax.formatter',
                          'zojax.layoutform',
                          'zojax.statusmessage',
                          'zojax.widget.checkbox',
                          'zojax.content.shortcut',
                          'zojax.content.textannotation'
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.testbrowser',
                                  'zope.securitypolicy',
                                  'zojax.security',
                                  'zojax.pageelement',
                                  'zope.app.zcmlfiles',
                                  'zojax.autoinclude',
                                  'zojax.content.browser',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
