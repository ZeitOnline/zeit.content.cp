# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='zeit.content.cp',
    version='0.7dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://intra.gocept.com/projects/projects/zeit-cms',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit', 'zeit.content'],
    install_requires=[
        'FeedParser',
        'gocept.lxml',
        'gocept.mochikit>=1.4.2.2',
        'gocept.runner',
        'lxml',
        'python-cjson',
        'setuptools',
        'stabledict',
        'zc.sourcefactory',
        'zeit.cms>=1.20.2',
        'zeit.content.quiz>=0.4.2',
        'zeit.find',
        'zope.app.pagetemplate',
        'zope.component',
        'zope.container>=3.8.1',
        'zope.event',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.viewlet',
    ],
    entry_points = dict(
        console_scripts =
        ['refresh-feeds = zeit.content.cp.feed:refresh_all',])
)
