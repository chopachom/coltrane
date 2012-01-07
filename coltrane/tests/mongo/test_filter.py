# -*- coding: utf-8 -*-
import sys

__author__ = 'pshkitin'

import copy
import time
from coltrane.tests.mongo.utils import save, storage, average, find, document

print 'test_filter'

doc = copy.deepcopy(document)

def test_find(filter):
    print filter
    start = time.time()
    d = find(filter)
    duration = time.time() - start
    friq = 1.0 / duration

    assert d is not None
    assert len(d) == 79

    return duration, friq

numbers = [100, 1000, 10000, 100000, 1000000, 4000000]

for num in numbers:
    res = []
    storage.entities.drop()
    for n in range(num):
        d = copy.deepcopy(doc)
        d['a']['c'] = {'d':[1,2,3], 'e':n}
        save(d)
    print 'Doc amount %d' % storage.entities.count()
    for i in range(3):
        res.append(test_find({'$and':[{'a.c.e':{'$gt': num/2 - 40}},
                {'a.c.e':{'$lt': num/2 + 40}}]}))
    duration, friq = tuple([average(vals) for vals in zip(*res)])
    print 'Test filter documents. Documents amount: %d; Duration: %f; Friquency: %f' %\
          (num, duration, friq)