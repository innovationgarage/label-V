import threading
import logging
import time
import random
import Queue
import sys
import skvideo.io
import skvideo.datasets
import cv2
import os
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

#BUF_SIZE = 10
#q = Queue.PriorityQueue(BUF_SIZE)
state = []
stateLock = threading.Lock()

class MyTracker(object):
    def __init__(self, frame):
        # Set up tracker
        # tracker_types : BOOSTING, MIL, KCF, TLD, MEDIANFLOW, GOTURN
        self.tracker = cv2.TrackerKCF_create()
        self.bbox = (287, 23, 86, 320)
#        self.bbox = cv2.selectROI(frame, False)
        self.status = self.tracker.init(frame, self.bbox)

    def update_tracker(self, frame):
        self.status, self.bbox = self.tracker.update(frame)

    def draw_bbox(self, frame):
        p1 = (int(self.bbox[0]), int(self.bbox[1]))
        p2 = (int(self.bbox[0] + self.bbox[2]), int(self.bbox[1] + self.bbox[3]))
        cv2.rectangle(frame, p1, p2, (0,255,0), 2, 1)

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.video = iter(enumerate(skvideo.io.vreader(self.target)))
        
    def run(self):
        while True:
            if not q.full():
                try:
                    frame = self.video.next()
                    if frame[0]==0:
                        t1 = MyTracker(frame[1])

#                    q.put((frame[0], frame[1], t1))
                    state.append((t1, frame, False))

                    logging.debug(
                        'Putting frame no. ' + str(frame[0]) #frame number
                        #+ ' : ' + str(q.qsize()) + ' frames in queue'
                    )
                except:
                    break
        return

class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        return

    @contextlib.contextmanager
    def getState():
        def getFirstState():
            for s in state:
                if s[2]:
                    return s
                return None
        with stateLock:
            s = getState()
            if s is None:
                return
            s[2] = False
        yield s
        with stateLock:
            s[1] += 1
            s[2] = True

    def run(self):
        with self.getState() as s:
            processFrame(s)
            
    def processFrame(s):
        t1, frame, False = s
        frame_nr, frame_data = frame
        logging.debug(
            'Getting frame no. ' + str(frame_nr)
            #+ ' : ' + str(q.qsize()) + ' frame in queue'
        )
                logging.debug(os.path.join('out', 'frame%s_%s'%(frame_nr, self.name)))
                t1.update_tracker(frame_data)
                logging.debug('tracer status: %s'%t1.status)
                if t1.status:
                    t1.draw_bbox(frame_data)
                    cv2.imwrite(os.path.join('out', 'frame%s_%s.png'%(frame_nr, self.name)), frame_data)
#                q.task_done()
                logging.debug(
                    'Finnish processing frame no. ' + str(frame_nr)
                    #+ ' : ' + str(q.qsize()) + ' frame in queue'
                )

#     def run(self):
#         while True:
#             if not q.empty():
#                 frame_nr, frame_data, t1 = q.get()
#                 logging.debug(
#                     'Getting frame no. ' + str(frame_nr)
#                     #+ ' : ' + str(q.qsize()) + ' frame in queue'
#                 )
#                 logging.debug(os.path.join('out', 'frame%s_%s'%(frame_nr, self.name)))
#                 t1.update_tracker(frame_data)
#                 logging.debug('tracer status: %s'%t1.status)
#                 if t1.status:
#                     t1.draw_bbox(frame_data)
#                     cv2.imwrite(os.path.join('out', 'frame%s_%s.png'%(frame_nr, self.name)), frame_data)
# #                q.task_done()
#                 logging.debug(
#                     'Finnish processing frame no. ' + str(frame_nr)
#                     #+ ' : ' + str(q.qsize()) + ' frame in queue'
#                 )


if __name__ == '__main__':
                    
    p = ProducerThread(name='producer', target=str(sys.argv[1]))
    c1 = ConsumerThread(name='consumer1')
    c2 = ConsumerThread(name='consumer2')

    p.start()
    c1.start()
    c2.start()

    # Wait for all threads to complete
    for t in [p, c1, c2]:
        t.join()
    print "Exiting Main Thread"
