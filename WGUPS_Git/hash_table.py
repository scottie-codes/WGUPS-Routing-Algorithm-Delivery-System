class DynamicHashTable:
    """
    A hash table for storing package data by ID that was made to rehash dynamically, if needed.

    Args:
        capacity (int): Initial number of buckets in the table (will resize if demands increase).
    """

    def __init__(self, capacity=100):
        # Initialize table with empty buckets for separate chaining
        self.table = [[] for _ in range(capacity)]
        self.size = 0

    def insert(self, key, value):
        """
        Inserts a key-value pair into the hash table. If the load factor exceeds 0.75, resizes the table.

        Args:
            key (int): Package ID (used as hash table key).
                 (object): The package object to store.
        """
        bucket = hash(key) % len(self.table)
        # Check if key exists, updates if found
        for pair in self.table[bucket]:
            if pair[0] == key:
                pair[1] = value
                return
        # otherwise adds new key-value pair
        self.table[bucket].append([key, value])
        self.size += 1

        # Calls rehash_table() to rehash if too full (over 75%) to maintain constant time performance
        if self.size / len(self.table) > 0.75:
            self.rehash_table()

    def rehash_table(self):
        """
        Doubles the capacity of the hash table and rehashes all existing entries.
        """
        old_table = self.table
        new_capacity = len(self.table) * 2 # doubles number of buckets
        self.table = [[] for _ in range(new_capacity)]
        self.size = 0
        # for every bucket and key-value pair in the old table, re-insert into new table
        for bucket in old_table:
            for key, value in bucket:
                self.insert(key, value)

        # table is now doubled in size and all data is re-hashed into new buckets

    def search(self, key):
        """
        Retrieves the value associated with a given key (package ID).

        Args:
             key (int): Package ID to look up.

        Returns:
            object or None: The package object if found, else None.
        """

        bucket = hash(key) % len(self.table)
        for pair in self.table[bucket]:
            if pair[0] == key:
                return pair[1]
        return None # if not found
