import hashlib


class HashTable(object):
    def __init__(self):
        self.arr = [None for i in xrange(16)]
        self.m = 0
        self.n = len(self.arr)

    def insert(self, key, value):
        """
        Inserts a key-value pair after checking load factor.
        """
        # storage prep work
        self.check_load()
        # key, value prep work
        elem = HashElement(key, value)
        hashed = hashlib.md5(elem.key)
        bucket = int(hashed.hexdigest(), 16) % self.n
        # if nothing in bucket, then insert key, value pair
        if self.arr[bucket] is None:
            self.arr[bucket] = elem
            self.m += 1
        else:
            # check for element in linked list and replace
            # or insert it at end of linked list
            cur = self.arr[bucket]
            while cur.next is not None and cur.key != key:
                cur = cur.next
            if cur.key == key:
                cur.val = elem.val
            elif cur.next is None:
                cur.next = elem
                self.m += 1

    def lookup(self, key):
        scans = 1
        hashed = hashlib.md5(key)
        bucket = int(hashed.hexdigest(), 16) % self.n

        cur = self.arr[bucket]
        if cur is not None:
            while cur is not None:
                if cur.key == key:
                    return cur.val, scans
                else:
                    scans += 1
                    cur = cur.next

        raise KeyError(key + ' is not in the table')

    def get(self, key, default=None):
        try:
            return self.lookup(key)
        except KeyError:
            return default

    def delete(self, key):
        hashed = hashlib.md5(key)
        bucket = int(hashed.hexdigest(), 16) % self.n

        cur = self.arr[bucket]
        if cur is not None:
            # check to see if node in self.arr is the key to delete
            if cur.key == key:
                self.arr[bucket] = cur.next
                return
            # if not, then start traversal from next key
            # keep track of parent, which is node in bucket at first
            parent = cur
            cur = cur.next
            while cur is not None:
                if cur.key == key:
                    parent.next = cur.next
                else:
                    parent = cur
                    cur = cur.next
        self.m -= 1

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
            if item is None:
                continue
            else:
                cur = item
                while cur is not None:
                    self.insert(cur.key, cur.val)
                    cur = cur.next


class HashElement(object):
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None

    def __repr__(self):
        elems = []
        cur = self
        while cur is not None:
            elems.append('{}:{}'.format(cur.key, cur.val))
            cur = cur.next
        return ' -> '.join(elems)


if __name__ == '__main__':
    import string
    import random

    chars = string.ascii_letters + string.digits
    cur = HashTable()
    lst = []
    # test that insert successful for each key
    for i in xrange(1000):
        key = ''.join(random.sample(chars, 3))
        value = ''.join(random.sample(chars, 3))
        cur.insert(key, value)
        lst.append(key)

    # test that lookup successful for each inserted key
    scans = []
    for key in lst:
        val, scan = cur.lookup(key)
        scans.append(scan)

    print scans
    print sum(scans) / 1000.0

    # test that key does not exist in table
    key = ''.join(random.sample(chars, 4))
    assert cur.get(key) is None

    for key in lst:
        cur.delete(key)
        assert cur.get(key) is None
