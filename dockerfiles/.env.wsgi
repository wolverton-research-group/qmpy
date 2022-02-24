#################################################################################
# This is an example file with all the required environment variables to 
# create the ".env" file. For security reasons, ".env" is not included in 
# version control (see .gitignore) and thus, not pushed to GitHub.
#
# Steps to follow:
#
#     Step 1: Copy this file (".env.example") to a new file named ".env" in 
#             this directory.
#
#     Step 2: Close this file (".env.example") and open the new file (".env")
#             and proceed to the Step 3 from ".env".
#
#     Step 3: Modify the environment values below to match your system and 
#             configuration.
#
#     Step 4: Save this ".env" file.
#
################################################################################

# Database-related variables.
#
#     Make sure to set them to match your MySQL DB configuration.
#     See their usage in qmpy/db/settings.py file. 
#     In short, they are used to define Django's DATABASES dictionary
OQMD_DB_name=qmdb
OQMD_DB_user=root
OQMD_DB_pswd=secret
OQMD_DB_host=mysql
OQMD_DB_port=3306


# Web-hosting related variables
#
#     The "OQMD_WEB_hosts" variable holds comma-separated hostnames that are
#     to be included in Django's ALLOWED_HOSTS tag. 
#     See qmpy/qmpy/db/settings.py file.
#
#     Set OQMD_WEB_debug=True only when the server is not in production.
#     OQMD_WEB_debug=False prints too many details during error enounters -> high security risk
OQMD_WEB_hosts=0.0.0.0,127.0.0.1
OQMD_WEB_debug=False


# REST API-related variables
#     These values are required to make queries from the /api/search page
#     Regular REST API from /optimade/ and /oqmdapi/ pages would work fine even without these
#     These values should match the host:port values provided in server hosting command
#     Eg: 
#         A server hosted using "python manage.py runserver example.com:8888" should
#         have OQMD_REST_host='example.com' and OQMD_REST_port='8888'
OQMD_REST_host=0.0.0.0
OQMD_REST_port=8000


# Static file storage-related variables
#     These values are used in qmpy/db/settings.py file.
#     The correct values for your implementation depends on where the static files are stored
#     for your server.
#
#     "OQMD_STATIC_root" and "OQMD_STATIC_url" are assigned to Django's STATIC_ROOT 
#     and STATIC_URL respectively.
#     https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#settings
#
#     OQMD_USE_CDN refers to whether CDN-hosted JS files are to be loaded instead of
#     local static JS files
#     Used in qmpy/templatetags/custom_filters.py
OQMD_STATIC_root=/static/
OQMD_STATIC_url=/static/
OQMD_USE_CDN=False

# Secret Key for signing cookies, hash generation and some authentication in Django.
#
# It's more significant in Django servers where the user authentication 
# is required, unlike oqmd.org
# 
#    More details: 
#        https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key
#
#    You can simply generate a 50 character key anytime.
#        https://github.com/django/django/blob/stable/2.2.x/django/core/management/utils.py#L76
#    The key given is randomly generated, but not used in any of our servers:
OQMD_DJANGO_secretkey='48o2)h#gwow!iyg&__4d%zkv8v&h=n!sv)0rvj$*1yj8tw0riu'

# URL of the PHP server to do CORS operations for JSMOL.
# More details: 
#        https://wiki.jmol.org/index.php/Jmol_JavaScript_Object/Info
#
# According to the official docs, if you can't host a php server,
# it is fine to set the value as:
#        https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php

JSMOL_serverURL='/static/js/jsmol/php/jsmol.php'
