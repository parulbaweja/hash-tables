from chaining import HashTable as chaining
from linear_probing import HashTable as probing
from robinhood import HashTable as robinhood
import string
import random
import pprint


def get_table(table_type):
    """
    Selects appropriate hash table based on string arg.
    """
    if table_type == 'chaining':
        return chaining()
    elif table_type == 'probing':
        return probing()
    elif table_type == 'probing2':
        return probing(probe=2)
    else:
        return robinhood()


def collect_scans(table_type, items):
    """
    Returns average number of scans to lookup items given a list of items.
    """
    table = get_table(table_type)
    lst = []
    for key, value in items:
        table.insert(key, value)
        lst.append(key)

    scans = []
    for key in lst:
        val, scan = table.lookup(key)
        scans.append(scan)

    ave_scan = sum(scans) / float(len(items))
    return ave_scan


# initialize available chars, table types, and sizes
chars = string.ascii_letters + string.digits
tables = ['chaining', 'probing', 'probing2', 'robinhood']
sizes = [32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

# initialize data storge for average scans per size
scans = {
    'chaining': [],
    'probing': [],
    'probing2': [],
    'robinhood': [],
}

# for each size of inputs, insert the key-value pairs
# for each table, retrieve ave num of scans and append to data dictionary
for size in sizes:
    lst = []
    for i in xrange(size):
        key = ''.join(random.sample(chars, 3))
        value = ''.join(random.sample(chars, 3))
        lst.append((key, value))
    for table in tables:
        ave_scan = collect_scans(table, lst)
        scans[table].append(ave_scan)

pprint.pprint(scans)
