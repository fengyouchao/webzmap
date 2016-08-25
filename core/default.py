from django.conf import settings
from webzmap.settings import WORK_DIR

cwd = getattr(settings, "ZMAP_CWD", WORK_DIR)
zmap_path = getattr(settings, "ZMAP_PATH", '/usr/local/sbin/zmap')
max_bandwidth = getattr(settings, 'ZMAP_MAX_BANDWIDTH', 8)
pid_file = getattr(settings, 'ZMAPD_PID_FILE', '/var/run/zmapd.pid')
default_bandwidth = getattr(settings, 'ZMAP_DEFAULT_BANDWIDTH', 2)

