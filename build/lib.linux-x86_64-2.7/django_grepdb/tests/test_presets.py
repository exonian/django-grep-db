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
        'model_two_multiple_fields': {'identifiers': ['tests.TestModelTwo'], 'field_type': ['CharField', 'TextField']},
        'both_models': {'identifiers': ['tests.TestModelTwo', 'tests.TestModel']},
        'preset_is_a_list': ['tests.TestModel', 'ignore_case']
    }
)
class TestPresets(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="The quick brown fox", text_field_two="jumped over the lazy dog")
        TestModel.objects.create(text_field="THE QUICK BROWN FOX")
        TestModelTwo.objects.create(text_field="The dog was lazy")
        TestModelTwo.objects.create(char_field="The fox was quick and brown")

    def test_error_raised_when_using_default_call_command(self):
        from django.core.management import call_command
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'brown', '-p', 'model_one')
        msg = "--preset mode is not compatible with django.core.management.call_command: " \
              "you need to use django_grepdb.management.call_command instead"
        self.assertEqual(cm.exception.message, msg)

    def test_identifier_from_preset(self):
        out = StringIO()
        call_command('grepdb', 'brown', '-s', '-p', 'model_one', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_identifier_and_toggle_from_preset(self):
        out = StringIO()
        call_command('grepdb', 'brown', '-s', '-p', 'model_one_case_insensitive', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_identifier_and_field_types_from_preset(self):
        out = StringIO()
        call_command('grepdb', 'was', '-s', '-p', 'model_two_multiple_fields', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=1)\x1b[0m\n" \
                   "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> char_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=2)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_multiple_identifiers_from_preset(self):
        out = StringIO()
        call_command('grepdb', 'dog', '-s', '-p', 'both_models', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModelTwo'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModelTwo object (pk=1)\x1b[0m\n" \
                   "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field_two\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_command_line_overrides_preset(self):
        out = StringIO()
        call_command('grepdb', 'dog', 'tests.TestModel', '-s', '-p', 'both_models', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field_two\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n"
        self.assertEqual(out.getvalue(), expected)

    def test_misconfigured_preset(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'brown', '-p', 'preset_is_a_list')
        msg = 'Preset "preset_is_a_list" is not a dict-like object'
        self.assertEqual(cm.exception.message, msg)

    def test_unknown_preset(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'brown', '-p', 'what_preset')
        msg = 'Preset "what_preset" not found in DJANGO_GREPDB_PRESETS. Available values are: ' \
              'model_two_multiple_fields, preset_is_a_list, model_one, model_one_case_insensitive, both_models'
        self.assertEqual(cm.exception.message, msg)
