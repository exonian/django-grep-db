# -*- coding: utf-8 -*-
from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils.six import StringIO

from models import TestModel


class TestShowValues(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(text_field="Lorem ipsum dolor sit amet, eu eam option expetendis. An equidem "
                                            "noluisse appareat his. Feugiat meliore vix ex, vel ad elit feugiat.")
        TestModel.objects.create(text_field="In qui doming evertitur, cum dicam vituperatoribus id. Insolens "
                                            "assueverit quo an, et case choro minimum usu, te sit mediocrem.\n"
                                            "Te placerat deserunt cum, et per enim mutat audire, putent graeco "
                                            "eligendi ne vix. Ut nisl ornatus nec, discere fierent eu has.")
        TestModel.objects.create(text_field="Cu usu molestie invidunt molestie usu cu.")

    def test_default_format_on_single_line_content(self):
        out = StringIO()
        call_command('grepdb', 'Feugiat', 'tests.TestModel', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n" \
                   "Lorem ipsum dolor sit amet, eu eam option expetendis. An equidem noluisse appareat his. " \
                   "\x1b[43m\x1b[30mFeugiat\x1b[0m meliore vix ex, vel ad elit feugiat.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_default_format_on_multi_line_content(self):
        out = StringIO()
        call_command('grepdb', 'dicam', 'tests.TestModel', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n" \
                   "In qui doming evertitur, cum \x1b[43m\x1b[30mdicam\x1b[0m vituperatoribus id. Insolens " \
                   "assueverit quo an, et case choro minimum usu, te sit mediocrem.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_show_all_on_multi_line_content(self):
        out = StringIO()
        call_command('grepdb', 'dicam', 'tests.TestModel', '-sa', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n" \
                   "In qui doming evertitur, cum \x1b[43m\x1b[30mdicam\x1b[0m vituperatoribus id. Insolens " \
                   "assueverit quo an, et case choro minimum usu, te sit mediocrem.\n" \
                   "Te placerat deserunt cum, et per enim mutat audire, putent graeco " \
                   "eligendi ne vix. Ut nisl ornatus nec, discere fierent eu has.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_show_surrounding_chars_on_single_line_content(self):
        out = StringIO()
        call_command('grepdb', 'Feugiat', 'tests.TestModel', '-s5', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n" \
                   "his. \x1b[43m\x1b[30mFeugiat\x1b[0m meli\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_show_surrounding_chars_across_lines(self):
        out = StringIO()
        call_command('grepdb', 'mediocrem\.', 'tests.TestModel', '-s5', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n" \
                   "sit \x1b[43m\x1b[30mmediocrem.\x1b[0m\nTe p\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_invalid_show_option(self):
        with self.assertRaises(CommandError) as cm:
            call_command('grepdb', 'Feugiat', '-sm')
        msg = "Error: argument --show-values/-s: Show values style must be one of 'a, l' or an integer"
        self.assertEqual(cm.exception.message, msg)

    def test_show_surrounding_chars_with_multiple_joined_matches(self):
        """Output should highlight every match accurately"""
        out = StringIO()
        call_command('grepdb', 'molestie', 'tests.TestModel', '-s10', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=3)\x1b[0m\n"\
                   "\x1b[43m\x1b[30mmolestie\x1b[0m invidunt \x1b[43m\x1b[30mmolestie\x1b[0m usu cu.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_show_surrounding_chars_with_overlapping_matches(self):
        """Output should highlight every match accurately"""
        out = StringIO()
        call_command('grepdb', '.{5}molestie.{5}', 'tests.TestModel', '-s5', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=3)\x1b[0m\n"\
                   "\x1b[43m\x1b[30m usu molestie invi\x1b[0m\x1b[43m\x1b[30mdunt molestie usu \x1b[0mcu.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_default_format_on_single_line_content_case_insensitive(self):
        out = StringIO()
        call_command('grepdb', 'MELIORE', 'tests.TestModel', '-i', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n" \
                   "Lorem ipsum dolor sit amet, eu eam option expetendis. An equidem noluisse appareat his. " \
                   "Feugiat \x1b[43m\x1b[30mmeliore\x1b[0m vix ex, vel ad elit feugiat.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_show_all_on_multi_line_content_case_insensitive(self):
        out = StringIO()
        call_command('grepdb', 'DICAM', 'tests.TestModel', '-sa', '-i', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=2)\x1b[0m\n" \
                   "In qui doming evertitur, cum \x1b[43m\x1b[30mdicam\x1b[0m vituperatoribus id. Insolens " \
                   "assueverit quo an, et case choro minimum usu, te sit mediocrem.\n" \
                   "Te placerat deserunt cum, et per enim mutat audire, putent graeco " \
                   "eligendi ne vix. Ut nisl ornatus nec, discere fierent eu has.\n\n"
        self.assertEqual(out.getvalue(), expected)

    def test_show_surrounding_chars_on_single_line_content_case_insensitive(self):
        out = StringIO()
        call_command('grepdb', 'MELIORE', 'tests.TestModel', '-s5', '-i', stdout=out)
        expected = "\x1b[1m\x1b[36m\n<class 'django_grepdb.tests.models.TestModel'> text_field\x1b[0m\n" \
                   "\x1b[1m\x1b[32mTestModel object (pk=1)\x1b[0m\n" \
                   "giat \x1b[43m\x1b[30mmeliore\x1b[0m vix\n\n"
        self.assertEqual(out.getvalue(), expected)
