# -*- coding: utf-8 -*-
from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from models import TestModel


class TestWithoutAdminInstalled(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.obj_1 = TestModel.objects.create(text_field="The quick brown fox")

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
    ]
)
class TestWithAdminInstalled(TestCase):
    urls = 'django_grepdb.tests.admin_urls'

    @classmethod
    def setUpTestData(cls):
        cls.obj_1 = TestModel.objects.create(text_field="The quick brown fox")

    def test_default_link_generation_output(self):
        """Default is to generate admin links, and to use localhost:8000 as the hostname"""
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object " \
                   "(pk=1)\x1b[0m\n\x1b[32mhttp://localhost:8000/admin/tests/testmodel/1/\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_option_without_argyment_turns_off_link_generation(self):
        out = StringIO()
        call_command('grepdb', 'quick', 'tests.TestModel.text_field', '-s', '-l', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)
