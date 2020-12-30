import cv2
import argparse
from pathlib import Path
import os
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-v','--video', dest='video', required=True)
args = parser.parse_args()

vid_dir = Path(args.video)
vid_names = os.listdir(vid_dir)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

for vid_name in tqdm(vid_names, desc='videos'):
    month, day, hour, minute = vid_name.split('.')[0].split('_')
    vid_path = str(vid_dir/vid_name)
    cap = cv2.VideoCapture(vid_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        else:
            break
    cap.release()
    red = False
    red_start_idx = []
    red_duration = []
    for idx, frame in tqdm(enumerate(frames),leave=False, desc=f'analizing {vid_name}',
                            total=len(frames)):
        if not red and np.linalg.norm(frame[10,10]-np.array([0,0,255]))<100:
            red = True
            red_start_idx.append(idx)
        elif red and np.linalg.norm(frame[10,10]-np.array([0,0,255]))>=100 :
            red = False
            red_duration.append(idx-red_start_idx[-1])

    for vid_idx, start_idx,dur in tqdm(zip(range(len(red_duration)),red_start_idx, red_duration), 
                        total=len(red_start_idx),
                        leave=False, desc=f'saving {vid_name}'):
        pre_writer = cv2.VideoWriter(
            str(vid_dir/f'pre_{month}_{day}_{vid_idx}.mp4'),
            fourcc,
            10,
            (frames[0].shape[1], frames[0].shape[0])
        )
        inter_writer = cv2.VideoWriter(
            str(vid_dir/f'inter_{month}_{day}_{vid_idx}.mp4'),
            fourcc,
            10,
            (frames[0].shape[1], frames[0].shape[0])
        )
        for f in frames[start_idx:start_idx+dur]:
            inter_writer.write(f)
        for f in frames[start_idx-dur:start_idx]:
            pre_writer.write(f)
        pre_writer.release()
        inter_writer.release()
