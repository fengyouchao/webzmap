# coding=utf-8
from django.template import Template, Context
from django.contrib import admin
from .models import Job, WhiteListFile, BlackListFile, Command


# Register your models here.
class JobAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    list_display = ['id', 'name', 'port', 'status', 'creation_time', 'output_path',
                    'log_path', 'status_path', 'pid', 'read_time', 'time_elapsed', 'time_remaining', 'percent_complete',
                    'active_send_threads', 'sent_total', 'sent_last_one_sec', 'sent_avg_per_sec', 'recv_success_total',
                    'recv_success_last_one_sec', 'recv_success_avg_per_sec', 'recv_total', 'recv_total_last_one_sec',
                    'recv_total_avg_per_sec', 'pcap_drop_total', 'drop_last_one_sec', 'drop_avg_per_sec',
                    'sendto_fail_total', 'sendto_fail_last_one_sec', 'sendto_fail_avg_per_sec', ]
    list_filter = ['status', 'creation_time']
    readonly_fields = ['id', 'creation_time', 'output_path', 'log_path', 'start_time', 'end_time']
    fieldsets = [
        (None, {'fields': ['name', 'port', 'white_list_file', 'black_list_file']}),
        ('选项', {'fields': ['bandwidth', 'verbosity', 'status']}),
    ]

    ordering = ['-creation_time']


class WhiteListFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'file', 'size', 'remark']
    fieldsets = [
        (None, {'fields': ['file', 'remark']}),
    ]


class BlackListFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'file', 'size', 'remark']
    fieldsets = [
        (None, {'fields': ['file', 'remark']}),
    ]


class CommandAdmin(admin.ModelAdmin):
    list_display = ['creation_time', 'cmd', 'job']


admin.site.register(Job, JobAdmin)
admin.site.register(WhiteListFile, WhiteListFileAdmin)
admin.site.register(BlackListFile, BlackListFileAdmin)
admin.site.register(Command, CommandAdmin)
