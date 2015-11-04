# -*- coding: utf-8 -*-
from django.core.management import CommandError
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from ..management import call_command
from models import TestModel, TestModelTwo


class TestWithoutPresets(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="The quick brown fox", text_field_two="jumped over the lazy dog")

    def test_presets_option_not_used_by_default(self):
        out = StringIO()
        call_command('grepdb', 'brown', stdout=out)
        expected = ""
        self.assertEqual(out.getvalue(), expected)

    def test_preset_option_fails(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'brown', '-p', 'model_one')
        msg = u'Preset specified but DJANGO_GREPDB_PRESETS is not configured in settings'
        self.assertEqual(cm.exception.message, msg)


@override_settings(
    DJANGO_GREPDB_PRESETS=[
        {'model_one': {'identifiers': ['tests.TestModel']}}
    ]
)
class TestWithMisconfiguredSetting(TestCase):
    def test_preset_option_fails(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'brown', '-p', 'model_one')
        msg = u'DJANGO_GREPDB_PRESETS is not a dict-like object'
        self.assertEqual(cm.exception.message, msg)


@override_settings(
    DJANGO_GREPDB_PRESETS={
        'model_one': {'identifiers': ['tests.TestModel']},
        'model_one_case_insensitive': {'identifiers': ['tests.TestModel'], 'ignore_case': True},
        'model_two': {'identifiers': ['tests.TestModelTwo']},
        'model_two_char_fields': {'identifiers': ['tests.TestModelTwo'], 'field_type': ['CharField']},
    }
)
class TestPresets(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="The quick brown fox", text_field_two="jumped over the lazy dog")
        TestModelTwo.objects.create(text_field="The dog was lazy")
        TestModelTwo.objects.create(char_field="The fox was quick and brown")

    def test_identifier_from_preset(self):
        out = StringIO()
        call_command('grepdb', 'brown', '-s', '-p', 'model_one', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> " \
                   "text_field\x1b[0m\n\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)
