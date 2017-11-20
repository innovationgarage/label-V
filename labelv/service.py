from flask import Flask, Response, request, abort
import uuid
import json
import ra
import cv2
import skvideo.io
import os.path
import pkg_resources

app = Flask(__name__, static_folder=None)

class Tracker(object):
    def __init__(self, video, frame, bboxes):
        self.tracker = cv2.MultiTracker_create()
        self.video_accessor = video_store(video)
        self.frame = frame
        self.bboxes = bboxes
        self.initialized = False

    def __iter__(self):
        return self
        
    def next(self):
        image = self.video_accessor[self.frame]

        if not self.initialized:
            for bbox in self.bboxes:
                if not self.tracker.add(cv2.TrackerMIL_create(), image, tuple(bbox)):
                    raise Exception("Unable to add tracker bbox")
            self.initialized = True
                
        ok, boxes = self.tracker.update(image)
        self.frame += 1
        if not ok:
            raise Exception("Unable to update tracker with current frame")

        return boxes.tolist()

video_store = ra.Store(skvideo.io.vreader)
tracker_store = ra.Store(Tracker)


def ensuredirs(pth):
    if os.path.exists(pth):
        return
    os.makedirs(pth)


def video_path(id):
    assert '/' not in id
    return os.path.join('upload', 'video', id.encode('utf-8'))

def session_path(id):
    assert '/' not in id
    return os.path.join('upload', 'session', id.encode('utf-8'))

ensuredirs("upload/video")
ensuredirs("upload/session")


@app.route('/video', methods=['PUT', 'POST'])
def upload():
    res = {}
    if 'file' in request.files:
        file = request.files['file']
        ext = os.path.splitext(file.filename)[-1]
        assert "/" not in ext
        if file.filename != '':
            res['id'] = str(uuid.uuid4()) + ext
            file.save(video_path(res['id']))
    return Response(json.dumps(res), mimetype='text/json')
            
@app.route('/video/<video>/image/<frame>', methods=['GET'])
def get_frame_image(video, frame):
    frame_content = video_store(video_path(video))[int(frame)]
    retval, frame_img = cv2.imencode(".png", frame_content)
    return Response(frame_img.tobytes(), mimetype='image/png')
    
@app.route('/video/<video>/session/<session>/bboxes/<frame>', methods=['GET'])
def get_frame_bboxes(video, session, frame):
    res = {"bboxes": []}

    session = session_path(session)
    if os.path.exists(session):
        with open(session) as f:
            data = json.load(f)

        frame = int(frame)

        keyframes = sorted(keyframe
                           for keyframe in (int(key)
                                            for key in data['keyframes'].iterkeys())
                           if keyframe < frame)

        if keyframes:
            keyframe = keyframes[-1]
            res['bboxes'] = tracker_store(video_path(video), keyframe, data['keyframes'][str(keyframe)]['bboxes'])[frame]

    return Response(json.dumps(res), mimetype='text/json')

@app.route('/video/<video>/session/<session>/bboxes/<frame>', methods=['POST'])
def set_frame_bboxes(video, session, frame):
    session = session_path(session)
    data = {'keyframes': {}}
    if os.path.exists(session):
        with open(session) as f:
            data = json.load(f)

    bboxes = request.get_json()

    if not bboxes:
        if frame in data['keyframes']:
            data['keyframes'].remove(frame)
    else:
        data['keyframes'][frame] = {'bboxes': bboxes, 'computed': {}}
    
    with open(session, "w") as f:
        json.dump(data, f)

    return Response(json.dumps({}), mimetype='text/json')

@app.route('/')
@app.route('/<path:path>')
def get_resource(path = ''):  # pragma: no cover
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    try:
        content = pkg_resources.resource_string('labelv', os.path.join("static", path))
    except IOError:
        try:
            content = pkg_resources.resource_string('labelv', os.path.join("static", path, "index.html"))
        except IOError:
            abort(404)
    return Response(content, mimetype=mimetype)
        
def main():
    app.run(host='localhost', port=4711)
