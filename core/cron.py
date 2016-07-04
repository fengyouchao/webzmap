# -*- coding: utf-8 -*-
# coding=utf-8
from .models import Job, STATUS_WAITING, STATUS_RUNNING
import logging
from tools.zmap import Zmap
from webzmap.settings import ZMAP

logger = logging.getLogger('cron')
cwd = ZMAP['CWD']


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
                logger.info(u"running job: id[%s], name[%s]", job.id, job.name)
                zmap = Zmap(cwd=cwd)
    except BaseException, e:
        logger.error("type:%s,message:%s", type(e), e.message)


def monitor_job_status():
    pass
