#! /usr/bin/env python

from math import *
import numpy as np
import cv2
import sys
import os
import argparse
import time

def read_bboxes(image):
	# choose the corners (or edges) of the tracking bbox
	bbox1 = cv2.selectROI('tracking', image)
	bbox2 = cv2.selectROI('tracking', image)
	bbox3 = cv2.selectROI('tracking', image)
	bbox4 = cv2.selectROI('tracking', image)
	return bbox1, bbox2, bbox3, bbox4

if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument("-v", "--video", help="path to the video file")
  ap.add_argument("-l", "--label", help="label of the object")
  ap.add_argument("-fp", "--frame path", help="directory to save frames in")
  ap.add_argument("-lp", "--label path", help="file to append labels to")
  ap.add_argument("-fr", "--frame rate", type=int, help="rate to save frames and labels at. Every 1/fr is saved")
  ap.add_argument("-fn", "--file name", default="frame", help="base name for each frame (imporant to set or frames from the previous videos will be replaced")
  ap.add_argument("-o", "--output", default='output.avi', help="path to the output video")        
  args = vars(ap.parse_args())

  if args.get('label', None) is None:
    class_name = 'label'
  else:
    class_name = args['label']

  if args.get('frame path', None) is None:
    print("frames are saved in Images/%sX.jpg"%args['file name'])
    frame_path = 'Images'
  else:
    print("frames are saved in %s/%sX.jpg"%(args['frame path'],args['file name']))
    frame_path = args['frame path']

  if args.get('label path', None) is None: 
    print("labels are saved in labels/label.csv")
    flabels = open("labels/label.csv", 'w')
    flabels.write("filename,width,height,class,xmin,ymin,xmax,ymax\n")
  else:
    print("labels are saved in %s"%args["label path"])
    flabels = open("%s"%args["label path"], 'a')

  if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
  else:
    camera = cv2.VideoCapture(args['video'])

  if args.get('frame rate', None) is None:        
    fr = 1
  else:
    fr = args['frame rate']

  cv2.namedWindow("tracking")
  tracker = cv2.MultiTracker_create()
  init_once = False

  count = 0
  ok, image = camera.read()
  if not ok:
    print('Failed to read video')
    exit()

  bbox1, bbox2, bbox3, bbox4 = read_bboxes(image)

  # initialize the FourCC, video writer, dimensions of the frame, and
  # zeros array
  fourcc = cv2.VideoWriter_fourcc(*'MJPG')
  writer = None
  (h, w) = (None, None)
  zeros = None

  while camera.isOpened():
    ok, image = camera.read()
    if not ok:
      print 'no image to read'
      break

    if ok:
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

    # Save video
    if writer is None:
      (h, w) = image.shape[:2]
      writer = cv2.VideoWriter(args['output'], fourcc, 20, (w, h), True)
      zeros = np.zeros((h, w), dtype="uint8")

    output = np.zeros((h, w, 3), dtype="uint8")
    output = image

    # write the output frame to file
    writer.write(output)

    # respond to keyboard interactions
    k = cv2.waitKey(1) & 0xFF
    if k == 27 : # ESC pressed
      cv2.destroyAllWindows()
      writer.release()
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
writer.release()
flabels.close()
