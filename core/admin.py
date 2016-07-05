# coding=utf-8
from django.template import Template, Context
from django.contrib import admin
from .models import Job, WhiteListFile, BlackListFile, STATUS_WAITING, STATUS_SUCCESS, STATUS_ERROR, STATUS_RUNNING


# Register your models here.
class JobAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    list_display = ['id', 'name', 'port', 'status', 'progress', 'left_time', 'hit_rate', 'creation_time', 'operation']
    list_filter = ['status', 'creation_time']
    readonly_fields = ['id', 'creation_time', 'output_path', 'log_path', 'start_time', 'end_time', 'progress',
                       'left_time', 'hit_rate']
    fieldsets = [
        (None, {'fields': ['name', 'port', 'white_list_file', 'black_list_file']}),
        ('选项', {'fields': ['bandwidth', 'verbosity', 'status']}),
    ]

    def operation(self, obj):
        if obj.status == STATUS_WAITING:
            value = "<button disabled>查看日志</button><button disabled>下载结果</button"
        elif obj.status == STATUS_RUNNING:
            value = "<button>查看日志</button><button disabled >下载结果</button"
        elif obj.status == STATUS_SUCCESS:
            value = "<button>查看日志</button><button >下载结果</button"
        elif obj.status == STATUS_ERROR:
            value = "<button>查看日志</button><button disabled>下载结果</button"
        template = Template(value)
        return template.render(Context())

    operation.short_description = '操作'
    operation.allow_tag = True
    ordering = ['-creation_time']


class WhiteListFileAdmin(admin.ModelAdmin):
    list_display = ['file', 'size', 'remark']
    fieldsets = [
        (None, {'fields': ['file', 'remark']}),
    ]


class BlackListFileAdmin(admin.ModelAdmin):
    list_display = ['file', 'size', 'remark']
    fieldsets = [
        (None, {'fields': ['file', 'remark']}),
    ]


admin.site.register(Job, JobAdmin)
admin.site.register(WhiteListFile, WhiteListFileAdmin)
admin.site.register(BlackListFile, BlackListFileAdmin)
