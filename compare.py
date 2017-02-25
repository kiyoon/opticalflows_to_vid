#!/usr/bin/env python2
import cv2
import os, sys
from os import path
from os.path import join

import numpy as np


WIDTH = 16
HEIGHT = 12
L = 10  # number of optical flow to concat

def load_flow(path, dim_ordering='tf', target_size=None):
#    start = time.time()
    """Loads an video into numpy array format.

    # Arguments
        path: Path to video file
        dim_ordering: 'default', 'tf' or 'th'
        grayscale: Boolean, whether to load the video as grayscale.
        target_size: Either `None` (default to original size)
            or tuple of ints `(frame_count, vid_height, vid_width)`.

    # Returns
        numpy array

    # Raises
        invalid dimension ordering value
    """


    cap = cv2.VideoCapture(path)
    frame_count = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT if cv2.__version__[0] == '2' else cv2.CAP_PROP_FRAME_COUNT) + 1e-7)
    height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT if cv2.__version__[0] == '2' else cv2.CAP_PROP_FRAME_HEIGHT) + 1e-7)
    width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH if cv2.__version__[0] == '2' else cv2.CAP_PROP_FRAME_WIDTH) + 1e-7)

    channels = 2*frame_count

    if dim_ordering == 'tf':
        vid = np.zeros([height,width,channels], dtype='uint8')
    else:
        vid = np.zeros([channels,height,width], dtype='uint8')

    i = 0

    # faster version: ignore target_size
    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        #if target_size is not None:
        #    frame = cv2.resize(frame, (target_size[1], target_size[0]))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if dim_ordering == 'th':
            frame = frame.transpose(2,0,1)
            vid[i:i+2] = frame[0:2]
            #vid[i] = frame[2]
            #vid[i+1] = frame[1]
        else:
            vid[:,:,i:i+2] = frame[:,:,0:2]
            #vid[:,:,i] = frame[:,:,2]
            #vid[:,:,i+1] = frame[:,:,1]
        i += 2

    """
    # slower version. maybe np.delete makes it slower
    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        if target_size is not None:
            frame = cv2.resize(frame, (target_size[1], target_size[0]))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if dim_ordering == 'th':
            frame = frame.transpose(2,0,1)
            vid[i:i+2] = frame[0:2]
        else:
            vid[:,:,i:i+2] = frame[:,:,0:2]
        i += 2
    """

    cap.release()
#    print(time.time() - start)
    return vid

if len(sys.argv) < 3:
    print "Usage: %s [vid_dir] [npy_dir]" % sys.argv[0]
    print "Author: Kiyoon Kim (yoonkr33@gmail.com)"
    print "No need to compare avi and npy data, since it turned out that avi is compressed."
    sys.exit()

vid_dir = sys.argv[1]
npy_dir = sys.argv[2]

if npy_dir.endswith('/'):
    npy_dir = npy_dir[:-1]

i = 0
total = 0
total_npy = 0
for root, dirs, files in os.walk(vid_dir):
    avis = filter(lambda x: x.endswith('.avi'), files)
    total += len(avis)
for root, dirs, files in os.walk(npy_dir):
    npys = filter(lambda x: x.endswith('.npy'), files)
    total_npy += len(npys)

if total != total_npy:
    raise Exception('number of files per each directory doesn\'t match')

for root, dirs, files in os.walk(vid_dir):
    avis = filter(lambda x: x.endswith('.avi'), files)
    for avi in avis:
        i += 1
        npy = join(root.replace(vid_dir, npy_dir, 1), avi) + '.npy'
        print "(%d/%d) Comparing %s" % (i, total, npy)
        npy_flow = np.load(npy)
        avi_flow = load_flow(join(root,avi))
        if not np.array_equal(npy_flow, avi_flow):
            print npy_flow, avi_flow
            print npy_flow.shape, avi_flow.shape
            jpg_u = join(root.replace(vid_dir, '/fasthome/kiyoon/hmdb/LR/crop/dropped_optical_flow_img/u', 1), avi)[:-4] + '/frame000001.jpg'
            jpg_v = join(root.replace(vid_dir, '/fasthome/kiyoon/hmdb/LR/crop/dropped_optical_flow_img/v', 1), avi)[:-4] + '/frame000001.jpg'
            u = cv2.imread(jpg_u, cv2.IMREAD_GRAYSCALE)
            v = cv2.imread(jpg_v, cv2.IMREAD_GRAYSCALE)
            for i in range(min(npy_flow.shape[2], avi_flow.shape[2])):
                cv2.imshow('npy', npy_flow[:,:,i])
                cv2.imshow('avi', avi_flow[:,:,i])
                cv2.imshow('u', u)
                cv2.imshow('v', v)
                cv2.waitKey(0)
            cv2.destroyAllWindows()
            raise Exception('different flow data detected')
