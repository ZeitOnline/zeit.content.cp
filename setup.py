from setuptools import setup, find_packages


setup(
    name='zeit.content.cp',
    version='3.13.0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Centerpage",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'cssselect',
        'feedparser',
        'gocept.cache',
        'gocept.httpserverlayer',
        'gocept.jslint>=0.2',
        'gocept.lxml',
        'gocept.mochikit>=1.4.2.2',
        'gocept.runner>-0.4',
        'gocept.selenium>=2.2.0.dev0',
        'grokcore.component',
        'lxml',
        'pyramid_dogpile_cache2',
        'requests',
        'setuptools',
        'xml-compare',
        'zc.sourcefactory',
        'zeit.cms>=2.90.0.dev0',
        'zeit.content.image>=2.5.1.dev0',
        'zeit.content.quiz>=0.4.2',
        'zeit.content.text>=2.0.2.dev0',
        'zeit.content.video>=2.4.1.dev0',
        'zeit.edit >= 2.13.0.dev0',
        'zeit.find >= 2.7.0.dev0',
        'zeit.retresco >= 1.6.0.dev0',
        'zeit.solr',
        'zope.app.appsetup',
        'zope.app.generations',
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
    entry_points={
        'console_scripts': [
            'refresh-feeds = zeit.content.cp.feed:refresh_all',
        ],
        'fanstatic.libraries': [
            'zeit_content_cp=zeit.content.cp.browser.resources:lib',
        ],
    },
)
