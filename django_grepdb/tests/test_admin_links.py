# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from models import TestModel


class TestWithoutAdminInstalled(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="The quick brown fox")

    def test_admin_option_not_used_by_default(self):
        out = StringIO()
        call_command('grepdb', 'brown', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_admin_option_fails(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'brown', 'tests.TestModel.text_field', '-s', '-l')
        self.assertEqual(cm.exception.message, u'Error: unrecognized arguments: -l')


@override_settings(
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django_grepdb',
        'django_grepdb.tests',
    ],
    ROOT_URLCONF='django_grepdb.tests.admin_urls'
)
class TestWithAdminInstalled(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="The quick brown fox")

    def test_default_link_generation_output_with_defined_default(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mhttps://local.example.com/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    @override_settings(
        DJANGO_GREPDB_SITES = {
            'staging': 'https://staging.example.com',
            'production': 'https://example.com',
        }
    )
    def test_default_link_generation_output_without_defined_default(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mlocalhost:8000/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_without_argument_turns_off_link_generation(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_with_http_hostname(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'http://fox.example.com', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mhttp://fox.example.com/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_with_https_hostname(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'https://fox.example.com', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mhttps://fox.example.com/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_with_schemeless_hostname(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'fox.example.com')
        msg = u'Reference fox.example.com is not recognised as a hostname and was not found in DJANGO_GREPDB_SITES'
        self.assertEqual(cm.exception.message, msg)

    def test_option_with_localhost(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'localhost:4000', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mlocalhost:4000/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_with_sites_key(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'production', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mhttps://example.com/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_with_mixed_arguments(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'staging', 'production', 'default',
                     'https://dev.example.com', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n" \
                   "\x1b[32mhttps://staging.example.com/admin/tests/testmodel/1/\x1b[0m\n" \
                   "\x1b[32mhttps://example.com/admin/tests/testmodel/1/\x1b[0m\n" \
                   "\x1b[32mhttps://local.example.com/admin/tests/testmodel/1/\x1b[0m\n" \
                   "\x1b[32mhttps://dev.example.com/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    @override_settings()
    def test_option_without_sites_setting(self):
        del settings.DJANGO_GREPDB_SITES
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', 'fox.example.com')
        msg = u'Reference fox.example.com is not recognised as a hostname and DJANGO_GREPDB_SITES is not ' \
              'configured in settings'
        self.assertEqual(cm.exception.message, msg)
