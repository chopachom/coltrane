# -*- coding: utf-8 -*-
import copy
import sys

__author__ = 'pshkitin'

import time
from coltrane.tests.mongo.utils import save, storage, average, get, big_doc, small_doc, document

print 'test_get'

doc = copy.deepcopy(document)

def test_get(key):
    start = time.time()
    d = get(key)
    duration = time.time() - start
    friq = 1.0 / duration
    assert d is not None

    return duration, friq

numbers = [100, 1000, 10000, 100000, 1000000, 4000000]
for num in numbers:
    res = []
    storage.entities.drop()
    for n in range(num):
        doc['_key'] = 'key_%d' % n
        save(doc)
    print 'Doc amount %d' % storage.entities.count()
    for i in range(3):
        res.append(test_get('key_%d' % (num/2)))
    duration, friq = tuple([average(vals) for vals in zip(*res)])
    print 'Test get document by id. Documents amount: %d; Duration: %f; Friquency: %f' %\
          (num, duration, friq)
