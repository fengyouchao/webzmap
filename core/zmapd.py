from core.models import Job, Command
from django.utils import timezone
from tools.zmap import Zmap, get_current_status
from webzmap.settings import ZMAP, WORK_DIR
from django import db
import logging
import os
import time
import multiprocessing
import signal
import sys

logger = logging.getLogger('cron')
cwd = ZMAP['CWD']
zmap_path = ZMAP['PATH']
pid_file = ZMAP['PID_FILE']
max_bandwidth = ZMAP['MAX_BANDWIDTH']


def execute_job(job_id):
    job = Job.objects.get(id=job_id)
    print "start job", job.name
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
                        verbosity=job.verbosity, bandwidth=job.bandwidth, status_updates_path=status_path,
                        stderr=file("/dev/null"))
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
    if os.path.exists(pid_file):
        sys.stdout.write("zmapd is already started\n")
        sys.exit()
    run_daemon_process(pid_file=pid_file, start_msg="Start zmapd(%s)\n")
    while True:
        time.sleep(1)
        running_jobs = Job.objects.filter(status=Job.STATUS_RUNNING)
        total_bandwidth = 0
        for job in running_jobs:
            total_bandwidth += job.bandwidth
        if total_bandwidth >= max_bandwidth:
            logger.debug(u"Achieve maximum bandwidth:%sM", max_bandwidth)
            continue
        jobs = [x for x in Job.objects.filter(status=Job.STATUS_PENDING).order_by('-priority')]
        db.close_old_connections()
        for j in jobs:
            p = multiprocessing.Process(target=execute_job, args=(j.id,))
            p.start()


def status():
    try:
        f = open(pid_file, 'r')
        pid = int(f.readline())
        sys.stdout.write('zmapd(pid %d) is running...\n' % pid)
    except IOError:
        sys.stdout.write("zmapd is stopped\n")


def stop():
    sys.stdout.write("Stopping zmapd...\n")
    try:
        f = open(pid_file, 'r')
        pid = int(f.readline())
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            sys.stdout.write("zmapd is not running\n")
        os.remove(pid_file)
        sys.stdout.write("                 [OK]\n")
    except IOError:
        sys.stdout.write("zmapd is not running\n")


def restart():
    stop()
    start()


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
        file(pid_file, 'w+').write("%s\n" % pid)
    # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    return pid
