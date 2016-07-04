from django.contrib import admin
from .models import Job, WhiteListFile, BlackListFile


# Register your models here.
class JobAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    list_display = ['id', 'name', 'port', 'status', 'progress', 'left_time', 'hit_rate', 'creation_time']
    list_filter = ['status', 'creation_time']
    readonly_fields = ['id']


class WhiteListFileAdmin(admin.ModelAdmin):
    list_display = ['file', 'size', 'remark']


class BlackListFileAdmin(admin.ModelAdmin):
    list_display = ['file', 'size', 'remark']


admin.site.register(Job, JobAdmin)
admin.site.register(WhiteListFile, WhiteListFileAdmin)
admin.site.register(BlackListFile, BlackListFileAdmin)
