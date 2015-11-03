from django.conf.urls import include, url
from django.contrib import admin

from models import TestModel, TestModelTwo

admin.site.register(TestModel)
admin.site.register(TestModelTwo)


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
