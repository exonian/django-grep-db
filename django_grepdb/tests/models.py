from django.db import models


class TestModel(models.Model):
    text_field = models.TextField(blank=True)
    text_field_two = models.TextField(blank=True)
    char_field = models.CharField(blank=True, max_length=255)

    class Meta:
        app_label = 'tests'


class TestModelTwo(models.Model):
    text_field = models.TextField(blank=True)
    char_field = models.CharField(blank=True, max_length=255)
    url = models.URLField(blank=True)

    class Meta:
        app_label = 'tests'
