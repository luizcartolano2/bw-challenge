"""This module contains the TransactionReconciler class for comparing and reconciling transaction lists.

The TransactionReconciler compares two sets of transactions, identifies matches (both exact and approximate),
and produces reconciliation reports showing which transactions were matched or missing from each set.
"""

from datetime import datetime
from typing import Tuple, List, Optional

from reconcile import Transaction


class TransactionReconciler:
    """A class for reconciling two sets of financial transactions.

    The reconciler compares transactions from two different sources, identifies matches
    (including those with slightly different dates), and generates reconciliation reports.

    Attributes:
        transactions1 (List[Transaction]): First set of transactions to reconcile.
        transactions2 (List[Transaction]): Second set of transactions to reconcile.

    Methods:
        parse_row: Converts a raw data row into a Transaction object.
        find_match: Finds a matching transaction in a list of candidates.
        reconcile: Performs the reconciliation between both transaction sets.
    """

    def __init__(self, rows1: List[List[str]], rows2: List[List[str]]):
        """Initialize the TransactionReconciler with two sets of transaction data.

        Args:
            rows1 (List[List[str]]): Raw transaction data from the first source.
            rows2 (List[List[str]]): Raw transaction data from the second source.
        """
        self.transactions1 = [self.parse_row(row) for row in rows1]
        self.transactions2 = [self.parse_row(row) for row in rows2]

    @staticmethod
    def parse_row(row: List[str]) -> Transaction:
        """Convert a raw data row into a Transaction object.

        Args:
            row (List[str]): A list of strings representing a transaction in the format:
                          [date (YYYY-MM-DD), department, amount, name, ...]

        Returns:
            Transaction: A Transaction object populated with the row's data.
        """
        return Transaction(
            date=datetime.strptime(row[0], "%Y-%m-%d").date(),
            department=row[1],
            amount=float(row[2]),
            name=row[3],
            original_row=row
        )

    @staticmethod
    def find_match(txn: Transaction, candidates: List[Transaction]) -> Optional[Transaction]:
        """Find a matching transaction from a list of candidate transactions.

        First looks for exact date matches, then falls back to near matches (±1 day).
        Only considers candidates that haven't already been matched (status=None).

        Args:
            txn (Transaction): The transaction to find a match for.
            candidates (List[Transaction]): Potential matching transactions to search through.

        Returns:
            Optional[Transaction]: The best matching transaction if found, None otherwise.
        """
        # Try exact date match first
        exact_matches = [
            c for c in candidates
            if c.status is None and txn.date == c.date and txn.matches(c)
        ]
        if exact_matches:
            return min(exact_matches, key=lambda c: c.date)  # pick earliest by date

        # Try +/- 1 day match
        close_matches = [
            c for c in candidates
            if c.status is None and txn.is_date_close(c) and txn.matches(c)
        ]
        if close_matches:
            return min(close_matches, key=lambda c: c.date)

        return None

    def reconcile(self) -> Tuple[List[str], List[str]]:
        """Perform the reconciliation between both transaction sets.

        Compares transactions from both sources, marks matches as "FOUND" and
        unmatched transactions as "MISSING". Returns the results as CSV-style strings.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing:
                - First list: Reconciled results from the first transaction set
                - Second list: Reconciled results from the second transaction set
                Each result includes the original data plus a status field.
        """
        for txn1 in self.transactions1:
            match = self.find_match(txn1, self.transactions2)
            if match:
                txn1.status = "FOUND"
                match.status = "FOUND"

        # After matching, tag all unmatched as MISSING
        for txn in self.transactions1:
            if txn.status is None:
                txn.status = "MISSING"
        for txn in self.transactions2:
            if txn.status is None:
                txn.status = "MISSING"

        # Convert to CSV-style strings with status
        out1 = [",".join(txn.original_row + [txn.status]) for txn in self.transactions1]
        out2 = [",".join(txn.original_row + [txn.status]) for txn in self.transactions2]

        return out1, out2
