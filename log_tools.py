import pickle
from pathlib import Path
from constants import *
import cv2

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
    data = data.rstrip()
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
    """success_rate

    return
    ------
    all_trials, success, fail, timeover
    
    """
    all_trials = 0
    success = 0
    fail = 0
    timeover = 0
    for log in logs:
        if log['type'] == TEST_ST:
            all_trials += 1
        elif log['type'] == NOR_REW:
            success += 1
        elif log['type'] == FAILED:
            fail+= 1
        elif log['type'] == TIME_OVR:
            timeover += 1
    return all_trials, success, fail, timeover

def test_cutter(vid_path : Path, logs: list):
    """log_to_vid
    vid_path : path including video name
    
    """
    cap = cv2.VideoCapture(str(vid_path.with_suffix('.ts')))
    cur_frame = 0
    record = False
    vid_writer = None
    vid_count = 0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    success_names = []
    for log in logs:
        while cur_frame<=log['frame']:
            ret, new_frame = cap.read()
            cur_frame += 1
            if not ret:
                break
            if record:
                vid_writer.write(new_frame)
        if not ret:
            break

        if log['type']==TEST_ST:
            new_name = vid_path.stem + '_' + str(vid_count) + '.mp4'
            vid_writer = cv2.VideoWriter(
                str(vid_path.with_name(new_name)),
                fourcc,
                10,
                (new_frame.shape[1],new_frame.shape[0])
            )
            record = True
            print('recording')
        elif log['type'] in [TIME_OVR, FAILED, NOR_REW] :
            if log['type']==NOR_REW:
                success_names.append(new_name)
            vid_writer.release()
            vid_count += 1
            record = False
            print(log['type'])
    if len(success_names)>0:
        suc_log_name = vid_path.stem + '_success.txt'
        with vid_path.with_name(suc_log_name).open('w') as f:
            for name in success_names:
                f.write(name+'\n')