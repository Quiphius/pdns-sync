from setuptools import setup

setup(name='pdnssync',
      version='0.1',
      description='PowerDNS sync tool',
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
      scripts=['bin/pdns-sync'],
      install_requires=[
          'psycopg2',
      ],
      zip_safe=False)
