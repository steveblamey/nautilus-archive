Nautilus Archive Extension
===========================

Installation
------------

Download and uncompress tarball. For installation use a setup.py script::

       $ sudo ./setup.py install

Restart Nautilus::

    $ nautilus -q


Dependencies
------------

Dependencies that must be met:

python-nautilus
tracker (installs libtracker-sparql)
gir1.2-tracker (dependecy of libtracker-sparql-dev)

- ``python-nautilus``::

      $ sudo apt-get install python-nautilus

- ``Tracker``::

      $ sudo apt-get install tracker
      
- GObject introspection for tracker (e.g. from gir1.2-tracker)::

      $ sudo apt-get install libtracker-sparql-X.XX-dev

Meta
----

- Author: Steve Blamey <steve@steveblamey.co.uk>
- License: GNU GPL v3
- Version: 0.1

.. _nautilus-archive: http://www.steveblamey.co.uk/nautilus-archive

