import csv
import json
import cv2
import skvideo.io
import ra
import service
import sys
import os

video_id = sys.argv[1]
session = sys.argv[2]

video = service.video_store(service.video_path(video_id))

def flatten_frame_data(data):
    if data['type'] == 'Group':
        for child in data['args']['children']:
            for item in flatten_frame_data(child):
                yield item
    else:
        yield data
        

imagedir = "%s-%s" % (video_id, session)
os.mkdir(imagedir)

with open("%s/frames.csv" % imagedir, "w") as outf:
    outf = csv.DictWriter(outf, ["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"])
    outf.writeheader()

    with open("upload/session/%s-%s" % (video_id, session)) as inf:
        session_data = json.load(inf)

    keyframes = [int(i) for i in session_data['keyframes'].keys()]
    keyframes.sort()
    
    for keyframe in keyframes:
        key = session_data['keyframes'][str(keyframe)]['key']
        trackerdir = "upload/tracker/%s/%s/%s" % (video_id, keyframe, key)
        frames = [int(i.split(".json")[0]) for i in os.listdir(trackerdir)]
        frames.sort()
        for frame in frames:
            with open("%s/%s.json" % (trackerdir, frame)) as inf:
                frame_data = flatten_frame_data(json.load(inf))

            frame_image = "frame_%s" % (keyframe + frame)
            img = video[keyframe + frame]
            cv2.imwrite("%s/%s.jpg" % (imagedir, frame_image), img)

            for item in frame_data:
                outf.writerow({
                    "filename": frame_image,
                    "width": img.shape[1],
                    "height": img.shape[0],
                    "class":item['args']['title'],
                    "xmin": int(item['args']['bbox'][0]),
                    "ymin": int(item['args']['bbox'][1]),
                    "xmax": int(item['args']['bbox'][0]+item['args']['bbox'][2]),
                    "ymax": int(item['args']['bbox'][1]+item['args']['bbox'][3])
                })
