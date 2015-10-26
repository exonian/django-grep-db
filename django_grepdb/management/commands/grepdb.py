import re

import colorama
from django.apps import apps
from django.core.management.base import BaseCommand
from termcolor import colored


class Command(BaseCommand):
    help = 'Provides a grep-like command line interface for searching objects in the database'

    def add_arguments(self, parser):
        parser.add_argument('pattern', type=str, help='Pattern to search for')
        parser.add_argument('identifier', nargs='+', type=str, help='Identifier of an app, model or field')
        parser.add_argument('--show', '-s', nargs='?', type=int, const=0,
                            help='Amount of text to show around result; overrides default of not showing results')
        parser.add_argument('--ignore-case', '-i', action='store_true', help='Match case-insensitively')

    def handle(self, **options):
        colorama.init()
        self.pattern = options['pattern']
        self.ignore_case = options['ignore_case']
        identifiers = options['identifier']
        queries = self.get_queries(identifiers)
        for query in queries:
            results = self.search(query)
            if results.exists():
                self.stdout.write(colored(u'\n{}'.format(query['manager'].model), 'cyan', attrs=['bold']))
                for result in results:
                    self.stdout.write(colored(u'{result} (pk={result.pk})'.format(result=result), 'green', attrs=['bold']))
                    show = options.get('show', False)
                    if show is not None:  # can't be a truthiness check, as zero is different from no show
                        text = getattr(result, query['field_name'])
                        surrounded_pattern = '.{{0,{show}}}{pattern}.{{0,{show}}}'.format(show=show, pattern=self.pattern)
                        regex_args = [surrounded_pattern, text]
                        if self.ignore_case:
                            regex_args.append(re.IGNORECASE)
                        matches = re.findall(*regex_args)
                        for match in matches:
                            self.stdout.write(match)
                        self.stdout.write('')

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
