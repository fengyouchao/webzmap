import os
import subprocess


class ZmapStatus(object):
    def __init__(self):
        self.read_time = None
        self.time_elapsed = 0
        self.time_remaining = 0
        self.percent_complete = 0
        self.active_send_threads = 0
        self.sent_total = 0
        self.sent_last_one_sec = 0
        self.sent_avg_per_sec = 0
        self.recv_success_total = 0
        self.recv_success_last_one_sec = 0
        self.recv_success_avg_per_sec = 0
        self.recv_total = 0
        self.recv_total_last_one_sec = 0
        self.recv_total_avg_per_sec = 0
        self.pcap_drop_total = 0
        self.drop_last_one_sec = 0
        self.drop_avg_per_sec = 0
        self.sendto_fail_total = 0
        self.sendto_fail_last_one_sec = 0
        self.sendto_fail_avg_per_sec = 0


class ShellExecuteError(BaseException):
    def __init__(self, error_msg):
        super(ShellExecuteError, self).__init__(error_msg)


def get_last_line(path):
    cmd = "tail -n 1 %s" % path
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return_code = p.wait()
    if return_code == 0:
        return p.stdout.read().strip()
    else:
        raise ShellExecuteError(p.stderr.read())


def get_current_status(status_path):
    line = get_last_line(status_path)
    if line.startswith("real-time"):
        return None
    status = ZmapStatus()
    items = line.split(",")
    status.read_time = items[0]
    status.time_elapsed = int(items[1])
    status.time_remaining = int(items[2])
    status.percent_complete = float(items[3])
    status.active_send_threads = int(items[4])
    status.sent_total = long(items[5])
    status.sent_last_one_sec = int(items[6])
    status.sent_avg_per_sec = int(items[7])
    status.recv_success_total = long(items[8])
    status.recv_success_last_one_sec = int(items[9])
    status.recv_success_avg_per_sec = int(items[10])
    status.recv_total = long(items[11])
    status.recv_total_last_one_sec = int(items[12])
    status.recv_total_avg_per_sec = int(items[13])
    status.pcap_drop_total = long(items[14])
    status.drop_last_one_sec = int(items[15])
    status.drop_avg_per_sec = int(items[16])
    status.sendto_fail_total = long(items[17])
    status.sendto_fail_last_one_sec = int(items[18])
    status.sendto_fail_avg_per_sec = int(items[19])
    return status


class Zmap(object):
    def __init__(self, execute_bin='/usr/local/sbin/zmap', verbosity=3, cwd=None):
        self.execute_bin = execute_bin
        self.verbosity = verbosity
        self.cwd = cwd

    def scan(self, port, output_path, log_path=None, bandwidth=2, white_list=None, black_list=None, verbosity=None,
             status_updates_path=None, quiet=False):
        if verbosity:
            self.verbosity = verbosity
        cmd = "%s -p %s" % (self.execute_bin, port)
        if output_path:
            cmd += ' -o %s' % output_path
        if bandwidth:
            cmd += " -B %sM" % bandwidth
        if white_list:
            cmd += " -w %s" % white_list
        if black_list:
            cmd += " -b %s" % black_list
        if status_updates_path:
            cmd += " -u %s" % status_updates_path
        if log_path:
            cmd += " -l %s" % log_path
        cmd += ' -v %s' % self.verbosity
        if quiet:
            cmd += ' -q'
        print cmd
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=self.cwd)
        return_code = p.wait()
        return return_code


if __name__ == '__main__':
    update_file_path = "progress.txt"
    zmap = Zmap()
    zmap.scan(80, output_path="output.ip", status_updates_path=update_file_path)
    status = get_current_status(update_file_path)
    import json
    print json.dumps(status)
