from distutils.core import setup

setup(
    name='Specter',
    version='0.1.0',
    packages=['specter'],
    url='https://github.com/jmvrbanac/Specter',
    license='MIT License',
    author='John Vrbanac',
    author_email='john.vrbanac@linux.com',
    description='Specter is a spec-based testing library to help facilitate BDD in Python.',
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points = {
        'console_scripts':
        ['specter = specter.runner:activate']}
)

