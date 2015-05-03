PDNS-Sync
=========
This is a script to handle generation of zones in a PowerDNS database and it can be used with both
MySQL and PostgreSQL.

Installation
------------
The easiest way to install the package is via ``easy_install`` or ``pip``::

  $ pip install pdnssync

There are also Debian/Ubuntu packages avaible

Usage
-----
There are two tools included in the package, ``pdns-sync`` for syncronizing the files and the database
and ``pdns-export`` for exporting an existing database to stdout.

The recomended set-up is to have all files in a git repos with a common extention (e.g. <file>.dns) and
use ``pdns-sync`` in a hook.

It's possible to have a folder with the files with a common extention (e.g. .txt or .dns) for the zones in a folder and
run in that folder::

  pdns-sync *.dns

Setup for use with git
----------------------
These commands will work in Ubuntu and probably most distributions with some minor changes.

Create an user::

  $ sudo adduser --disabled-password --gecos "DNS Sync User" dns

Become the user and create git repository::

  $ sudo -u dns -s
  $ git init dns

Set config for git so it's possible to push::

  $ git -C dns config receive.denyCurrentBranch ignore

Add ssh keys for the users that will have access to the file .ssh/authorized_keys
and create the hook file ``dns/.git/hooks/post-receive`` with the content::

  #!/bin/sh

  export GIT_WORK_TREE=/home/dns/dns

  export PDNS_DBTYPE=postgresql
  export PDNS_DB=pdns
  export PDNS_DBUSER=pdns
  export PDNS_DBPASSWORD=secret
  export PDNS_DBHOST=localhost

  git checkout -f

  cd $GIT_WORK_TREE
  pdns-sync *.dns

The environment variables are for the database configuration and the values above are the default except for the password 

Make the hook executable::

  chmod +x dns/.git/hooks/post-receive

It is possible to set up a virtualenv and adding a line like this to the script just below the ``#!`` line::

  . /home/dns/.virtualenvs/pdnssync/bin/activate

Just use your own virtualenv name if it's not pdnssync.

To use, just clone the repos as normal, add, delete or change the files, checkin your changes and when the repos is pushed
all the changes will be applied if there are no errors and if there are errors, fix them and try to push again.

To increase the security 

Format
------
This is an example of a domain and a reverse domain in a file::

  D example.com ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com
  M mx1.example.com 20 mx2.example.com

  192.168.0.80 www.example.com

  192.168.0.53 ns1.example.com
  192.168.0.54 ns2.example.com

  192.168.0.25 mx1.example.com
  192.168.0.26 mx2.example.com

  D 0.168.192.in-addr.arpa ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com
