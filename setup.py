"""
CCH - Cloud CLI for Humans.

Very simple cloud CLI, specifically designed for human use. Strictly forbidden
for scripts' consumption :)

Just type `mkvm` and it will help you step-by-step create a virtual machine, by
first letting you provide a flavor from availale flavors, then similarly a
security group, and then root volume storage.  All the other commands are just
as simple!

View demo at: https://asciinema.org/a/ektm98481nniu7rldc1ncu5af


Installation
------------

    pip install cch

More details at https://github.com/rushiagr/cch/blob/master/README.md
"""

from setuptools import find_packages, setup

dependencies = ['click', 'awscli', 'boto3', 'prettytable', 'future']

setup(
    name='cch',
    version='0.1.19',
    url='https://github.com/rushiagr/cch',
    license='Apache 2.0',
    author='Rushi Agrawal',
    author_email='rushi.agr@gmail.com',
    description='Cloud CLI for Humans',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'lsvm = cch.cli:lsvm',
            'mkvm = cch.cli:mkvm',
            'rmvm = cch.cli:rmvm',
            'stpvm = cch.cli:stpvm',

            'lskp = cch.cli:lskp',
            'mkkp = cch.cli:mkkp',
            'rmkp = cch.cli:rmkp',

            'lssg = cch.cli:lssg',
            'mksg = cch.cli:mksg',
            'rmsg = cch.cli:rmsg',

            'lsimg = cch.cli:lsimg',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
