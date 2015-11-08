=============
django_grepdb
=============

django_grepdb is a simple command-line app to provide basic grep-like searching of
Django model fields using the ORM. Written to facilitate searching for a tag,
filter, named url etc in templates in the database, but can also be used to quickly
find model instances from the command line.


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

2. Run::

    $ python manage.py grepdb <pattern> <app_label.Model.field_name>


Usage
-----

Find instances of ``{% custom_template_tag.*%}`` in all text fields on the
model ``EmailAction`` from app ``sprinkle``, show lines containing matches,
and generate admin links (if ``django.contrib.admin`` is installed)::

    $ python manage.py grepdb "{% custom_template_tag.*%}" sprinkle.EmailAction
    <class 'sprinkle.models.EmailAction'> text_field

    User registered (pk=13)
    localhost:8000/admin/sprinkle/emailaction/13/
    <p>Hi {% custom_template_tag user.get_full_name %},</p>

    Password reset request (pk=24)
    localhost:8000/admin/sprinkle/emailaction/24/
    <p>Hi, {% custom_template_tag user.get_full_name %}</p>


Options
-------

Options are listed using ``$ python manage.py grepdb --help`` but here are some of the things
you can do with ``django_grepdb``.

Search multiple models::

    $ python manage.py grepdb <pattern> sprinkle.EmailAction cms.MarkdownNode

Specify fields instead of finding all text fields::

    $ python manage.py grepdb <pattern> sprinkle.EmailAction.body sprinkle.EmailAction.subject

Find all instances of CharField instead of TextField::

    $ python manage.py grepdb <pattern> sprinkle.EmailAction -c

Show the whole field of a match rather than just the line::

    $ python manage.py grepdb <pattern> sprinkle.EmailAction -sa

Change the hostname of the admin links::

    $ python manage.py grepdb <pattern> sprinkle.EmailAction -l https://dev.example.com

Specify hostname key-value pairs in settings::

    DJANGO_GREPDB_SITES = {
        'default': 'https://staging.example.com'
        'dev': 'https://dev.example.com',
    }

    $ python manage.py grepdb <pattern> sprinkle.EmailAction -l dev

Specify preset configurations in settings::

    DJANGO_GREPDB_PRESETS = {
        'users': dict(identifiers=['auth.user', 'projects.userprofile'],
                      field_type=['CharField', 'TextField'],
                      ignore_case=True),
        'templates': dict(identifiers=['sprinkle.EmailAction', 'cms.HTMLNode', 'cms.TextNode', 'cms.MarkdownNode'])

    $ python manage.py grepdb <pattern> -p templates
