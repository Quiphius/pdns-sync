from setuptools import setup

setup(
    name='pdnssync',
    version='0.2',
    description='PowerDNS sync tool',
    long_description='A tool to read a hosts-like file and synconize it with the database used by PowerDNS.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: System :: Systems Administration',
    ],
    keywords='powerdns hosts sync postgresql',
    url='http://github.com/storborg/funniest',
    author='Mikael Olofsson',
    author_email='mikael.olofsson@oet.nu',
    license='MIT',
    packages=['pdnssync'],
    entry_points={
        'console_scripts': ['pdns-sync=pdnssync.main:do_sync',
                            'pdns-export=pdnssync.main:do_export'],
    },
    install_requires=[
        'MySQL-python',
        'psycopg2',
    ],
    platforms=[
        'any',
    ],
    zip_safe=False
)
