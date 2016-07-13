# coding=utf-8
from .models import Job, Command
from django.utils import timezone
from tools.zmap import Zmap, get_current_status
from webzmap.settings import ZMAP, WORK_DIR
import logging
import os
import time
import signal
import uuid

logger = logging.getLogger('cron')
cwd = ZMAP['CWD']
zmap_path = ZMAP['PATH']


def execute_command(job, process):
    commands = Command.objects.filter(job=job).order_by('creation_time')
    for command in commands:
        logger.info("execute job:[%s], type:%s", command.job.id, command.cmd)


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
    logger.debug("run execute job")
    try:
        running_jobs = Job.objects.filter(status=Job.STATUS_RUNNING)
        if len(running_jobs) > 0:
            for job in running_jobs:
                logger.debug(u"detected running: id[%s], name[%s]", job.id, job.name)
        else:
            logger.info("fetch waiting jobs")
            jobs = Job.objects.filter(status=Job.STATUS_PENDING).order_by('-priority')
            if len(jobs) > 0:
                job = jobs[0]
                job_home_path = os.path.join(WORK_DIR, job.id)
                if not os.path.exists(job_home_path):
                    os.makedirs(job_home_path)
                job.status = Job.STATUS_RUNNING
                job.start_time = timezone.now()
                job.save()
                logger.info(u"running job: id[%s], name[%s]", job.id, job.name)
                output_path = os.path.join(job_home_path, 'output.txt')
                log_path = os.path.join(job_home_path, 'job.log')
                status_path = os.path.join(job_home_path, 'status.txt')
                zmap = Zmap(cwd=cwd, execute_bin=zmap_path)
                process = zmap.scan(job.port, subnets=job.subnets, output_path=output_path, log_path=log_path,
                                    verbosity=job.verbosity, bandwidth=job.bandwidth, status_updates_path=status_path)
                job.pid = process.pid
                job.save()
                exit_code = process.poll()
                exit_by_user = False
                while exit_code is None:
                    commands = Command.objects.filter(job=job, status=Command.STATUS_PENDING).order_by('creation_time')
                    for command in commands:
                        logger.info("execute job:[%s], type:%s", command.job.id, command.cmd)
                        if command.cmd == Command.CMD_PAUSE:
                            if job.status == Job.STATUS_RUNNING:
                                process.send_signal(signal.SIGSTOP)
                                command.status = Command.STATUS_DONE
                                command.save()
                                job.status = Job.STATUS_PAUSED
                                job.save()
                            else:
                                command.status = Command.STATUS_ERROR
                                command.save()
                        if command.cmd == Command.CMD_CONTINUE:
                            if job.status == Job.STATUS_PAUSED:
                                process.send_signal(signal.SIGCONT)
                                command.status = Command.STATUS_DONE
                                command.save()
                                job.status = Job.STATUS_RUNNING
                                job.save()
                            else:
                                command.status = Command.STATUS_ERROR
                                command.save()
                        if command.cmd == Command.CMD_STOP:
                            if job.status == Job.STATUS_RUNNING or job.status == Job.STATUS_PAUSED:
                                process.send_signal(signal.SIGKILL)
                                command.status = Command.STATUS_DONE
                                command.save()
                                job.status = Job.STATUS_STOPPED
                                job.end_time = timezone.now()
                                job.save()
                                exit_by_user = True
                    status = get_current_status(status_path)
                    if status:
                        job.update_execute_status(status)
                        job.save()
                    time.sleep(1)
                    exit_code = process.poll()
                if exit_code == 0:
                    logger.info("zmap return success code:%s, log path:%s", exit_code, log_path)
                    job.status = Job.STATUS_DONE
                    job.end_time = timezone.now()
                    job.save()
                elif not exit_by_user:
                    logger.error("zmap return error code:%s, log path:%s", exit_code, log_path)
                    job.status = Job.STATUS_ERROR
                    job.end_time = timezone.now()
                    job.save()

    except BaseException as e:
        logger.exception(e.message)
