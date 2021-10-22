import log_tools as lt
from pathlib import Path
import numpy as np

LOG_DIRS = [
    'records/09_22',
    'records/09_23',
    'records/09_24',
    'records/09_25',
    'records/09_26',
    'records/09_27',
    'records/09_28',
    'records/09_29',
    'records/09_30',
]
results = {}
for log_dir in LOG_DIRS:
    log_dir = Path(log_dir)
    all_logs = lt.log_to_dict(log_dir)
    result = np.zeros(4)
    for name, logs in all_logs.items():
        lt.test_cutter(log_dir/name, logs)
        r = lt.success_rate(logs)
        if r[1]>0: print(name, ' success')
        result += r
    results[log_dir]=result

print(results)