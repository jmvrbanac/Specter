import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read_requires(relative):
    try:
        abs_path = os.path.abspath(relative)
        contents = open(abs_path, 'r').read()
    except IOError:
        # We should only hit this when we are using tox
        return []
    return [l for l in contents.split('\n') if l != '']

long_desc = None
if os.path.exists('pypi_description.rst'):
    long_desc = open('pypi_description.rst').read()

setup(
    name='Specter',
    version='0.1.6',
    packages=['specter'],
    url='https://github.com/jmvrbanac/Specter',
    license='MIT License',
    author='John Vrbanac',
    author_email='john.vrbanac@linux.com',
    description='Specter is a spec-based testing library to help facilitate BDD-testing in Python.',
    long_description=long_desc,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
    tests_require=read_requires('./tools/test-requires'),
    install_requires=['pynsive', 'pyevents', 'coverage'],
    entry_points = {
        'console_scripts':
        ['specter = specter.runner:activate']}
)

