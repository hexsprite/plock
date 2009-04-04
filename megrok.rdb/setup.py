from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.rdb',
      version=version,
      description="SQLAlchemy based RDB support for Grok.",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Grok Team',
      author_email='grok-dev@zope.org',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'grok >= 0.13',
          'SQLAlchemy > 0.5beta2',
          'zope.sqlalchemy',
          'z3c.saconfig',
         ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
