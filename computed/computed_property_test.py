"""Unit tests for computed property functionality.

This module demonstrates and tests the implementation of a `computed_property` decorator
that provides cached property computation with dependency tracking. The decorator:
- Automatically caches computed values
- Recomputes only when dependencies change
- Supports getter, setter, and deleter operations
- Tracks computation count for testing purposes
"""

import unittest

from computed import computed_property


class Person:
    """Example class demonstrating computed property usage.

    This class shows how to use the `computed_property` decorator to create a
    cached property that automatically updates when its dependencies change.

    Attributes:
        first (str): First name of the person
        last (str): Last name of the person
        _compute_count (int): Internal counter tracking property computations
    """

    def __init__(self, first, last):
        """Initialize a Person instance with first and last names.

        Args:
            first (str): First name
            last (str): Last name
        """
        self.first = first
        self.last = last
        self._compute_count = 0  # tracks how often `full_name` is recomputed

    @computed_property('first', 'last', 'age')
    def full_name(self):
        """Computed property combining first and last names.

        The property is automatically recomputed when any of its dependencies
        (first, last, or age) change. The result is cached between accesses.

        Returns:
            str: Combined first and last name separated by a space
        """
        self._compute_count += 1
        return f"{self.first} {self.last}"

    @full_name.setter
    def full_name(self, value):
        """Setter that splits full name into first and last components.

        Args:
            value (str): Full name to split (expects exactly one space)
        """
        first, last = value.split()
        self.first = first
        self.last = last

    @full_name.deleter
    def full_name(self):
        """Deleter that clears both first and last names."""
        self.first = ''
        self.last = ''


class TestComputedProperty(unittest.TestCase):
    """Test suite for computed property functionality.

    Verifies correct behavior of the `computed_property` decorator through
    the `Person.full_name` example property.
    """

    def test_initial_computation(self):
        """Test initial property computation.

        Verifies:
        - Property computes correct initial value
        - Computation count increments on first access
        """
        p = Person("John", "Doe")
        self.assertEqual(p.full_name, "John Doe")
        self.assertEqual(p._compute_count, 1)

    def test_cached_value(self):
        """Test property value caching.

        Verifies:
        - Property value is cached between accesses
        - Computation count remains unchanged on subsequent accesses
        """
        p = Person("Jane", "Smith")
        _ = p.full_name
        _ = p.full_name
        self.assertEqual(p._compute_count, 1)

    def test_dependency_invalidation(self):
        """Test dependency-triggered recomputation.

        Verifies:
        - Changing a dependency invalidates the cache
        - Property recomputes on next access after invalidation
        - Computation count increments appropriately
        """
        p = Person("Alice", "Wonder")
        _ = p.full_name
        p.first = "Ally"
        self.assertEqual(p.full_name, "Ally Wonder")
        self.assertEqual(p._compute_count, 2)

    def test_setter(self):
        """Test property setter functionality.

        Verifies:
        - Setting the property updates underlying dependencies
        - Property reflects new values after being set
        """
        p = Person("A", "B")
        p.full_name = "Foo Bar"
        self.assertEqual(p.first, "Foo")
        self.assertEqual(p.last, "Bar")
        self.assertEqual(p.full_name, "Foo Bar")

    def test_deleter(self):
        """Test property deleter functionality.

        Verifies:
        - Deleting the property clears underlying values
        - Property reflects cleared state after deletion
        """
        p = Person("X", "Y")
        del p.full_name
        self.assertEqual(p.first, "")
        self.assertEqual(p.last, "")


if __name__ == '__main__':
    unittest.main()
