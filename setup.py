from setuptools import setup, find_packages
import os

version = open("ftw/dashboard/portlets/recentlymodified/version.txt").read().strip()

setup(name='ftw.dashboard.portlets.recentlymodified',
      version=version,
      description="recentlymodified portlet - auge",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='philippegross',
      author_email='mailto:info@4teamwork.ch',
      url='http://plone.org/products/ftw.dashboard.portlets.recentlymodified/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.dashboard'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.pipbox',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
