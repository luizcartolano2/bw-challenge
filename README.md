# BW Challenge

Project that implements a reconcile account method, a reverse file read and a computed property decorator.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

Follow these steps to set up the project locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/luizcartolano2/bw-challenge
   ```
2. Navigate into the project directory
3. Either run one of the main files or some of the tests

## Project Structure
```
└── bw-challenge/
    ├── computed/
    │   ├── __init__.py
    │   ├── computed_property.py
    │   ├── computed_property_decorator.py
    │   └── computed_property_test.py
    ├── exceptions/
    │   ├── __init__.py
    │   └── buffer_too_small.py
    ├── fileread/
    │   ├── __init__.py
    │   ├── last_lines.py
    │   └── last_lines_test.py
    ├── reconcile/
    │   ├── __init__.py
    │   ├── reconcile_accounts.py
    │   ├── transaction.py
    │   ├── transaction_reconciler.py
    │   └── transaction_reconciler_test.py
    ├── .gitignore
    ├── 1_main_reconcile_acc.py
    ├── 2_main_lines.py
    ├── 3_main_computed_prop.py
    └── README.md
```

## License
[MIT](https://choosealicense.com/licenses/mit/)