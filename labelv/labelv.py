#! /usr/bin/env python
from math import *
import numpy as np
import cv2
import sys
import os
import argparse
import time
import skvideo.io
import skvideo.datasets

def read_bboxes(image):
  # choose the corners (or edges) of the tracking bbox
  bbox1 = cv2.selectROI('tracking', image)
  bbox2 = cv2.selectROI('tracking', image)
  bbox3 = cv2.selectROI('tracking', image)
  bbox4 = cv2.selectROI('tracking', image)
  return bbox1, bbox2, bbox3, bbox4

def labelv():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-l", "--label", default='label', help="label of the object")
    ap.add_argument("-fp", "--frame path", default='Images', help="directory to save frames in")
    ap.add_argument("-lp", "--label path", default='labels/label.csv', help="file to append labels to")
    ap.add_argument("-m", "--mode", default='w', type=str,help="mode to open the labels file in, a for append, w for write")
    ap.add_argument("-fr", "--frame rate", type=int, default=1, help="rate to save frames and labels at. Every 1/fr is saved")
    ap.add_argument("-fn", "--file name", default="frame", help="base name for each frame (imporant to set or frames from the previous videos will be replaced")
    args = vars(ap.parse_args())

    class_name = args['label']

    print("frames are saved in %s/%sX.jpg"%(args['frame path'],args['file name']))
    frame_path = args['frame path']

    print("labels are saved in %s"%args["label path"])
    flabels = open("%s"%args["label path"], args["mode"])
    if args['mode'] == 'w':
      flabels.write("filename,width,height,class,xmin,ymin,xmax,ymax\n")

    camera = skvideo.io.vreader(args['video'])
    fr = args['frame rate']

    cv2.namedWindow("tracking")
    tracker = cv2.MultiTracker_create()
    init_once = False

    count = 0
    bbox1 = bbox2 = bbox3 = bbox4 = None

    for image in camera:
      if bbox1 is None:
        bbox1, bbox2, bbox3, bbox4 = read_bboxes(image)

      count += 1
      if count%fr==0:
        # save the frame
        cv2.imwrite(os.path.join(frame_path, "%s%d.jpg" %(args['file name'], count)), image)     # save frame as JPEG file

      if not init_once:
        ok1 = tracker.add(cv2.TrackerMIL_create(), image, bbox1)
        ok2 = tracker.add(cv2.TrackerMIL_create(), image, bbox2)
        ok3 = tracker.add(cv2.TrackerMIL_create(), image, bbox3)
        ok4 = tracker.add(cv2.TrackerMIL_create(), image, bbox4)
        init_once = True

      ok, boxes = tracker.update(image)
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
      if count%fr==0:
        # write the box to the labels
        flabels.write('%s%d,%d,%d,%s,%d,%d,%d,%d\n'%(args['file name'], count, width, height, class_name, xmin, ymin, xmax, ymax))

      for newbox in boxes:
        p1 = (int(newbox[0]), int(newbox[1]))
        p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
        cv2.rectangle(image, p1, p2, (200,0,0), 3)
      po1 = (xtl, ytl)
      po2 = (xtr, ybl)
      cv2.rectangle(image, po1, po2, (0,0,200), 5)
      cv2.putText(image, "Frame: " + str(count) + " Tracking " + class_name, (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (250,0,0), 2);
      cv2.imshow('tracking', image)

      # respond to keyboard interactions
      k = cv2.waitKey(1) & 0xFF
      if k == 27 : # ESC pressed
        cv2.destroyAllWindows()
        flabels.close()
        break 
      elif k == 32: # SPACE pressed
        new_class_name = raw_input('New label: ')
        if new_class_name:
          class_name = new_class_name
        tracker = cv2.MultiTracker_create()
        init_once = False
        bbox1, bbox2, bbox3, bbox4 = read_bboxes(image)

    # do a bit of cleanup
    cv2.destroyAllWindows()
    flabels.close()
