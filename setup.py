import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

long_desc = None
if os.path.exists('pypi_description.rst'):
    long_desc = open('pypi_description.rst').read()

version = ''
if os.path.exists('.package-version'):
    version = open('.package-version', 'r').readline().strip()

setup(
    name='Specter',
    version=version,
    packages=find_packages(exclude=('tests')),
    url='https://github.com/jmvrbanac/Specter',
    license='MIT License',
    author='John Vrbanac',
    author_email='john.vrbanac@linux.com',
    description='Specter is a spec-based testing library to help facilitate BDD-testing in Python.',
    long_description=long_desc,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
    tests_require=['tox', 'nose', 'flake8'],
    install_requires=['pike>=0.1.0', 'pyevents', 'coverage', 'six'],
    entry_points = {
        'console_scripts':
        ['specter = specter.runner:activate']}
)
