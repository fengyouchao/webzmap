# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from webzmap.settings import WORK_DIR
import os
import uuid

STATUS_WAITING = 0
STATUS_RUNNING = 1
STATUS_SUCCESS = 2
STATUS_ERROR = 3


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
    file = models.FileField(upload_to=get_black_list_path, verbose_name='文件')
    size = models.BigIntegerField(default=0, verbose_name=u'大小')
    remark = models.CharField(max_length=255, verbose_name=u'备注', blank=True, null=True)

    class Meta:
        verbose_name = '黑名单'
        verbose_name_plural = '黑名单'

    def __unicode__(self):
        return self.file.name


class WhiteListFile(models.Model):
    """
    Zmap white list file
    """
    file = models.FileField(upload_to=get_white_list_path, verbose_name='文件')
    size = models.BigIntegerField(default=0, verbose_name=u'大小')
    remark = models.CharField(max_length=255, verbose_name=u'备注', blank=True, null=True)

    class Meta:
        verbose_name = '白名单'
        verbose_name_plural = '白名单'

    def __unicode__(self):
        return self.file.name


class Job(models.Model):
    STATUS_TYPE = (
        (STATUS_WAITING, u'等待执行'),
        (STATUS_RUNNING, u'正在执行'),
        (STATUS_SUCCESS, u'执行完成'),
        (STATUS_ERROR, u'执行错误'),
    )
    PRIORITY = (
        (0, u'低'),
        (1, u'中'),
        (2, u'高'),
        (3, u'极高'),
    )
    id = models.CharField(max_length=32, default=gen_job_id, primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=30, default=u'扫描任务', verbose_name=u'任务名称')
    port = models.IntegerField(verbose_name=u'扫描端口')
    bandwidth = models.IntegerField(default=100, verbose_name=u'带宽')
    priority = models.IntegerField(choices=PRIORITY, default=1, verbose_name=u'优先级')
    white_list_file = models.ForeignKey(WhiteListFile, null=True, blank=True, verbose_name='白名单')
    black_list_file = models.ForeignKey(BlackListFile, null=True, blank=True, verbose_name=u'黑名单')
    output_path = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'输出文件')
    log_path = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'日志文件')
    status_path = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'状态文件')
    status = models.IntegerField(choices=STATUS_TYPE, default=0, verbose_name=u'状态')
    progress = models.CharField(max_length=3, null=True, blank=True, verbose_name=u'执行进度')
    left_time = models.CharField(max_length=15, null=True, blank=True, verbose_name=u'剩余时间')
    verbosity = models.IntegerField(default=3, verbose_name=u'日志级别')
    creation_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name=u'启动时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=u'结束时间')
    hit_rate = models.CharField(max_length=10, null=True, blank=True, verbose_name=u'命中率')
    remark = models.CharField(max_length=255, verbose_name=u'备注', null=True, blank=True)

    def get_white_list_file_path(self):
        if self.white_list_file:
            return os.path.abspath(self.white_list_file.file.name)
        else:
            return None

    def get_black_list_file_path(self):
        if self.black_list_file:
            return os.path.abspath(self.black_list_file.file.name)
        return None

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
