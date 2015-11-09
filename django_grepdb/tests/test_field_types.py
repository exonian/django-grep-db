# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from models import TestModelTwo


class TestPresets(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModelTwo.objects.create(text_field="The quick brown fox")
        TestModelTwo.objects.create(char_field="The quick brown fox")
        TestModelTwo.objects.create(url="http://example.com/fox/")

    def test_field_type_defaults_to_text_fields(self):
        out = StringIO()
        call_command('grepdb', 'fox', 'tests.TestModelTwo', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_special_charfield_detection_option(self):
        """-c option should detect the CharField and the URLField (subclass of CharField)"""
        out = StringIO()
        call_command('grepdb', 'fox', 'tests.TestModelTwo', '-c', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> char_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=2)\x1b[0m\n" \
                   "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> url\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=3)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_named_field_type_detection_option(self):
        out = StringIO()
        call_command('grepdb', 'fox', 'tests.TestModelTwo', '-f', 'CharField', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> char_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=2)\x1b[0m\n" \
                   "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> url\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=3)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_multiple_field_type_detection_options(self):
        out = StringIO()
        call_command('grepdb', 'fox', 'tests.TestModelTwo', '-c', '-t', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=1)\x1b[0m\n" \
                   "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> char_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=2)\x1b[0m\n" \
                   "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> url\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=3)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)
