# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from webzmap.settings import WORK_DIR, ZMAP
import os
import uuid


def get_white_list_path(self, filename):
    parent = os.path.join(WORK_DIR, "whitelist")
    return os.path.join(parent, filename)


def get_black_list_path(self, filename):
    parent = os.path.join(WORK_DIR, "blacklist")
    return os.path.join(parent, filename)


def gen_job_id():
    return str(uuid.uuid4()).replace('-', '')


class BlackListFile(models.Model):
    """
    Zmap black list file
    """
    name = models.CharField(max_length=30, unique=True, verbose_name=u'名称')
    file = models.FileField(upload_to=get_black_list_path, verbose_name='文件')
    size = models.BigIntegerField(default=0, verbose_name=u'大小')
    remark = models.CharField(max_length=255, verbose_name=u'备注', blank=True, null=True)

    class Meta:
        verbose_name = '黑名单'
        verbose_name_plural = '黑名单'

    def __unicode__(self):
        return self.name


class WhiteListFile(models.Model):
    """
    Zmap white list file
    """
    name = models.CharField(max_length=30, unique=True, verbose_name=u'名称')
    file = models.FileField(upload_to=get_white_list_path, verbose_name='文件')
    size = models.BigIntegerField(default=0, verbose_name=u'大小')
    remark = models.CharField(max_length=255, verbose_name=u'备注', blank=True, null=True)

    class Meta:
        verbose_name = '白名单'
        verbose_name_plural = '白名单'

    def __unicode__(self):
        return self.name


class Job(models.Model):
    STATUS_PENDING = 0
    STATUS_RUNNING = 1
    STATUS_DONE = 2
    STATUS_ERROR = 3
    STATUS_PAUSED = 4
    STATUS_STOPPED = 5
    STATUS_CANCELED = 6
    STATUS_CHOICES = (
        (STATUS_PENDING, u'PENDING'),
        (STATUS_RUNNING, u'RUNNING'),
        (STATUS_DONE, u'DONE'),
        (STATUS_ERROR, u'ERROR'),
        (STATUS_PAUSED, u'PAUSE'),
        (STATUS_STOPPED, u'STOPPED'),
        (STATUS_CANCELED, u'CANCELED'),
    )
    PRIORITY = (
        (0, u'低'),
        (1, u'中'),
        (2, u'高'),
        (3, u'极高'),
    )

    LOG_LEVEL = (
        (0, 'FATAL'),
        (1, 'ERROR'),
        (2, 'WARN'),
        (3, 'INFO'),
        (4, 'DEBUG'),
        (5, 'TRACE'),
    )

    id = models.CharField(max_length=32, default=gen_job_id, primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=30, default=u'扫描任务', verbose_name=u'任务名称')
    port = models.IntegerField(verbose_name=u'扫描端口')
    bandwidth = models.IntegerField(default=ZMAP['DEFAULT_BANDWIDTH'], verbose_name=u'带宽')
    priority = models.IntegerField(choices=PRIORITY, default=1, verbose_name=u'优先级')
    white_list_file = models.ForeignKey(WhiteListFile, null=True, blank=True, verbose_name='白名单')
    black_list_file = models.ForeignKey(BlackListFile, null=True, blank=True, verbose_name=u'黑名单')
    output_path = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'输出文件')
    log_path = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'日志文件')
    status_path = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'状态文件')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name=u'状态')
    verbosity = models.IntegerField(choices=LOG_LEVEL, default=3, verbose_name=u'日志级别')
    creation_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name=u'启动时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=u'结束时间')
    remark = models.CharField(max_length=255, verbose_name=u'备注', null=True, blank=True)

    pid = models.IntegerField(null=True, blank=True, verbose_name=u'进程号')
    read_time = models.DateTimeField(null=True, blank=True)
    time_elapsed = models.IntegerField(default=0)
    time_remaining = models.IntegerField(default=0)
    percent_complete = models.FloatField(default=0)
    active_send_threads = models.IntegerField(default=0)
    sent_total = models.IntegerField(default=0)
    sent_last_one_sec = models.IntegerField(default=0)
    sent_avg_per_sec = models.IntegerField(default=0)
    recv_success_total = models.IntegerField(default=0)
    recv_success_last_one_sec = models.IntegerField(default=0)
    recv_success_avg_per_sec = models.IntegerField(default=0)
    recv_total = models.IntegerField(default=0)
    recv_total_last_one_sec = models.IntegerField(default=0)
    recv_total_avg_per_sec = models.IntegerField(default=0)
    pcap_drop_total = models.IntegerField(default=0)
    drop_last_one_sec = models.IntegerField(default=0)
    drop_avg_per_sec = models.IntegerField(default=0)
    sendto_fail_total = models.IntegerField(default=0)
    sendto_fail_last_one_sec = models.IntegerField(default=0)
    sendto_fail_avg_per_sec = models.IntegerField(default=0)

    def update_execute_status(self, status):
        self.read_time = status.read_time
        self.time_elapsed = status.time_elapsed
        self.time_remaining = status.time_remaining
        self.percent_complete = status.percent_complete
        self.active_send_threads = status.active_send_threads
        self.sent_total = status.sent_total
        self.sent_last_one_sec = status.sent_last_one_sec
        self.sent_avg_per_sec = status.sent_avg_per_sec
        self.recv_success_total = status.recv_success_total
        self.recv_success_last_one_sec = status.recv_success_last_one_sec
        self.recv_success_avg_per_sec = status.recv_success_avg_per_sec
        self.recv_total = status.recv_total
        self.recv_total_last_one_sec = status.recv_total_last_one_sec
        self.recv_total_avg_per_sec = status.recv_total_avg_per_sec
        self.pcap_drop_total = status.pcap_drop_total
        self.drop_last_one_sec = status.drop_last_one_sec
        self.drop_avg_per_sec = status.drop_avg_per_sec
        self.sendto_fail_total = status.sendto_fail_total
        self.sendto_fail_last_one_sec = status.sendto_fail_last_one_sec
        self.sendto_fail_avg_per_sec = status.sendto_fail_avg_per_sec

    def hit_rate(self):
        return self.recv_success_total / self.sent_total

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'

    def __unicode__(self):
        return self.name


class Command(models.Model):
    STATUS_PENDING = 0
    STATUS_DONE = 1
    STATUS_ERROR = 2
    STATUS_TYPES = (
        (STATUS_PENDING, u'Pending'),
        (STATUS_DONE, u'DONE'),
        (STATUS_ERROR, u'ERROR'),
    )
    CMD_PAUSE = 0
    CMD_CONTINUE = 1
    CMD_STOP = 2
    CMD_TYPES = (
        (CMD_PAUSE, u'PAUSE'),
        (CMD_CONTINUE, u'CONTINUE'),
        (CMD_STOP, u'STOP'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(default=timezone.now)
    cmd = models.IntegerField(choices=CMD_TYPES)
    status = models.IntegerField(choices=STATUS_TYPES, default=STATUS_PENDING)

    class Meta:
        verbose_name = '命令'
        verbose_name_plural = '命令'
