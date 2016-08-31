from core.models import Job, Command
from django.utils import timezone
from tools.zmap import Zmap, get_current_status
from webzmap.settings import WORK_DIR
from django import db
import default as settings
import logging
import os
import time
import multiprocessing
import signal
import sys
import fcntl

logger = logging.getLogger('zmapd')


class ProcessStatus(object):
    def __init__(self, running=False, pid=-1):
        self.running = running
        self.pid = pid


def execute_job(job_id):
    job = Job.objects.get(id=job_id)
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
    zmap = Zmap(cwd=settings.cwd, execute_bin=settings.zmap_path)
    process = zmap.scan(job.port, subnets=job.subnets, output_path=output_path, log_path=log_path,
                        verbosity=job.verbosity, bandwidth=job.bandwidth, status_updates_path=status_path,
                        stderr=open("/dev/null"))
    job.pid = process.pid
    job.save()
    exit_code = process.poll()
    exit_by_user = False
    while exit_code is None:
        # check job is deleted
        try:
            Job.objects.get(id=job.id)
        except Job.DoesNotExist:
            process.send_signal(signal.SIGKILL)
            exit_by_user = True
            logger.info("stopped deleted job:id[%s] name[%s]", job.id, job.name)
            time.sleep(1)
            exit_code = process.poll()
            continue
        commands = Command.objects.filter(job=job, status=Command.STATUS_PENDING).order_by('creation_time')
        for command in commands:
            logger.info("execute command on job:[%s], type:%s", command.job.id, command.cmd)
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
        try:
            status = get_current_status(status_path)
            if status:
                job.update_execute_status(status)
                job.save()
        except ValueError:
            pass
        time.sleep(1)
        exit_code = process.poll()
    if exit_code == 0:
        logger.info("zmap return success code:%s, log path:%s", exit_code, log_path)
        job.status = Job.STATUS_DONE
        job.percent_complete = 100
        job.end_time = timezone.now()
        job.time_remaining = 0
        job.save()
    elif not exit_by_user:
        logger.error("zmap return error code:%s, log path:%s", exit_code, log_path)
        job.status = Job.STATUS_ERROR
        job.end_time = timezone.now()
        job.save()


def start():
    if os.path.exists(settings.pid_file):
        with open(settings.pid_file) as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
            except IOError:
                sys.stdout.write("zmapd is already started\n")
                return

    run_daemon_process(pid_file=settings.pid_file, start_msg="Start zmapd(%s)\n")
    pid_file = open(settings.pid_file)
    fcntl.flock(pid_file, fcntl.LOCK_SH)
    while True:
        time.sleep(1)
        running_jobs = Job.objects.filter(status=Job.STATUS_RUNNING)
        total_bandwidth = 0
        for job in running_jobs:
            total_bandwidth += job.bandwidth
        if total_bandwidth >= settings.max_bandwidth:
            logger.debug(u"Achieve maximum bandwidth:%sM", settings.max_bandwidth)
            continue
        jobs = [x for x in Job.objects.filter(status=Job.STATUS_PENDING).order_by('-priority')]
        db.close_old_connections()
        for j in jobs:
            p = multiprocessing.Process(target=execute_job, args=(j.id,))
            p.start()


def status():
    process_status = get_process_status()
    if process_status.running:
        sys.stdout.write('zmapd(pid %d) is running...\n' % process_status.pid)
    else:
        sys.stdout.write("zmapd is stopped\n")


def stop():
    sys.stdout.write("Stopping zmapd...")
    process_status = get_process_status()
    if process_status.running:
        with open(settings.pid_file, 'r') as f:
            pid = int(f.readline())
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                sys.stdout.write("                 [FAILED]\n")
                sys.stdout.write("zmapd is not running\n")
        os.remove(settings.pid_file)
        sys.stdout.write("                 [OK]\n")
    else:
        sys.stdout.write("                 [FAILED]\n")
        sys.stdout.write("zmapd is not running\n")


def restart():
    stop()
    start()


def get_process_status():
    if os.path.exists(settings.pid_file):
        with open(settings.pid_file) as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
                os.remove(settings.pid_file)
                return ProcessStatus(False)
            except IOError:
                pid = int(f.readline())
                return ProcessStatus(True, pid)
    else:
        return ProcessStatus(False)


def run_daemon_process(stdout='/dev/null', stderr=None, stdin='/dev/null',
                       pid_file=None, start_msg='started with pid %s'):
    """
         This forks the current process into a daemon.
         The stdin, stdout, and stderr arguments are file names that
         will be opened and be used to replace the standard file descriptors
         in sys.stdin, sys.stdout, and sys.stderr.
         These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
         may not appear in the order that you expect.
    """
    # flush io
    sys.stdout.flush()
    sys.stderr.flush()
    # Do first fork.
    try:
        if os.fork() > 0:
            sys.exit(0)  # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()
    # Do second fork.
    try:
        if os.fork() > 0:
            sys.exit(0)  # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Open file descriptors and print start message
    if not stderr:
        stderr = stdout
        si = file(stdin, 'r')
        so = file(stdout, 'a+')
        se = file(stderr, 'a+', 0)  # unbuffered
        pid = str(os.getpid())
        sys.stderr.write(start_msg % pid)
        sys.stderr.flush()
    if pid_file:
        with open(pid_file, 'w+') as f:
            f.write("%s\n" % pid)
    # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    return pid
