#!/usr/bin/env python

'''
Multithreaded video processing sample.
Usage:
   video_threaded.py {<video device number>|<video file name>}

   Shows how python threading capabilities can be used
   to organize parallel captured frame processing pipeline
   for smoother playback.

Keyboard shortcuts:

   ESC - exit
   space - switch between multi and single threaded processing
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2

from multiprocessing.pool import ThreadPool
from collections import deque

from common import clock, draw_str, StatValue
import video

from math import *
import numpy as np
import cv2
import sys
import os
import argparse
import time
import skvideo.io
import skvideo.datasets

class DummyTask:
    def __init__(self, data):
        self.data = data
    def ready(self):
        return True
    def get(self):
        return self.data

def read_bboxes(frame):
  # choose the corners (or edges) of the tracking bbox
  bbox1 = cv2.selectROI('tracking', frame)
  bbox2 = cv2.selectROI('tracking', frame)
  bbox3 = cv2.selectROI('tracking', frame)
  bbox4 = cv2.selectROI('tracking', frame)
  return bbox1, bbox2, bbox3, bbox4

if __name__ == '__main__':
    import sys

    print(__doc__)

    try:
        fn = sys.argv[1]
    except:
        fn = 0
#    cap = video.create_capture(fn)
    cap = skvideo.io.vreader(fn)
    
    # def process_frame(frame, t0):
    #     # some intensive computation...
    #     frame = cv2.medianBlur(frame, 19)
    #     frame = cv2.medianBlur(frame, 19)
    #     return frame, t0

    def process_frame(frame, tracker, t0):
        ok, boxes = tracker.update(frame)
        xtl = int(min([b[0] for b in boxes]))
        ytl = int(min([b[1] for b in boxes]))
        xtr = int(max([b[0]+b[2] for b in boxes]))
        ybl = int(max([b[1]+b[3] for b in boxes]))
        width = int(xtr - xtl)
        height = int(ybl - ytl)
        xmin = int(min(xtl, xtr))
        xmax = int(max(xtl, xtr))
        ymin = int(min(ytl, ybl))
        ymax = int(max(ytl, ybl))

        for newbox in boxes:
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, (200,0,0), 3)
        po1 = (xtl, ytl)
        po2 = (xtr, ybl)
        cv2.rectangle(frame, po1, po2, (0,0,200), 5)
        cv2.imshow('tracking', frame)

        return frame, t0
    
    threadn = cv2.getNumberOfCPUs()
    pool = ThreadPool(processes = threadn)
    pending = deque()

    threaded_mode = True

    latency = StatValue()
    frame_interval = StatValue()
    last_frame_time = clock()

    tracker = cv2.MultiTracker_create()
    init_once = False

    count = 0
    bbox1 = bbox2 = bbox3 = bbox4 = None
    
    while True:
        while len(pending) > 0 and pending[0].ready():
            res, t0 = pending.popleft().get()
            latency.update(clock() - t0)
            draw_str(res, (20, 20), "threaded      :  " + str(threaded_mode))
            draw_str(res, (20, 40), "latency        :  %.1f ms" % (latency.value*1000))
            draw_str(res, (20, 60), "frame interval :  %.1f ms" % (frame_interval.value*1000))
            cv2.imshow('threaded video', res)
        if len(pending) < threadn:
            for frame in cap:
                #_, frame = cap.read()
                t = clock()
                frame_interval.update(t - last_frame_time)
                last_frame_time = t
                if bbox1 is None:
                    bbox1, bbox2, bbox3, bbox4 = read_bboxes(frame)
                    
                count += 1
                if count%100==0:
                    print('frame ',count)

                if not init_once:
                    ok1 = tracker.add(cv2.TrackerMIL_create(), frame, bbox1)
                    ok2 = tracker.add(cv2.TrackerMIL_create(), frame, bbox2)
                    ok3 = tracker.add(cv2.TrackerMIL_create(), frame, bbox3)
                    ok4 = tracker.add(cv2.TrackerMIL_create(), frame, bbox4)
                    init_once = True
                    
                if threaded_mode:
                    task = pool.apply_async(process_frame, (frame.copy(), tracker, t))
                else:
                    task = DummyTask(process_frame(frame, t))
                pending.append(task)
        ch = cv2.waitKey(1)
        if ch == ord(' '):
            threaded_mode = not threaded_mode
        if ch == 27:
            break

cv2.destroyAllWindows()
