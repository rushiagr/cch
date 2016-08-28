"""
Cloud CLI for Humans.

Run 'lsvm' or 'mkvm' to list or create a VM in EC2 cloud.
"""

from setuptools import find_packages, setup

dependencies = ['click', 'boto3', 'prettytable']

setup(
    name='cch',
    version='0.1.1',
    url='https://github.com/rushiagr/cch',
    license='BSD',
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
