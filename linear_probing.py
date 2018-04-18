import hashlib


class HashElement(object):
    def __init__(self, key, value):
        self.key = key
        self.val = value
        self.tombstone = False


class HashTable(object):
    def __init__(self, probe=1):
        self.arr = [None for i in xrange(16)]
        self.m = 0
        self.n = len(self.arr)
        self.probe = probe

    def _hash_key(self, key):
        hashed = hashlib.md5(key)
        bucket = int(hashed.hexdigest(), 16) % self.n
        return bucket

    def insert(self, key, value):
        self.check_load()

        elem = HashElement(key, value)
        bucket = self._hash_key(elem.key)
        cur = bucket
        base = 1

        while True:
            if self.arr[cur] is None or self.arr[cur].tombstone:
                self.arr[cur] = elem
                self.m += 1
                return
            # increment bucket
            cur = int(bucket + base / 2.0 +
                      (base ** self.probe) / 2.0) % self.n
            base += 1

    def lookup(self, key):
        bucket = self._hash_key(key)
        cur = bucket
        base = 1

        while True:
            if self.arr[cur] is None:
                raise KeyError(key + ' is not in the table')
            if self.arr[cur].key == key and not self.arr[cur].tombstone:
                return self.arr[cur].val
            cur = int(bucket + base / 2.0 +
                      (base ** self.probe) / 2.0) % self.n
            # naive implementation causes loop shown in note below
            # cur = (bucket + base ** self.probe) % self.n
            base += 1

    def get(self, key, default=None):
        try:
            return self.lookup(key)
        except KeyError:
            return default

    def delete(self, key):
        bucket = self._hash_key(key)
        cur = bucket
        base = 1

        while True:
            if self.arr[cur] is None:
                return
            if self.arr[cur].key == key and not self.arr[cur].tombstone:
                self.arr[cur].tombstone = True
                self.m -= 1
            cur = int(bucket + base / 2.0 +
                      (base ** self.probe) / 2.0) % self.n
            base += 1

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

    for probe in (1, 2, 3):
        table = HashTable(probe)
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
