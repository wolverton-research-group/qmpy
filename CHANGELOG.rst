qmpy changelog
==========================

1.x.0 - 09/xx/2019
------------------

- Django upgrade to 1.8.18 from 1.6.xx
    - Model instance creation is done via Class Managers because model instace auto-save was removed to optimize memory
    - The command - makemigrations is used to auto-detect model changes. It i used for building in travis
    - [Django Querysets] (https://docs.djangoproject.com/en/2.2/ref/models/querysets/#q-objects) are implemented for data filtering
- RESTful framework added
    - Serialized DFT data availability
    - Lark Parser to handle queries
    - Pagination
- Change in UI of the landing page
- Optimized the phase diagram and stability plot generation for compounds
- More Django tests added



1.2.0 - 09/28/2018
------------------


1.1.0 - 05/02/2018
------------------

