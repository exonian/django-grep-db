import argparse
import re

import colorama
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from termcolor import colored


def show_values_style(arg):
    special_choices = ['a', 'l']
    if arg in special_choices:
        return arg
    try:
        return int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Show values style must be one of '{values}' or an integer".format(
            values=', '.join(special_choices)))


class Command(BaseCommand):
    help = 'Provides a grep-like command line interface for searching objects in the database'

    def add_arguments(self, parser):
        parser.add_argument('pattern', type=str, help='Pattern to search for')
        parser.add_argument('identifier', nargs='+', type=str, help='Identifier of a model or field')
        parser.add_argument('--show-values', '-s', nargs='?', type=show_values_style, default='l',
                            help='Turn off showing matching values (default is any line containing a match), ' +
                            'or provide the mode "a" to show the entire field ' +
                            'or an integer to show that many characters either side of a match.')
        parser.add_argument('--ignore-case', '-i', action='store_true', help='Match case-insensitively')
        parser.add_argument('--find-text-fields', '-t', dest='field_types', action='append_const', const='TextField',
                            help='Search all TextField fields on a model if no field is specified')
        parser.add_argument('--find-char-fields', '-c', dest='field_types', action='append_const', const='CharField',
                            help='Search all CharField fields on a model if no field is specified')
        parser.add_argument('--find-fields', '-f', dest='field_types', action='append', type=str,
                            help='Search all fields of this type on a model if no field is specified')
        parser.add_argument('--admin-links', '-l', nargs='*', default=['http://localhost:8000'],
                            help='Generate admin links. Defaults to true, using http://localhost:8000/ as hostname.' +
                            'Can be passed one or more hostnames to use instead. If DJANGO_GREPDB_SITES is a dict ' +
                            'defined in settings, keys from it can also be passed to use their values as hostnames.' +
                            'Links can be disabled by using this argument without any values.')

    def handle(self, **options):
        colorama.init()
        self.pattern = options['pattern']
        self.ignore_case = options['ignore_case']
        self.show_values = options.get('show_values', False)
        self.field_types = options['field_types'] or ['TextField']
        self.admin_hostnames = self.get_admin_hostnames(options)

        identifiers = options['identifier']
        queries = self.get_queries(identifiers)
        for query in queries:
            results = self.search(query)
            if results.exists():
                self.stdout.write(colored(u'\n{model} {field}'.format(model=query['manager'].model, field=query['field_name']),
                                          'cyan', attrs=['bold']))
                for result in results:
                    self.stdout.write(colored(u'{result} (pk={result.pk})'.format(result=result), 'green', attrs=['bold']))
                    if self.admin_hostnames:
                        self.stdout.write(self.get_admin_links(result))
                    if self.show_values is not None:  # can't be a truthiness check, as zero is different from no show
                        self.stdout.write(self.get_value(result, query))

    def get_admin_hostnames(self, options):
        from_options = options.get('admin_links', False)
        if not from_options:
            return
        from django.contrib.admin import site as admin_site
        self.admin_site = admin_site
        hostnames = []
        for reference in from_options:
            hostnames.append(self.get_admin_hostname(reference))
        return hostnames

    def get_admin_hostname(self, reference):
        """Treats the reference as a hostname if it contains a dot or the string 'localhost'.
        If it contains neither, looks up the reference in settings.DJANGO_GREPDB_SITES
        """
        if '.' in reference or 'localhost' in reference:
            return reference
        try:
            sites = getattr(settings, 'DJANGO_GREPDB_SITES')
        except AttributeError:
            msg = u'Reference {} is not recognised as a hostname and DJANGO_GREPDB_SITES is not configured in settings'
            raise CommandError(msg.format(reference))
        try:
            hostname = sites[reference]
        except KeyError:
            msg = u'Reference {} is not recognised as a hostname and was not found in DJANGO_GREPDB_SITES'
            raise CommandError(msg.format(reference))
        return hostname


    def get_queries(self, identifiers):
        queries = []
        for identifier in identifiers:
            queries.extend(self.get_queries_for_identifier(identifier))
        return queries

    def get_queries_for_identifier(self, identifier):
        model, field_names = self.parse_identifier(identifier)
        queries = []
        for field_name in field_names:
            params = self.get_queryset_params(field_name)
            queries.append(dict(manager=model._default_manager, params=params, field_name=field_name))
        return queries

    def search(self, query):
        return query['manager'].filter(**query['params'])

    def parse_identifier(self, identifier):
        parts = identifier.split('.')
        app_label, model_name = parts[:2]
        field_names = parts[2:]
        model = apps.get_model(app_label, model_name)
        if not field_names:
            field_names = self.get_field_names_for_model(model)
        return (model, field_names)

    def get_field_names_for_model(self, model):
        return [field.name for field in model._meta.fields if field.get_internal_type() in self.field_types]

    def get_queryset_params(self, field_name):
        lookup_type = 'regex'
        if self.ignore_case:
            lookup_type = 'i' + lookup_type
        return {'{field_name}__{lookup_type}'.format(field_name=field_name, lookup_type=lookup_type): self.pattern}

    def get_value(self, result, query):
        text = getattr(result, query['field_name'])
        show_values = self.show_values
        if show_values == 'a':
            return self.get_value_all(text)
        elif show_values == 'l':
            return self.get_value_line(text)
        else:
            return self.get_value_surrounded(text)

    def get_value_all(self, text):
        regex_args = [self.pattern, text, re.DOTALL]
        if self.ignore_case:
            regex_args[2] += re.IGNORECASE
        matches = [m.span() for m in re.finditer(*regex_args)]
        value = u''
        end_of_previous = 0
        for start, end in matches:
            value = value + text[end_of_previous:start] + colored(text[start:end], 'grey', 'on_yellow')
            end_of_previous = end
        value = value + text[end_of_previous:] + '\n\n'
        return value

    def get_value_line(self, text):
        value = u''
        for line in text.splitlines():
            regex_args = [self.pattern, line]
            if self.ignore_case:
                regex_args.append(re.IGNORECASE)
            matches = [m.span() for m in re.finditer(*regex_args)]
            if matches:
                end_of_previous = 0
                for start, end in matches:
                    value = value + line[end_of_previous:start] + colored(line[start:end], 'grey', 'on_yellow')
                    end_of_previous = end
                value = value + line[end_of_previous:] + '\n\n'
        return value

    def get_value_surrounded(self, text):
        regex_args = [self.pattern, text]
        if self.ignore_case:
            regex_args.append(re.IGNORECASE)
        matches = re.findall(*regex_args)
        chars = self.show_values
        matches = [m.span() for m in re.finditer(*regex_args)]
        value = u''
        end_of_previous = 0
        for start, end in matches:
            if end_of_previous and end_of_previous > start:
                value = value[:start - end_of_previous]
            elif end_of_previous and end_of_previous > start - chars:
                value += text[end_of_previous:start]
            else:
                value += '\n' + text[start - chars:start]
            value += colored(text[start:end], 'grey', 'on_yellow') + text[end:end + chars]
            end_of_previous = end + chars
        value = value.strip() + '\n\n'
        return value

    def get_admin_links(self, result):
        content_type = ContentType.objects.get_for_model(result)
        admin_url_pattern = 'admin:{app}_{model}_change'.format(app=content_type.app_label, model=content_type.model)
        relative_url = reverse(admin_url_pattern, args=[result.pk])
        return '\n'.join([colored(hostname + relative_url, 'green') for hostname in self.admin_hostnames])
