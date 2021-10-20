import log_tools as lt
from pathlib import Path


LOG_DIR = 'records/09_26'

log_dir = Path(LOG_DIR)

all_logs = lt.log_to_dict(LOG_DIR)
for name, logs in all_logs.items():
    