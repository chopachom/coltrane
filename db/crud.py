__author__ = 'pshkitin'


books = { 'books': [
        {'key':1, 'title': 'Title1', 'author': 'Nikita Shmakov'},
        {'key':2, 'title': 'Title2', 'author': 'Nikita Shmakov'}
]}

counterId = 2

def init_app(app):
    pass

class Crud(object):

    def get(self, bucket, key=None):
        if key is None:
            return books[bucket]
        else:
            for obj in books[bucket]:
                if obj['key'] == int(key): return obj

    def save(self, bucket, obj, key=None):
        books[bucket].append(obj)
        global counterId
        counterId += 1
        obj['id'] = counterId
        return counterId

    def delete(self, bucket, key):
        l = books[bucket]
        l2 = filter((lambda obj: True if obj['key'] == key else False), l)
        if len(l2):
            l.remove(l2[0])
            return 0
        else:
            return 1

    def update(self, bucket, key, obj):
        l = books[bucket]
        l2 = filter((lambda obj: True if obj['key'] == key else False), l)
        if len(l2):
            l.remove(l2[0])
            l.append(obj)
            return 0
        else:
            return 1

crud = Crud()