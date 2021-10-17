import pickle
from pathlib import Path
from constants import *

def log_to_dict(log_path):

    log_dir = Path(log_path)

    log_names = []
    for l in log_dir.iterdir():
        if l.suffix == '.log':
            log_names.append(l.stem)

    all_logs = {}
    for name in log_names:
        logs = []
        with open(str((log_dir/name).with_suffix('.log')),'r') as log:
            lines = log.readlines()
            for line in lines:
                logs.append(line_to_dict(line))
        all_logs[name] = logs
    return all_logs

def line_to_dict(log_line:str):
    log_line = log_line.replace('x,y','x_y')
    f, m, d, hh, mm, ss, name, data = log_line.split(',')
    return {
        'frame' : int(f),
        'month' : int(m),
        'day' : int(d),
        'hour' : int(hh),
        'minute' : int(mm),
        'second' : int(ss),
        'type' : name,
        'data' : data,
    }

def success_rate(logs: list):
    all_trials = 0
    success = 0
    for log in logs:
        if log['type'] == TEST_ST:
            all_trials += 1
        elif log['type'] == NOR_REW:
            success += 1
    return all_trials, success