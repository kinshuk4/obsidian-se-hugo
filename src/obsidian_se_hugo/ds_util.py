class LinkedHashSet:
    def __init__(self):
        # A dictionary to store unique elements (acts as the set)
        self._set = {}
        # A list to maintain the insertion order (acts as the linked list)
        self._list = []

    def add(self, item):
        """Adds an item to the set if it's not already present."""
        if item not in self._set:
            self._set[item] = None  # The value can be anything, we just need the key
            self._list.append(item)

    def remove(self, item):
        """Removes an item from the set and the list."""
        if item in self._set:
            del self._set[item]
            self._list.remove(item)

    def __contains__(self, item):
        """Checks if an item is in the set."""
        return item in self._set

    def __len__(self):
        """Returns the number of elements in the set."""
        return len(self._list)

    def __iter__(self):
        """Allows for iteration in insertion order."""
        return iter(self._list)