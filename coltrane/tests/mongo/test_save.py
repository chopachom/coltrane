# -*- coding: utf-8 -*-
__author__ = 'pshkitin'

import copy
import time
from coltrane.tests.mongo.utils import save, storage, average, document

print 'test_save'

doc = copy.deepcopy(document)

def test_save(number):
    """
        Сохранение JSON документа много раз.
        Документ: doc = {'Key1dsfdsf': {'Key2sdfsdfsdf':[1,2,3], 'Key3dfgfdgfdg':'New Year'}}
    """
    res = []
    for i in xrange(number):
        d = copy.deepcopy(doc)
        start = time.time()
        save(d)
        duration = time.time() - start
        friq = 1.0 / duration
        res.append((duration, friq))
    print 'Doc amount %d' % storage.entities.count()
    duration, friq = tuple([average(vals) for vals in zip(*res)])
    return duration, friq

number = [100, 1000, 10000, 100000, 1000000, 4000000]

for num in number:
    res = []
    for i in range(3):
        storage.entities.remove()
        res.append(test_save(num))
    duration, friq = tuple([average(vals) for vals in zip(*res)])
    print 'Save document. Documents amount: %d; Duration: %f; Friquency: %f' %\
          (num, duration, friq)