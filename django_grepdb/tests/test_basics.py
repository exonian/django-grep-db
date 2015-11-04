# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from models import TestModel


class TestBasicsEndToEnd(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="The quick brown fox",
                                             text_field_two="jumped over the lazy brown dog")
        TestModel.objects.create(text_field="The fox and the cat were not lazy")
        TestModel.objects.create(text_field="The CAT was not lazy")

    def test_minimal_output(self):
        out = StringIO()
        call_command('grepdb', 'brown', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_minimal_output_two_matches(self):
        out = StringIO()
        call_command('grepdb', 'fox', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n\x1b" \
                   "[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_minimal_output_two_fields(self):
        out = StringIO()
        call_command('grepdb', 'brown', 'tests.TestModel.text_field', 'tests.TestModel.text_field_two',
                     '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n\x1b[1m\x1b" \
                   "[32mTestModel object (pk=1)\x1b[0m\n\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models." \
                   "TestModel'> text_field_two\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_minimal_output_case_sensitive_by_default(self):
        out = StringIO()
        call_command('grepdb', 'cat', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_minimal_output_case_insensitive(self):
        out = StringIO()
        call_command('grepdb', 'cat', 'tests.TestModel.text_field', '-s', '-i', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n\x1b[1m\x1b" \
                   "[32mTestModel object (pk=2)\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=3)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_minimal_output_regex_search(self):
        out = StringIO()
        call_command('grepdb', 'The.* fox', 'tests.TestModel.text_field', '-s', '-i', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n\x1b[1m\x1b" \
                   "[32mTestModel object (pk=1)\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_minimal_output_regex_search_two(self):
        out = StringIO()
        call_command('grepdb', 'The.+ fox', 'tests.TestModel.text_field', '-s', '-i', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n\x1b[1m\x1b" \
                   "[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)
