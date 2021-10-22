import os
from setuptools import setup, find_packages

long_desc = None
if os.path.exists('README.rst'):
    long_desc = open('README.rst').read()

version = '0.0.1'

setup(
    name='Spektrum',
    version=version,
    packages=find_packages(exclude=('tests')),
    url='https://github.com/liquidweb/spektrum',
    license='MIT License',
    author='LiquidWeb Quality Engineering',
    author_email='software-qa@liquidweb.com',
    description='Spektrum is a spec-based testing library to help facilitate BDD-testing in Python.',
    long_description=long_desc,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ),
    python_requires='>=3.5',
    tests_require=['pytest', 'flake8'],
    install_requires=[
        'colored',
        'docopt',
        'pike>=0.1.0',
        'coverage',
    ],
    entry_points = {
        'console_scripts': [
            'specter = specter.__main__:main'
        ]
    },
)
