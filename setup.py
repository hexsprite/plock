from setuptools import setup, find_packages

version = '0.0'

setup(name='plock',
      version=version,
      description="",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'megrok.rdb',
                        # Add extra requirements here
                        ],
      entry_points = """
      [console_scripts]
      plock-debug = plock.startup:interactive_debug_prompt
      plock-ctl = plock.startup:zdaemon_controller
      [paste.app_factory]
      main = plock.startup:application_factory
      """,
      )
