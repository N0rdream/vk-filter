from django.contrib import admin
from .models import StopWord, History


class CustomHistoryAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'has_stopword', 'is_not_member')

admin.site.register(StopWord)
admin.site.register(History, CustomHistoryAdmin)
