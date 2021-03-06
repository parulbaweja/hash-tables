import hashlib


class HashElement(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.tombstone = False
        self.hashed = int(hashlib.md5(key).hexdigest(), 16)

    def __repr__(self):
        return '{}:{}'.format(self.key, self.value)


class HashTable(object):
    def __init__(self):
        self.arr = [None for i in xrange(16)]
        self.m = 0
        self.n = len(self.arr)

    def _get_bucket_idx(self, hashed):
        return hashed % self.n

    def _get_bucket_dist(self, bucket, elem):
        return (bucket - self._get_bucket_idx(elem.hashed)) % self.n

    def insert(self, key, value):
        self.check_load()

        elem = HashElement(key, value)
        bucket = self._get_bucket_idx(elem.hashed)

        while True:
            # if bucket is open, insert element there
            if self.arr[bucket] is None:
                self.arr[bucket] = elem
                self.m += 1
                return
            else:
                # if bucket is not open, compare against current item
                cur = self.arr[bucket]
                cur_dist = self._get_bucket_dist(bucket, cur)
                elem_dist = self._get_bucket_dist(bucket, elem)

                # if dist is same, then they belong to the same bucket
                # so check to see if keys are same and replace the value
                if elem_dist == cur_dist:
                    if elem.key == cur.key:
                        self.arr[bucket].value = elem.value
                        return
                    if cur.tombstone:
                        self.arr[bucket] = elem
                        self.m += 1
                        return
                # if dist between elem and bucket is bigger, insert elem
                if elem_dist > cur_dist:
                    # if keys are same, update the values, do not increment m
                    # if elem.key == cur.key:
                    #     cur.value = elem.value
                    #     return
                    # otherwise, swap items and continue to insert
                    self.arr[bucket] = elem
                    elem = cur

                # increment bucket to check next bucket in next iteration
                bucket = (bucket + 1) % self.n

    def lookup(self, key):
        elem = HashElement(key, value=None)
        bucket = self._get_bucket_idx(elem.hashed)
        scans = 1

        while True:
            if self.arr[bucket] is None:
                raise KeyError(key + 'is not in table')

            cur = self.arr[bucket]
            cur_dist = self._get_bucket_dist(bucket, cur)
            elem_dist = self._get_bucket_dist(bucket, elem)

            if elem_dist > cur_dist:
                # we've moved on to a cur that has a bucket larger
                # than our elem bucket
                # for example we hit cur_bucket = 1 while searching for
                # elem_bucket = 0
                # if 0 element existed, it would have come before
                raise KeyError(key + 'is not in table')
            elif elem_dist < cur_dist:
                # need to increment bucket
                bucket = (bucket + 1) % self.n
            else:
                if self.arr[bucket].key == elem.key:
                    if self.arr[bucket].tombstone:
                        return
                    return self.arr[bucket].value, scans
                bucket = (bucket + 1) % self.n
            scans += 1

    def get(self, key, default=None):
        try:
            return self.lookup(key)
        except KeyError:
            return default

    def delete(self, key):
        elem = HashElement(key, value=None)
        bucket = self._get_bucket_idx(elem.hashed)

        while True:
            if self.arr[bucket] is None:
                return

            cur = self.arr[bucket]
            cur_dist = self._get_bucket_dist(bucket, cur)
            elem_dist = self._get_bucket_dist(bucket, elem)

            if elem_dist > cur_dist:
                return
            elif elem_dist < cur_dist:
                bucket = (bucket + 1) % self.n
            else:
                if self.arr[bucket].key == elem.key:
                    if self.arr[bucket].tombstone:
                        return

                    # if self._get_bucket_idx(elem.hashed) == bucket:
                    #     if self.arr[bucket].tombstone:
                    #         return
                    # else:
                    #     if self.arr[bucket].tombstone:
                    #         return
                    self.m -= 1
                    self.arr[bucket].tombstone = True
                    return
                bucket = (bucket + 1) % self.n

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
                self.insert(item.key, item.value)


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

    scans = []
    for key in lst:
        val, scan = table.lookup(key)
        scans.append(scan)
    print scans
    print sum(scans) / float(len(scans))

    key = ''.join(random.sample(chars, 4))
    assert table.get(key) is None

    for key in lst:
        table.delete(key)
        assert table.get(key) is None
