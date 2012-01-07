# -*- coding: utf-8 -*-
import sys

__author__ = 'pshkitin'

import copy
import time
from coltrane.tests.mongo.utils import save, storage, average, big_doc, find, small_doc, update, document

print 'test_update'

doc = copy.deepcopy(document)

def test_update(filter, doc_update):
    print filter
    start = time.time()
    update(filter, doc_update)
    duration = time.time() - start
    friq = 1.0 / duration

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
        filt = {'$and':[{'a.c.e':{'$gt': num/2 - 40}},
                {'a.c.e':{'$lt': num/2 + 40}}]}
        d = {'a.b':{'name':'Pasha', 'age':num}}
        res.append(test_update(filt, d))
    duration, friq = tuple([average(vals) for vals in zip(*res)])
    print 'Test update document by filter. Documents amount: %d; Duration: %f; Friquency: %f' %\
          (num, duration, friq)
