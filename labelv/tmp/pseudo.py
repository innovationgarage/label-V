import contextlib
import threading

state = [('tracker1', (0, 'frame1'), False), ('tracker2', (0, 'frame2'), False)]
stateLock = threading.Lock()

@contextlib.contextmanager
def getState():
    def getFirstState():
        for s in state:
            if s[2]:
                print('s', s)
                return s
            print('None')
            return None
    with stateLock:
        s = getState()
        if s is None:
            print('s is None')
            return
        s[2] = False
    print('yielding s', s)
    yield s
    with stateLock:
        s[1] += 1
        s[2] = True

def processFrame(frame):
    print(frame)

with getState() as s:
    processFrame(s)

def workerThreadRunFunction():
    with getState() as s:
        processFrame(s)

