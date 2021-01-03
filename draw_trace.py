import cv2
import argparse
from pathlib import Path
import os
from tqdm import tqdm, trange
import numpy as np
import skimage
import imageio

MARKER = np.array([0,255,255])
LINE_OVER = [0,255,255]
LINE_WHITE = [0,0,170]

parser = argparse.ArgumentParser()
parser.add_argument('-v','--video', dest='video', required=True)
args = parser.parse_args()

vid_dir = Path(args.video)
vid_names = os.listdir(vid_dir)

for vid_name in tqdm(vid_names, desc='videos'):
    name = vid_name.split('.')[0]
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
    pos_rr = []
    pos_cc = []
    for idx, frame in tqdm(enumerate(frames),leave=False, 
                            desc=f'analizing {vid_name}',
                            total=len(frames)):
        mask = np.linalg.norm(frame-MARKER,axis=-1)<100
        mask[0:20,0:60] = False
        rr, cc = np.nonzero(mask)
        pos_rr.append(np.mean(rr).astype(np.int))
        pos_cc.append(np.mean(cc).astype(np.int))
    frame_map = frames[-1]
    white_map = np.ones_like(frame_map) * 255
    for i in trange(len(pos_rr)-1, leave=False, 
                    desc=f'drawing lines {vid_name}'):
        frame_map = cv2.line(
            frame_map,
            (pos_cc[i],pos_rr[i]),
            (pos_cc[i+1],pos_rr[i+1]),
            LINE_OVER,
            thickness=5
        )
        white_map = cv2.line(
            white_map,
            (pos_cc[i],pos_rr[i]),
            (pos_cc[i+1],pos_rr[i+1]),
            LINE_WHITE,
            thickness=5
        )

    cv2.imwrite(str(vid_dir/f'{name}_overlay.png'), frame_map)    
    cv2.imwrite(str(vid_dir/f'{name}_white.png'), white_map)