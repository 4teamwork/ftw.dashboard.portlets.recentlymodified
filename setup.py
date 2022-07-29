from setuptools import setup, find_packages
import os

version = '2.0.0.dev0'
maintainer = 'Philipp Gross'

tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'plone.mocktestcase',
    'zope.testing',
    'plone.app.contenttypes',
]

setup(name='ftw.dashboard.portlets.recentlymodified',
      version=version,
      description="Recently modified portlet for the dashboard",
      long_description=open("README.rst").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw dashboard portlet recentlymodified',
      author='4teamwork AG',
      maintainer=maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.dashboard.portlets.recentlymodified',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.dashboard', 'ftw.dashboard.portlets'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'Plone',
          'setuptools',
          'ftw.upgrade',
          'ftw.dashboard.dragndrop>=2',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points="""
        # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
        """,
      )
