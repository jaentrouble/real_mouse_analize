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
LINE_THICK = 1
BATCH_SIZE = 500

parser = argparse.ArgumentParser()
parser.add_argument('-v','--video', dest='video', required=True)
args = parser.parse_args()

vid_dir = Path(args.video)
vid_names = os.listdir(vid_dir)
vid_names.sort()

distances = []

def gaussian_heatmap_batch(rr, cc, shape, sigma=10):
    """
    Returns a heat map of a point
    Shape is expected to be (HEIGHT, WIDTH)
    [r,c] should be the point i.e. opposite of pygame notation.

    Parameters
    ----------
    rr : np.array
        batch of row of the points
    cc : np.array
        batch of the points
    shape : tuple of int
        (HEIGHT, WIDTH)

    Returns
    -------
    heatmap : np.array
        shape : (HEIGHT, WIDTH)
    """
    coordinates = np.stack(np.meshgrid(
        np.arange(shape[0],dtype=np.float32),
        np.arange(shape[1],dtype=np.float32),
        indexing='ij',
    ), axis=-1)[np.newaxis,...]
    keypoints = np.stack([rr,cc],axis=-1).reshape((-1,1,1,2))
    heatmaps = np.exp(-(np.sum((coordinates-keypoints)**2,axis=-1))/(2*sigma**2))

    return heatmaps


for vid_name in tqdm(vid_names, desc='videos'):
    if not (vid_name.split('.')[-1] in ('mkv','mp4','ts')):
        continue
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
        # mask[0:20,0:60] = False
        rr, cc = np.nonzero(mask)
        pos_rr.append(np.mean(rr).astype(np.int))
        pos_cc.append(np.mean(cc).astype(np.int))
    frame_map = frames[-1].copy()
    # white_map = np.ones_like(frame_map) * 255
    for i in trange(len(pos_rr)-1, leave=False, 
                    desc=f'drawing lines {vid_name}'):
        frame_map = cv2.line(
            frame_map,
            (pos_cc[i],pos_rr[i]),
            (pos_cc[i+1],pos_rr[i+1]),
            LINE_OVER,
            thickness=LINE_THICK
        )
        # white_map = cv2.line(
        #     white_map,
        #     (pos_cc[i],pos_rr[i]),
        #     (pos_cc[i+1],pos_rr[i+1]),
        #     LINE_WHITE,
        #     thickness=LINE_THICK
        # )
    # dist = 0
    # bef_r = pos_rr[0]
    # bef_c = pos_cc[0]
    # for r, c in zip(pos_rr[1:], pos_cc[1:]):
    #     dist += np.linalg.norm(
    #         np.subtract([bef_r,bef_c],[r,c])
    #     )
    #     bef_r = r
    #     bef_c = c
    # distances.append((vid_name, dist))
    heatmap_final = np.zeros(frames[-1].shape[:2])
    for i in trange(len(frames)//BATCH_SIZE+1, leave=False):
        heatmaps = gaussian_heatmap_batch(
            pos_rr[i*BATCH_SIZE:(i+1)*BATCH_SIZE], 
            pos_cc[i*BATCH_SIZE:(i+1)*BATCH_SIZE], 
            frames[-1].shape[0:2])
        heatmap_piece = np.sum(heatmaps, axis=0)
        heatmap_final += heatmap_piece
    heatmap_final = np.sqrt(heatmap_final)
    norm_hm = ((heatmap_final/(np.max(heatmap_final)))*255).astype(np.uint8)
    color_hm = cv2.applyColorMap(norm_hm, cv2.COLORMAP_JET)
    mixed = cv2.addWeighted(frames[-1],0.5, color_hm,0.5,0.0)

    cv2.imwrite(str(vid_dir/f'{name}_overlay.png'), frame_map)    
    # cv2.imwrite(str(vid_dir/f'{name}_white.png'), white_map)
    cv2.imwrite(str(vid_dir/f'{name}_heatmap.png'),mixed)

# with open(vid_dir/'distances.txt', 'w') as f:
#     for vid_name, dist in distances:
#         f.write(f'{vid_name} : {dist:.2f}\n')