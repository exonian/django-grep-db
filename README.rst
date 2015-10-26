======
grepdb
======

grepdb is a simple command-line app to provide basic grep-like searching of
Django model fields using the ORM.

Quick start
-----------

1. Add "django_grepdb" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'django_grepdb',
    )

   or, if you have a separate settings file for development in which you
   extend your global settings, like this::

    INSTALLED_APPS = INSTALLED_APPS + ('django_grepdb',) 

2. Run:
    python manage.py grepdb <pattern> <app_label.Model.field_name>
