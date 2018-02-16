import os.path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='fec2json',
    version='0.0.1',
    author='Rachel Shorey',
    author_email='rachel.shorey@nytimes.com',
    url='https://github.com/newsdev/fec2json',
    description='Python client for turning a FEC filing csv file into JSON.',
    long_description="",
    packages=['fec2json'],
    entry_points={
        'console_scripts': (
            'fec2json = process_filing:main',
        ),
    },
    license="Apache License 2.0",
    keywords='FEC data parsing json elections finance campaign',
    install_requires=['ujson'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)