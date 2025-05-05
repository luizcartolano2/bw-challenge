import csv
from pathlib import Path

from reconcile import reconcile_accounts

if __name__ == "__main__":
    transactions1 = list(csv.reader(Path('data/trans1.csv').open()))
    transactions2 = list(csv.reader(Path('data/trans2.csv').open()))
    out1, out2 = reconcile_accounts(transactions1, transactions2)
    print(out1)
    print("--------------------------------------------")
    print(out2)
