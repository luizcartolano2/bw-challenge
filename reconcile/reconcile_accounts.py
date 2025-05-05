"""This module provides a high-level interface for reconciling transaction accounts.

The module contains a simplified function that wraps the TransactionReconciler class
to provide a straightforward interface for comparing two sets of transaction data.

Example:
    >>> transactions1 = [["2023-01-01", "Sales", "100.00", "Product A"]]
    >>> transactions2 = [["2023-01-01", "Sales", "100.00", "Product A"]]
    >>> result1, result2 = reconcile_accounts(transactions1, transactions2)
    >>> print(result1[0])
    2023-01-01,Sales,100.00,Product A,FOUND
"""
from typing import List, Tuple
from reconcile import TransactionReconciler


def reconcile_accounts(transactions1: List[List[str]], transactions2: List[List[str]]) -> Tuple[List[str], List[str]]:
    """Reconcile two sets of transaction data and return matched results.

    This function provides a simplified interface for comparing transaction records
    from two different sources. It automatically:
    - Parses the raw transaction data
    - Identifies matching transactions (including near matches)
    - Tags all transactions with their reconciliation status
    - Returns the results in CSV-style format

    Args:
        transactions1 (List[List[str]]): Raw transaction data from first source.
                                        Each transaction should be a list of strings
                                        in format [date, department, amount, name, ...]
        transactions2 (List[List[str]]): Raw transaction data from second source.
                                        Same format as transactions1.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists of strings:
            - First list: Reconciled results from transactions1
            - Second list: Reconciled results from transactions2
            Each result string is a CSV line with original data plus status field.
    """
    reconciler = TransactionReconciler(transactions1, transactions2)
    return reconciler.reconcile()
