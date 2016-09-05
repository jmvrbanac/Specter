import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

long_desc = None
if os.path.exists('README.rst'):
    long_desc = open('README.rst').read()

version = '0.5.1'

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
        'Programming Language :: Python :: 3.4',
    ),
    tests_require=['pytest', 'flake8'],
    install_requires=['pike>=0.1.0', 'pyevents', 'coverage', 'six', 'astor'],
    entry_points = {
        'console_scripts':
        ['specter = specter.runner:activate']}
)
