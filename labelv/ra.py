""" Example usage:

    >>> import labelv.ra
    >>> xrange_store = labelv.ra.Store(xrange)
    >>> my_range = xrange_store(0, 10000, 2)
    >>> my_range[0]
    0
    >>> my_range[1]
    2
    >>> my_range[2]
    4
    >>> my_range[1]
    2
    >>> my_range[4999]
    9998
    >>> my_range[5000]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "labelv/ra.py", line 39, in __getitem__
        raise KeyError(idx)
    KeyError: 5000
"""

import json

class Iterator(object):
    def __init__(self, itercls, args):
        self.iterator = iter(itercls(*args.args, **args.kw))
        self.idx = 0
        
    def next(self):
        try:
            return self.iterator.next()
        finally:
            self.idx += 1

class Accessor(object):
    def __init__(self, itercls, cachecls, args):
        self.itercls = itercls
        self.cache = None
        if cachecls:
            self.cache = cachecls(*args.args, **args.kw)
        self.args = args
        self.iterators = []

    def __getitem__(self, idx):
        if self.cache and idx in self.cache:
            return self.cache[idx]
        self.iterators.sort(lambda a, b: cmp(a.idx, b.idx))
        matching = [iterator
                    for iterator in self.iterators
                    if iterator.idx <= idx]
        if not matching:
            iterator = Iterator(self.itercls, self.args)
            self.iterators.append(iterator)
        else:
            iterator = matching[-1]
        try:
            while iterator.idx < idx:
                iterator.next()
            return iterator.next()
        except StopIteration:
            self.iterators.remove(iterator)
            raise KeyError(idx)
    
class Args(object):
    __slots__ = ("args", "kw", "repr", "hash")
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw
        self.repr = json.dumps((self.args, self.kw), sort_keys=True)
        self.hash = hash(self.repr)
    def __hash__(self):
        return self.hash
    def __cmp__(self, other):
        return cmp(self.repr, other.repr)

class Store(object):
    def __init__(self, itercls, cachecls=None):
        self.itercls = itercls
        self.cachecls = cachecls
        self.accessors = {}

    def __call__(self, *args, **kw):
        args = Args(*args, **kw)
        if args not in self.accessors:
            self.accessors[args] = Accessor(self.itercls, self.cachecls, args)
        return self.accessors[args]

