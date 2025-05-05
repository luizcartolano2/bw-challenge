"""This module contains the Transaction class which represents a financial transaction.

The Transaction class is a data structure that stores information about individual
financial transactions, including their date, department, amount, and other relevant
details. It also provides methods for comparing transactions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Transaction:
    """A class representing a financial transaction.

    Attributes:
        date (datetime): The date and time when the transaction occurred.
        department (str): The department associated with the transaction.
        amount (float): The monetary amount of the transaction.
        name (str): The name or description of the transaction.
        status (Optional[str]): The current status of the transaction (e.g., 'pending', 'completed').
                              Defaults to None if not specified.
        original_row (List[str]): The original data row from which the transaction was created.
                                Defaults to an empty list if not specified.

    Methods:
        matches(other): Determines if this transaction matches another based on key fields.
        is_date_close(other): Checks if this transaction's date is close to another.
    """

    date: datetime.date
    department: str
    amount: float
    name: str
    status: Optional[str] = None
    original_row: List[str] = field(default_factory=list)

    def matches(self, other: 'Transaction') -> bool:
        """Check if this transaction matches another transaction based on key fields.

        Two transactions are considered matching if they have the same department,
        amount, and name.

        Args:
            other (Transaction): Another Transaction object to compare against.

        Returns:
            bool: True if the transactions match on key fields, False otherwise.
        """
        return (
                self.department == other.department and
                self.amount == other.amount and
                self.name == other.name
        )

    def is_date_close(self, other: 'Transaction') -> bool:
        """Check if this transaction's date is within one day of another transaction's date.

        Args:
            other (Transaction): Another Transaction object to compare against.

        Returns:
            bool: True if the dates are within one day of each other, False otherwise.
        """
        return abs((self.date - other.date).days) <= 1
