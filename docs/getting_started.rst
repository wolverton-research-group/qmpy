============
Installation
============

---------
From repo
---------

Install qmpy with pip or easy install::

    >>> pip install qmpy

or:: 

    >>> easy_install -U qmpy

.. note::
    Using pip or easy_install to install scipy or numpy can be unreliable. It
    is better to install from a proper repository for your linux distribution.
    However, if that version of SciPy is earlier than 0.12.0 you will need to
    obtain another installation. If necessary, you can obtain the needed
    libraries with::

        $ sudo apt-get install libatlas-dev libatlas-base-dev 
        $ sudo apt-get install liblapack-dev gfortran

----------------
From GitHub repo
----------------

Obtain the source with::

    $ git clone https://github.com/wolverton-research-group/qmpy.git
    $ cd qmpy
    $ python setup.py install

Be aware that f you want to install qmpy from source, you will be responsible 
for ensuring that you have all of the following required packages installed. 

-----------------
Required Packages
-----------------

* Django (https://www.djangoproject.com/)
* Numpy (http://www.numpy.org/)
* Scipy (http://www.scipy.org/)
* PyYAML (http://pyyaml.org/)
* python-MySQL (https://pypi.python.org/pypi/MySQL-python)
* python-memcached
* django-extensions
* PuLP (https://pythonhosted.org/PuLP/) (required for grand canonical linear
  programming and high-dimensional phase diagram slices)

--------------------
Recommended Packages
--------------------

* matplotlib (http://matplotlib.org/) (required for creating figures)
* networx (http://networkx.github.io/) (required for creating spin lattices,
  and some high-dimensional phase diagram analysis)

.. warning::
 In order for pulp to work, you must have a working linear programming
 package installed. PuLP provides a simple library for this, but it is 
 up to you to make sure it is working.

=======================
Setting up the database
=======================

The database can be downloaded from
http://oqmd.org/static/downloads/qmdb.sql.gz

Once you have the database file, you need to unzip it and load it into a
database MySQL. On a typical linux installation this process will look like::

    $ wget http://oqmd.org/static/downloads/qmdb.sql.gz
    $ gunzip qmdb.sql.gz
    $ mysql < qmdb.sql

.. note::
    Assuming your install is on linux, and assuming you haven't used MySQL at
    all, you will need to enter a mysql session as root ("mysql -u root -p"),
    create a user within MySQL ("CREATE USER 'newuser'@'localhost';"), grant
    that user permissions ("GRANT ALL PRIVILEGES ON * . * TO
    'newuser'@'localhost'; FLUSH PRIVILEGES;").

.. note::
    The name of the deployed database has changed since previous releases
    (qmdb_prod). If your install isn't working, make sure that the database
    name agrees with what is found in qmpy/db/settings.py.

Once this is done, you need to edit qmpy/db/settings.py. Set the DATABASES
variable such that 'USER' is the user with permissions to access the newly
installed database.

.. note:: For windows/cygwin users:
    To use MySQL in Cygwin, you need to install MySQL via the Oracle website for
    windows. Only after MySQL is install in windows can use mysql in Cygwin. You
    can find the download for MySQL here:
    http://dev.mysql.com/downloads/windows/installer.

    It is free, but you have to register with Oracle to access. Next, you need to
    move the database file over to the Windows MySQL data drive. It may vary by
    version, but you might find it at C:\ProgramData\MySQL\MySQL Server 5.6\data.
    Copy the downloaded database directory into this folder. Finally, in the
    db/settings.py file, the HOST has to be set to ‘127.0.0.1’, and set the PORT
    and PASSWORD variables as well according to your MySQL installation.

To verify that the database is properly installed and has appropriate
permissions, run::

    mysql> select count(*) from entries;
    +----------+
    | count(*) |
    +----------+
    |   173653 |
    +----------+

The number may not match what is shown above, but as long as you don't recieve
any errors, your database should be working properly.

