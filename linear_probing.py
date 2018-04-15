import hashlib


class HashElement(object):
    def __init__(self, key, value):
        self.key = key
        self.val = value
        self.tombstone = False


class HashTable(object):
    def __init__(self):
        self.arr = [None for i in xrange(16)]
        self.m = 0
        self.n = len(self.arr)

    def _hash_key(self, key):
        hashed = hashlib.md5(key)
        bucket = int(hashed.hexdigest(), 16) % self.n
        return bucket

    def insert(self, key, value):
        self.check_load()

        elem = HashElement(key, value)
        bucket = self._hash_key(elem.key)

        while True:
            if self.arr[bucket] is None or self.arr[bucket].tombstone:
                self.arr[bucket] = elem
                self.m += 1
                return
            # increment bucket
            bucket = (bucket + 1) % self.n
            # quadratic - i += 1, bucket = (bucket + i ** 2) % self.n

    def lookup(self, key):
        bucket = self._hash_key(key)

        # then check all buckets after, until we come back to the original bucket
        while True:
            if self.arr[bucket] is None:
                raise KeyError(key + ' is not in the table')
            if self.arr[bucket].key == key and not self.arr[bucket].tombstone:
                return self.arr[bucket].val
            bucket = (bucket + 1) % self.n
            # quadratic - i += 1, bucket = (bucket + i ** 2) % self.n

    def get(self, key, default=None):
        try:
            return self.lookup(key)
        except KeyError:
            return default

    def delete(self, key):
        bucket = self._hash_key(key)

        while True:
            if self.arr[bucket] is None:
                return
            if self.arr[bucket].key == key and not self.arr[bucket].tombstone:
                self.arr[bucket].tombstone = True
                self.m -= 1
            bucket = (bucket + 1) % self.n
            # quadratic - i += 1, bucket = (bucket + i ** 2) % self.n

    def check_load(self):
        load_factor = self.m / float(self.n)
        if load_factor >= 0.9:
            self.resize()

    def resize(self):
        old = self.arr
        self.n *= 2
        self.m = 0
        self.arr = [None for i in xrange(self.n)]
        for item in old:
            if item is not None:
                self.insert(item.key, item.val)


if __name__ == '__main__':
    import random
    import string

    table = HashTable()
    lst = []
    chars = string.ascii_letters + string.digits

    for i in xrange(1000):
        key = ''.join(random.sample(chars, 3))
        value = ''.join(random.sample(chars, 3))
        table.insert(key, value)
        lst.append(key)

    for key in lst:
        table.lookup(key)

    key = ''.join(random.sample(chars, 4))
    assert table.get(key) is None

    for key in lst:
        table.delete(key)
        assert table.get(key) is None

