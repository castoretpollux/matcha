# Register your models here.
from django.contrib import admin

from core.models import Document, ExternalUser, Folder

admin.site.register(Folder)
admin.site.register(Document)
admin.site.register(ExternalUser)
