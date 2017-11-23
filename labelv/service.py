from flask import Flask, Response, request, abort
import uuid
import json
import ra
import cv2
import skvideo.io
import os.path
import pkg_resources
import hashlib
import copy

app = Flask(__name__, static_folder=None)

class Tracker(object):
    def __init__(self, video, frame, labels, key):
        self.tracker = cv2.MultiTracker_create()
        self.video_accessor = video_store(video_path(video))
        self.frame = frame
        self.labels = labels
        self.initialized = False
        print "Starting new tracker for video %s based on keyframe %s" % (video, frame)

    def __iter__(self):
        return self

    def flatten_labels(self):
        res = {}
        def flatten(item, path=()):
            if item['type'] == 'Label':
                res[path] = item['args']
            elif item['type'] == 'Group':
                for idx, child in enumerate(item['args']['children']):
                    itempath = path + (idx,)
                    flatten(child, itempath)
            else:
                raise Exception('Unknown node type: %s' % item['type'])
        flatten(self.labels)
        return res

    def unflatten_labels(self, labels):
        res = copy.deepcopy(self.labels)
        def replace(path, label, node):
            if len(path) == 0:
                node['args'] = label
            else:
                replace(path[1:], label, node['args']['children'][path[0]])
        def update_group_bboxes(node):
            if node['type'] == 'Label':
                pass
            elif node['type'] == 'Group':
                for child in node['args']['children']:
                    update_group_bboxes(child)
                bboxes = [child['args']['bbox']
                          for child in node['args']['children']]
                node['args']['bbox'] = [
                    min(bbox[0] for bbox in bboxes),
                    min(bbox[1] for bbox in bboxes),
                    max(bbox[0] + bbox[2] for bbox in bboxes),
                    max(bbox[1] + bbox[3] for bbox in bboxes)
                ]            
        for path, label in labels.iteritems():
            replace(path, label, res)
        update_group_bboxes(res)
        return res
            
    def next(self):
        image = self.video_accessor[self.frame]

        if not len(self.flatten_labels()):
            import pdb
            pdb.set_trace()
        paths, labels = zip(*self.flatten_labels().items())
        
        if not self.initialized:
            for label in labels:
                if not self.tracker.add(cv2.TrackerMIL_create(), image, tuple(label['bbox'])):
                    raise Exception("Unable to add tracker bbox")
            self.initialized = True
                
        ok, boxes = self.tracker.update(image)
        self.frame += 1
        if not ok:
            raise Exception("Unable to update tracker with current frame")

        res = {}
        for path, label, bbox in zip(paths, labels, boxes.tolist()):
            label = dict(label)
            label['bbox'] = bbox
            res[path] = label
        
        return self.unflatten_labels(res)

class TrackerCache(object):
    def __init__(self, video, frame, labels, key):
        self.video = video
        self.frame = frame
        self.labels = labels
        self.key = key
        self.basepath = os.path.join('upload', 'tracker', self.video, str(self.frame), self.key)

    def frame_path(self, frame):
        return os.path.join(self.basepath, "%s.json" % frame)
        
    def __contains__(self, frame):
        path = self.frame_path(frame)
        exists = os.path.exists(path)
        if not exists:
            print "Cache miss for frame %s (%s)" % (frame, path)
        return os.path.exists(self.frame_path(frame))
    
    def __getitem__(self, frame):
        with open(self.frame_path(frame)) as f:
            return json.load(f)
    
    def __setitem__(self, frame, labels):
        path = self.frame_path(frame)
        ensuredirs(os.path.split(path)[0])
        with open(path, "w") as f:
            json.dump(labels, f)
    
video_store = ra.Store(skvideo.io.vreader)
tracker_store = ra.Store(Tracker, TrackerCache)


def ensuredirs(pth):
    if os.path.exists(pth):
        return
    os.makedirs(pth)


def video_path(id):
    assert '/' not in id
    return os.path.join('upload', 'video', id.encode('utf-8'))

def session_path(videoid, sessionid):
    assert '/' not in videoid
    assert '/' not in sessionid
    return os.path.join('upload', 'session', ("%s-%s" % (videoid, sessionid)).encode('utf-8'))

ensuredirs("upload/video")
ensuredirs("upload/tracker")
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

@app.route('/video/<video>/session/<session>/metadata', methods=['GET'])
def get_metadata(video, session):
    metadata = skvideo.io.ffprobe(video_path(video))
    metadata['keyframes'] = []

    session = session_path(video, session)
    if os.path.exists(session):
        with open(session) as f:
            metadata['keyframes'] = [int(key) for key in json.load(f)['keyframes'].iterkeys()]

    return Response(json.dumps(metadata), mimetype='text/json')

@app.route('/video/<video>/session/<session>/bboxes/<frame>', methods=['GET'])
def get_frame_bboxes(video, session, frame):
    assert '/' not in video
    assert '/' not in session
    
    res = {"labels": [], 'keyframe': -1}

    session = session_path(video, session)
    if os.path.exists(session):
        with open(session) as f:
            data = json.load(f)

        frame = int(frame)

        keyframes = sorted(keyframe
                           for keyframe in (int(key)
                                            for key in data['keyframes'].iterkeys())
                           if keyframe <= frame)

        if keyframes:
            res['keyframe'] = keyframe = keyframes[-1]
            frame_data = data['keyframes'][str(keyframe)]            
            res['labels'] = tracker_store(video, keyframe, frame_data['data']['labels'], frame_data['key'])[frame]

    return Response(json.dumps(res), mimetype='text/json')

@app.route('/video/<video>/session/<session>/bboxes/<frame>', methods=['POST'])
def set_frame_bboxes(video, session, frame):
    session = session_path(video, session)
    data = {'keyframes': {}}
    if os.path.exists(session):
        with open(session) as f:
            data = json.load(f)

    frame_data = request.get_json()

    if frame_data and frame_data["labels"] and frame_data["labels"]['args'] and frame_data["labels"]['args']['children']:
        frame_data = {'data': frame_data}
        frame_data['key'] = hashlib.sha1(json.dumps(frame_data['data'], sort_keys=True)).hexdigest()
        data['keyframes'][frame] = frame_data
    else:
        if frame in data['keyframes']:
            del data['keyframes'][frame]
        
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
