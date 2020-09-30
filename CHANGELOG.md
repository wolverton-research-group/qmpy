qmpy changelog
==========================

1.4.0 - 09/29/2020
------------------

- Python upgrade to 3.7.xx from 2.7.xx
    - New version of qmpy is tested only against Python 3 
    - Syntax changes needed to compile in py3
    - MySQL-python packages is no longer supported. Instead the mysqlclient package dependency is added
    - The \_\_cmp\_\_ function is deprecated. \_\_lt\_\_ is used instead to compare Model objects
- Django upgrade to 2.2.xx from 1.8.18
    - ForeignKey.on\_delete functions are added as it is now mandated
    - Removed the deprecated SubfieldBase metaclass and added the alternative from\_db\_value function to load data from DB
    - URL view specifications are changed from strings to model views
    - Parent import directory changes for multple Django classes (eg: context\_processors)
    - Several changes in format of settings file params
    - Defined hash function for Phase objects
    - Changed the Model field definition to have blank=True instead of null=True
- Conflict between qmpy.io and python3's default io module are resolved. Now we import subclasses or function individually specified insidethese io modules
- Visualization page is improved
    - More customization tools and upgraded Jsmol version
- Blackened
    - Reformatted the scripts using Black
- Added Structured Data scripts to adhere to the definitions in schema.org


1.3.0 - 11/05/2019
------------------

- Django upgrade to 1.8.18 from 1.6.xx
    - Model instance creation is done via Class Managers because model instace auto-save was removed to optimize memory
    - The command - makemigrations is used to auto-detect model changes. It i used for building in travis
    - [Django Querysets](https://docs.djangoproject.com/en/2.2/ref/models/querysets/#q-objects) are implemented for data filtering
- RESTful framework added
    - Serialized DFT data availability with both default [OQMD](http://oqmd.org/static/docs/models.html) and [OPTiMaDe](http://www.optimade.org/) specified keyword-sets. 
    - [Lark Parser](https://lark-parser.readthedocs.io/en/latest/) to convert raw queries to logical Django Queries
    - Pagination is implemented while retreiving RESTful query results
- Spglib upgraded to >1.9
    - Removed dependency on pyspglib since it is no longer maintained by its developer(s)
    - Significant changes to the internal implementation of Structure model, even though it's not expected to be affect the end-user
- More unit tests
    - duplicate entry detection, structure transformations
- Change in UI of the landing page
    - Removed the on-the-fly calculations of # of entries while loading the oqmd.org main page
    - Removed the twitter based phase lookup instructions since it's no longer operational
- Optimized the phase diagram and stability plot generation for compounds
    - Stability plot is now generated from the PhaseData that was already collected for generating phase diagram, instead of performing a second database lookup


1.2.0 - 09/28/2018
------------------


1.1.0 - 05/02/2018
------------------

