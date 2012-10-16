from setuptools import setup, find_packages
import os

version = '1.2.6'
maintainer = 'Philipp Gross'
tests_require = ['zope.testing',
                 'plone.app.testing',
                 'plone.mocktestcase',
                 ]

setup(name='ftw.dashboard.portlets.recentlymodified',
      version=version,
      description="Recently modified portlet for the dashboard",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Plone :: 4.0",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules", ],
      keywords='',
      author='4teamwork GmbH',
      maintainer=maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.dashboard.portlets.recentlymodified',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.dashboard', 'ftw.dashboard.portlets'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      install_requires=[
          'setuptools',
          'collective.js.jqsmartTruncation',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
        # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
        """,
      )
