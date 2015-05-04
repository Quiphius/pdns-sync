PDNS-Sync
=========
This is a script to handle generation of zones in a PowerDNS database and it can be used with both
MySQL and PostgreSQL.

Installation
------------
.. The easiest way to install the package is via ``easy_install`` or ``pip``::
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

To increase the security change the shell for the dns user to git-shell::

  sudo chsh -s /usr/bin/git-shell dns

Format
------
The files used by ``pdns-sync`` are normal hosts files with additional rows for non A or AAAA records.

**Normal A or AAAA**
  Like a hosts file with either an ipv4 or an ipv6 address and also works with multiple hostnames on each row
  When an address has multiple hostnames the first will be used as the reverse address unless one is tagged
  with an ~ sign, then it will be used as the reverse instead.

example::
  
  192.0.2.4 foo.example.com
  192.0.2.5 bar.example.com baz.example.com
  192.0.2.5 ~ptr.example.com
  2001:db8::44 ipv6.example.com

**Multiple addresses for a hostname**
  A hostname can have multiple addresses for used in DNS Round Robin

example::

  192.0.2.80 www.example.com
  192.0.2.81 www.example.com

**Defining a domain**
  Start a line with a D to define a domain followed by the name, primary nameserver and responsible email address. The
  field can be set by adding four additional arguments, refresh, retry, expire and minimum. The default values are
  86400 7200 604800 300. The serial is automagicaly generated using the date and a counter.
  Following the domain definition are a line begining with an N and a list of nameservers for the domain and an optional line begining with
  M and a list with mail exchangers, the prio is default 10 but can be set on the line.
  Don't forget to define your reverse zones and expand your ipv6 reverse zones.

example::

  D example.com ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com
  M mx1.example.com 20 mx2.example.com

  D example.org ns1.example.com hostmaster@example.com 172800 7200 604800 600
  N ns1.example.com ns2.example.com
  M mx1.example.com
  
  D 2.0.192.in-addr.arpa ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com
  
  D 8.b.d.0.1.0.0.2.ip6.arpa ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com

**Aliases**
  To create a CNAME add a line begining with C, the alias and the target.

example::

  C mail.example.com mx1.example.com

**Change the TTL**
  The TTL for the records defaults to 3600 and can be change with a line begining with T and a number for the new TTL, this TTL will be used
  for the rest of the file or until a new value is set.

example::

  T 600
  192.0.2.80 www.example.com
  T 3600
  192.0.2.25 mail.example.com

**Service records**
  To creat an SRV records add a line begining with S, the service name, prio, weight, port and target.

example::

  S _sip._tcp.example.com 1 2 5060 sip.example.com

Example
-------
This is an example of a domain and a reverse domain in a file::

  D example.com ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com
  M mx1.example.com 20 mx2.example.com

  192.0.2.80 www.example.com

  192.0.2.53 ns1.example.com
  192.0.2.54 ns2.example.com

  192.0.2.25 mx1.example.com
  192.0.2.26 mx2.example.com

  D 2. 0.192.in-addr.arpa ns1.example.com hostmaster@example.com
  N ns1.example.com ns2.example.com
