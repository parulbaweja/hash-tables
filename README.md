# Hash Tables

This repo contains three implementations of a hash table with the following applied concepts: chaining, linear probing and robinhood. Each explores a different framework for space management and information retrieval.

Each key is hashed with Python's md5, built into the hashlib library. To find the specific bucket a key falls into, the hashed value is mod-ed by the length of the list (hash_value % n).

Each implementation includes a load factor threshold of 0.9 (inserted elements / length of list). If the load factor increases, the allocated storage must be resized. All implementations follow the model of doubling the allocated storage. Each element is re-hashed and re-inserted in a new list, which replaces the current list.

## Chaining

### Summary

In this implementation, the HashElement class includes key, value and next attributes. Each bucket takes the form of a linked list. If a collision occurs (where two disparate keys hash and mod to the same bucket), the item to be inserted is simply set as the next for the head or parent element.

### Considerations

1. Technically, lookup, insert and delete are O(kᵢ), where kᵢ is the number of elements in the ith bucket. However, on average with a well distributed hash function, this tends to be a constant, allowing for O(1) runtime on these operations.
2. Linked lists do not optimize for cache locality, as nodes are dispersed throughout memory.
3. In its worse case, all keys hash to the same spot, so search is O(n). Ideally, each slot holds the average number of keys.

## Linear & Quadratic Probing

### Summary

In linear probing, to find an element, we can search the i + 0, i + 1, i + 2 indices and so on. The first element that lands in a particular bucket is inserted at that index. Thereafter, elements that also land in the same particular bucket are inserted at the first available spot after the original bucket.

```python
[None, None, 2, 3, 4, 5, 6, None, 8, 9, 10, None, 12, 13, 14, 15]
```

In the list above (n = 16), bucket 15 is filled and we trying to insert an item that hashes and mods to bucket 15. We must not look at the next location, which is 16, or 0 due to the wrap-arround:

  16 (current index)  % 16 (list size) = 0

When an element is removed, it must be converted to a tombstone. It now serves as a marker that other elements, that fall into that bucket, live further on or around the list. The tombstone remains until such time that a new element is inserted into the bucket. My lookup continues until it hits an empty slot: tombstones prevent search misses.

### Quadratic Version

Naively, I implemented the following quadatric probing function (for linear, probe = 1) to find the index of the next bucket to search:

```python
    next_bucket = (bucket + base ** probe) % n
```

where:

- bucket = current index
- base = 1, 2, 3, 4, etc
- probe = a selected constant for the exponent
- n = length of list

For probe = 2, this function caused an infinite loop because the same four indices were being visited. This loop was particularly interesting to debug.

For a table with n = 16, initial bucket = 0 and probe = 2, let's track the next_bucket.

| i | bucket + base ** probe | % n |
|:-:|:----------------------:|:---:|
| 0 | 0                      | 0   |
| 1 | 1                      | 1   |
| 2 | 4                      | 4   |
| 3 | 9                      | 9   |
| 4 | 16                     | 0   |
| 5 | 25                     | 9   |
| 6 | 36                     | 4   |
| 7 | 49                     | 1   |

As displayed in the '% n' column, the same buckets are visited every four iterations, so we never search all the buckets. After research, it turns out that a power-of-two table must have the following [quadratic function] (http://research.cs.vt.edu/AVresearch/hashing/quadratic.php):

```python
next_bucket = (bucket + base / 2 + (base ** probe) / 2) % n
```

Let's examine the previous example with this implementation:

| i | bucket + base ** probe | % n |
|:-:|:----------------------:|:---:|
| 0 | 0                      | 0   |
| 1 | 1                      | 1   |
| 2 | 3                      | 3   |
| 3 | 6                      | 6   |
| 4 | 10                     | 10  |
| 5 | 15                     | 15  |
| 6 | 21                     | 5   |
| 7 | 28                     | 12  |

This function ensures that every bucket is visited at least once - upon searching, we will come across a bucket that either has the item or is empty.

## Robinhood

### Summary

The Robinhood implementation requires keeping elements with the same buckets adjacent to one another. The HashElement now contains key, value, tombstone (bool) and hashed (the hashed value of the key). By storing this, we have an easy lookup to compare our arg key to keys that live in the table.

To insert a key, we now compare the distances if keys from their respective buckets. For example, let's say we have the following list, where each number represents the bucket that key belongs to:

```python
[ 15, 15, 0, 1, 2, ... 15]
```

Now, we want to insert a key that falls in the 0 bucket. Here's what we do:
1) Go to the 0 bucket. If nothing is there, insert it.
2) Unfortunately, something is in the 0 bucket. So, let's compare how far the current element is from it's home bucket versus our insert element:
    - 15 is 1 away from its home bucket due to wrap-around
    - 0 is 0 away from its home bucket
3) Since 15 is further from it's home, we leave it there and keep searching.

Based on this, we only insert if the current element distance is less than the insert element distance. At this point, we swap the elements and recurse.

### Considerations

1. This is similar to chaining (elements with same bucket exist within a linked list) in that elements are grouped near each other, however it takes advantage of cache locality due to a list's contiguous storage in memory.
2. Search time reduces - the overhead is in finding the first element with that bucket, but once we find it, we iterate through the list until we hit an element with a larger bucket.
3. An optimization of this method would involve storing the list index of the first element in the list that belongs to this bucket. This would reduce the number of scans it takes to find elements that belong to said bucket.

## Benchmarking Scans

To reach a better conclusion in terms of comparing the methods, I chose to examine the average number of scans each method takes to lookup a key. For each method, I inserted the same, randomly generated list of key-value pairs, called a lookup on each key in the list and kept track of the scans until the key was found.

![Average Number of Scans to Lookup per Table Size] (https://github.com/parulbaweja/hash-tables/blob/master/images/benchmark_scans.jpg)

The graph displays that scans remain constant for each method. In particular, chaining requires the fewest scans: the items are distributed evenly, so we reach a bucket immediately and iterate until we find the item. Meanwhile, linear probing requires the most scans, as the item is inserted at the next available empty bucket. For robinhood, the implementation would really take advantage of cache locality if the optimization (listed in Considerations) was implemented; then, robinhood's performance would be near that of chaining's.
