#!/usr/bin/env python2
import cv2
import os, sys
from os import path
from os.path import join

import numpy as np


WIDTH = 16
HEIGHT = 12
L = 10  # number of optical flow to concat

if len(sys.argv) < 3:
    print "Usage: %s [input_dir] [output_dir] [slice=True]" % sys.argv[0]
    print "Author: Kiyoon Kim (yoonkr33@gmail.com)"
    print "Combine u, v optical flow jpeg files to videos. In the video, R channel is for u, G for v, and B is not used."
    print "Only fixed image resolution works (16x12)"
    print "If slice=False, save one optical flow to one video file. Otherwise, slice them to be 2 channels * 10 frames data"
    sys.exit()

input_dir = sys.argv[1]
output_dir = sys.argv[2]
bSlice = sys.argv[3] == 'True'

if output_dir.endswith('/'):
    output_dir = output_dir[:-1]

search_dir = join(input_dir, 'u')
frame = np.zeros((HEIGHT,WIDTH,3), np.uint8)
i = 0
total = 0
for root_u, dirs, files in os.walk(search_dir):
    jpgs = filter(lambda x: x.startswith('frame') and x.endswith('.jpg'), files)
    if len(jpgs) > 0:
        total += 1

if cv2.__version__[0] == '2':
    fourcc = cv2.cv.CV_FOURCC(*'HFYU')  # Huffman lossless
else:
    fourcc = cv2.FOURCC(*'HFYU')

for root_u, dirs, files in os.walk(search_dir):
    jpgs = filter(lambda x: x.startswith('frame') and x.endswith('.jpg'), files)
    if len(jpgs) > 0:
        jpgs = sorted(jpgs)
        i += 1
        out_file = root_u.replace(search_dir, output_dir, 1) + '.avi'
        out_dir = os.path.dirname(out_file)
        print "(%d/%d) Processing %s" % (i, total, out_file)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        root_v = root_u.replace(search_dir, join(input_dir, 'v'), 1)

        if bSlice:
            j = 0
            sliced = jpgs[j:j+L]
            while len(sliced) == L:
                vid_writer = cv2.VideoWriter(out_file + '%03d.avi' % j, fourcc, 25.0, (WIDTH,HEIGHT))
                for jpg in sliced:
                    frame[:,:,2] = cv2.imread(join(root_u, jpg), cv2.IMREAD_GRAYSCALE)
                    frame[:,:,1] = cv2.imread(join(root_v, jpg), cv2.IMREAD_GRAYSCALE)
                    vid_writer.write(frame)
                vid_writer.release()
                j+=1
                sliced = jpgs[j:j+L]
        else:
            vid_writer = cv2.VideoWriter(out_file, fourcc, 25.0, (WIDTH,HEIGHT))
            for jpg in jpgs:
                frame[:,:,2] = cv2.imread(join(root_u, jpg), cv2.IMREAD_GRAYSCALE)
                frame[:,:,1] = cv2.imread(join(root_v, jpg), cv2.IMREAD_GRAYSCALE)
                vid_writer.write(frame)
            vid_writer.release()


