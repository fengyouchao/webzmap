# coding=utf-8
from .models import Job, STATUS_WAITING, STATUS_RUNNING, STATUS_SUCCESS, STATUS_ERROR
from django.utils import timezone
from tools.zmap import Zmap
from webzmap.settings import ZMAP, WORK_DIR
import logging
import os
import uuid

logger = logging.getLogger('cron')
cwd = ZMAP['CWD']


def create_output_path(job):
    parent = os.path.join(WORK_DIR, "output")
    if not os.path.exists(parent):
        os.makedirs(parent)
    t = timezone.now().strftime('%Y%m%d')
    u = job.id[:6]
    name = "%s-%s-%s.txt" % (job.port, t, u)
    return os.path.join(parent, name)


def create_log_path(job):
    parent = os.path.join(WORK_DIR, "logs")
    if not os.path.exists(parent):
        os.makedirs(parent)
    t = timezone.now().strftime('%Y%m%d')
    u = job.id[:6]
    name = "%s-%s-%s.log" % (job.port, t, u)
    return os.path.join(parent, name)


def create_status_path(job):
    parent = os.path.join(WORK_DIR, "status")
    if not os.path.exists(parent):
        os.makedirs(parent)
    t = timezone.now().strftime('%Y%m%d')
    u = job.id[:6]
    name = "%s-%s-%s.status" % (job.port, t, u)
    return os.path.join(parent, name)


def execute_job():
    try:
        running_jobs = Job.objects.filter(status=STATUS_RUNNING)
        if len(running_jobs) > 0:
            for job in running_jobs:
                logger.debug(u"detected running: id[%s], name[%s]", job.id, job.name)
        else:
            logger.info("fetch waiting jobs")
            jobs = Job.objects.filter(status=STATUS_WAITING).order_by('-priority')
            if len(jobs) > 0:
                job = jobs[0]
                job.output_path = create_output_path(job)
                job.log_path = create_log_path(job)
                job.status_path = create_status_path(job)
                job.status = STATUS_RUNNING
                job.start_time = timezone.now()
                job.save()
                logger.info(u"running job: id[%s], name[%s]", job.id, job.name)
                zmap = Zmap(cwd=cwd)
                logger.info("%s", cwd)
                exit_code = zmap.scan(job.port, output_path=job.output_path, log_path=job.log_path,
                                      verbosity=job.verbosity, bandwidth=job.bandwidth, status_updates_path=job.id)
                if exit_code != 0:
                    logger.error("zmap return error code:%s, log path:%s", exit_code, job.log_path)
                    job.status = STATUS_ERROR
                else:
                    logger.info("zmap return success code:%s, log path:%s", exit_code, job.log_path)
                    job.status = STATUS_SUCCESS
                job.end_time = timezone.now()
                job.save()
    except BaseException, e:
        logger.exception(e.message)


def monitor_job_status():
    pass
