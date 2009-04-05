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
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'grokcore.startup',
                        'z3c.testsetup',
                        'megrok.rdb',
                        # Add extra requirements here
                        ],
      entry_points = """
      [console_scripts]
      plock-debug = grokcore.startup:interactive_debug_prompt
      plock-ctl = grokcore.startup:zdaemon_controller
      [paste.app_factory]
      main = grokcore.startup:application_factory
      """,
      )
