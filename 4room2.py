import log_tools as lt

LOG_DIR = 'records/09_26'

all_logs = lt.log_to_dict(LOG_DIR)
for name, logs in all_logs.items():
    print(name)
    print(lt.success_rate(logs))

