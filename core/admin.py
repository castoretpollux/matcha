from django.contrib import admin

from core.models import DynamicPipeline, ChatSession, UserToken
# Register your models here.

admin.site.register(DynamicPipeline)
admin.site.register(ChatSession)
admin.site.register(UserToken)
