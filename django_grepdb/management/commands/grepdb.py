import argparse
import re

import colorama
from django.apps import apps
from django.core.management.base import BaseCommand
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
        parser.add_argument('identifier', nargs='+', type=str, help='Identifier of an app, model or field')
        parser.add_argument('--show-values', '-s', nargs='?', type=show_values_style, const='l',
                            help='Show field value in addition to object representation and pk. ' +
                                 'Takes optional value of number of chars to show each side of match (default is 25)')
        parser.add_argument('--ignore-case', '-i', action='store_true', help='Match case-insensitively')

    def handle(self, **options):
        colorama.init()
        self.pattern = options['pattern']
        self.ignore_case = options['ignore_case']
        self.show_values = options.get('show_values', False)
        identifiers = options['identifier']
        queries = self.get_queries(identifiers)
        for query in queries:
            results = self.search(query)
            if results.exists():
                self.stdout.write(colored(u'\n{}'.format(query['manager'].model), 'cyan', attrs=['bold']))
                for result in results:
                    self.stdout.write(colored(u'{result} (pk={result.pk})'.format(result=result), 'green', attrs=['bold']))
                    if self.show_values is not None:  # can't be a truthiness check, as zero is different from no show
                        self.stdout.write(self.get_value(result, query))

    def get_queries(self, identifiers):
        return [self.get_query(identifier) for identifier in identifiers]

    def get_query(self, identifier):
        model, field_name = self.parse_identifier(identifier)
        params = self.get_queryset_params(field_name)
        return dict(manager=model._default_manager, params=params, field_name=field_name)

    def search(self, query):
        return query['manager'].filter(**query['params'])

    def parse_identifier(self, identifier):
        app_label, model_name, field_name = identifier.split('.')
        return (apps.get_model(app_label, model_name), field_name)

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
            regex_args.append(re.IGNORECASE)
        matches = [m.span() for m in re.finditer(*regex_args)]
        value = u''
        end_of_previous = 0
        for start, end in matches:
            value = value + text[end_of_previous:start] + colored(text[start:end], 'grey', 'on_yellow')
            end_of_previous = end
        value = value + text[end_of_previous:] + '\n\n'
        return value

    def get_value_line(self, text):
        surrounded_pattern = r'(\\n.*)({pattern})(\\n.*)'.format(pattern=self.pattern)
        regex_args = [surrounded_pattern, text]
        if self.ignore_case:
            regex_args.append(re.IGNORECASE)
        matches = re.findall(*regex_args)
        for pre, match, post in matches:
             return pre + colored(match, 'grey', 'on_yellow') + post + '\n\n'

    def get_value_surrounded(self, text):
        chars = self.show_values
        surrounded_pattern = r'(.{{0,{chars}}})({pattern})(.{{0,{chars}}})'.format(
            chars=self.show_values, pattern=self.pattern
        )
        regex_args = [surrounded_pattern, text, re.DOTALL]
        if self.ignore_case:
            regex_args.append(re.IGNORECASE)
        matches = re.findall(*regex_args)
        for pre, match, post in matches:
             return pre + colored(match, 'grey', 'on_yellow') + post + '\n\n'
