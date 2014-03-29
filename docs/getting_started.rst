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

-----------
From source
-----------

Download the source at http://pypi.python.org/pypi/qmpy. However, if you want 
to install qmpy from source, you will be responsible for ensuring that you have 
all of the following required packages installed. 

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

--------------------
Recommended Packages
--------------------

* matplotlib (http://matplotlib.org/) (required for creating figures)
* pyflot (https://github.com/andrefsp/pyflot) (required for rendering figures
  for html)
* networx (http://networkx.github.io/) (required for creating spin lattices,
  and some high-dimensional phase diagram analysis)
* PuLP (https://pythonhosted.org/PuLP/) (required for grand canonical linear
  programming and high-dimensional phase diagram slices)

.. warning::
 In order for pulp to work, you must have a working linear programming
 package installed. PuLP provides a simple library for this, but it is 
 up to you to make sure it is working.

=======================
Setting up the database
=======================

The database can be downloaded from
http://oqmd.org/static/downloads/database.tgz or within qmpy you can run::

    >>> sync_database()

and follow the command line prompts to download the database. 

Once you have the database file, you must place the entire database directory 
into into your mysql data folder, (most likely /var/lib/mysql/ on a 
linux system). Make sure that the database directory, and all files within 
it are owned by the user 'mysql'. On a typical linux installation this process
might go like::

    $ wget http://oqmd.org/static/downloads/database.tgz
    $ tar -xvf database.tgz
    $ mv qmdb /var/lib/mysql/qmdb
    $ sudo chown -r mysql: /var/lib/mysql/qmdb

.. note:: 
    The name of the deployed database has changed since previous releases
    (qmdb_prod). Please make sure you keep the database name the same as the
    folder name it untars as.

Finally, once this is done you need to 
give any users that will be accessing the database permissions. 
Do this from the mysql command line::

    mysql> GRANT ALL PRIVILEGES ON *.* to '[username]'@'localhost'

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

