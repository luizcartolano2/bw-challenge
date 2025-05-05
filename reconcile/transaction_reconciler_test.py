"""Unit tests for transaction reconciliation functionality.

This module contains test cases for the TransactionReconciler class, verifying:
- Basic matching functionality
- Handling of exact and near date matches
- Duplicate transaction handling
- Correct status assignment (FOUND/MISSING)
- Edge cases in transaction reconciliation

The tests use the standard unittest framework and follow AAA pattern (Arrange-Act-Assert).
"""

import unittest

from reconcile import TransactionReconciler


class TestTransactionReconciliation(unittest.TestCase):
    """Test suite for transaction reconciliation functionality.

    Contains test cases that verify different reconciliation scenarios including
    exact matches, near matches (within 1 day), no matches, and duplicate handling.
    """

    def test_no_matches(self):
        """Test scenario with no matching transactions between lists.

        Verifies that:
        - When no transactions match between sets
        - All transactions are marked as MISSING
        - No FOUND statuses appear in results
        """
        data1 = [
            ["2023-01-01", "Sales", "100.00", "Product A"],
            ["2023-01-02", "HR", "200.00", "Salary"]
        ]
        data2 = [
            ["2023-01-03", "Marketing", "150.00", "Ad Campaign"],
            ["2023-01-04", "IT", "300.00", "Software"]
        ]
        result1, result2 = TransactionReconciler(data1, data2).reconcile()

        self.assertIn("MISSING", result1[0])
        self.assertIn("MISSING", result1[1])
        self.assertIn("MISSING", result2[0])
        self.assertIn("MISSING", result2[1])

    def test_all_rows_match(self):
        """Test scenario where all transactions match exactly.

        Verifies that:
        - When all transactions have exact matches
        - All transactions are marked as FOUND
        - No MISSING statuses appear in results
        """
        data1 = [
            ["2023-01-01", "Sales", "100.00", "Product A"],
            ["2023-01-02", "HR", "200.00", "Salary"]
        ]
        data2 = [
            ["2023-01-01", "Sales", "100.00", "Product A"],
            ["2023-01-02", "HR", "200.00", "Salary"]
        ]
        result1, result2 = TransactionReconciler(data1, data2).reconcile()

        self.assertIn("FOUND", result1[0])
        self.assertIn("FOUND", result1[1])
        self.assertIn("FOUND", result2[0])
        self.assertIn("FOUND", result2[1])

    def test_some_matches_exact_dates_only(self):
        """Test scenario with partial matches (exact dates only).

        Verifies that:
        - Only transactions with exact date matches are paired
        - Non-matching transactions are marked as MISSING
        - Matching logic respects all fields (date, department, amount, name)
        """
        data1 = [
            ["2023-01-01", "Sales", "100.00", "Product A"],  # Will match
            ["2023-01-02", "HR", "200.00", "Salary"]  # Won't match
        ]
        data2 = [
            ["2023-01-01", "Sales", "100.00", "Product A"],  # Match
            ["2023-01-02", "HR", "300.00", "Salary"]  # Different amount
        ]
        result1, result2 = TransactionReconciler(data1, data2).reconcile()

        # Check first set
        self.assertIn("FOUND", result1[0])
        self.assertIn("MISSING", result1[1])

        # Check second set
        self.assertIn("FOUND", result2[0])
        self.assertIn("MISSING", result2[1])

    def test_some_matches_no_exact_dates(self):
        """Test scenario with partial matches (near dates only).

        Verifies that:
        - Transactions with dates within 1 day are matched
        - Transactions with dates differing by >1 day are not matched
        - The matching logic properly handles date proximity
        """
        data1 = [
            ["2023-01-01", "Sales", "100.00", "Product A"],  # Will match (2023-01-02 is close)
            ["2023-01-03", "HR", "200.00", "Salary"]  # Won't match
        ]
        data2 = [
            ["2023-01-02", "Sales", "100.00", "Product A"],  # Close date match
            ["2023-01-05", "HR", "200.00", "Salary"]  # Too far date
        ]
        result1, result2 = TransactionReconciler(data1, data2).reconcile()

        # Check first set
        self.assertIn("FOUND", result1[0])
        self.assertIn("MISSING", result1[1])

        # Check second set
        self.assertIn("FOUND", result2[0])
        self.assertIn("MISSING", result2[1])

    def test_matches_with_duplicates(self):
        """Test scenario with duplicate transactions in source data.

        Verifies that:
        - When multiple potential matches exist
        - The earliest dated transaction is selected
        - Only one match is created per transaction
        """
        data1 = [
            ["2023-01-01", "Sales", "100.00", "Product A"]  # Should match earliest in data2
        ]
        data2 = [
            ["2023-01-03", "Sales", "100.00", "Product A"],  # Later date
            ["2023-01-02", "Sales", "100.00", "Product A"],  # Earlier date (should match this)
            ["2023-01-04", "Sales", "100.00", "Product A"]  # Later date
        ]
        reconciler = TransactionReconciler(data1, data2)
        result1, result2 = reconciler.reconcile()

        # Check that the earliest date was matched (2023-01-02)
        matched_row = next(r for r in result2 if "FOUND" in r)
        self.assertIn("2023-01-02", matched_row)

        # Check that only one match occurred
        found_count = sum(1 for r in result2 if "FOUND" in r)
        self.assertEqual(1, found_count)


if __name__ == '__main__':
    unittest.main()
