import datetime
import unittest

from beancount.core.compare import compare_entries
from beancount.core.data import Transaction
from beancount.loader import load_string

import tests.util


def tx_normal(date: datetime.date, narration: str) -> Transaction:
    return tests.util.make_transaction(
        date=date,
        payee='Tesla',
        narration=narration,
        account_from='Liabilities:CreditCard:0001',
        account_to='Assets:Car:ModelX',
        amount='200000',
    )


def tx_depreciated(date: datetime.date, narration: str) -> Transaction:
    return tests.util.make_transaction(
        date=date,
        payee='Tesla',
        narration=narration,
        account_from='Assets:Car:ModelX',
        account_to='Expenses:Depreciation:Car:ModelX',
        amount='24000',
    )


class DepreciateTest(unittest.TestCase):
    def test_simple(self):
        journal_str = """
plugin "beancount_periodic.depreciate"
1900-01-01 open Liabilities:CreditCard:0001 USD
1900-01-01 open Assets:Car:ModelX USD
1900-01-01 open Expenses:Depreciation:Car:ModelX USD
2022-03-31 * "Tesla" "Model X"
  Liabilities:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly =80000"
"""
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_normal(datetime.date(2022, 3, 31), 'Model X'),
            tx_depreciated(datetime.date(2022, 3, 31), 'Model X Depreciated(1/5)'),
            tx_depreciated(datetime.date(2023, 3, 31), 'Model X Depreciated(2/5)'),
            tx_depreciated(datetime.date(2024, 3, 31), 'Model X Depreciated(3/5)'),
            tx_depreciated(datetime.date(2025, 3, 31), 'Model X Depreciated(4/5)'),
            tx_depreciated(datetime.date(2026, 3, 31), 'Model X Depreciated(5/5)'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)

    def test_generate_until_01(self):
        journal_str = """
plugin "beancount_periodic.depreciate" "{'generate_until':'2024-03-31'}"
1900-01-01 open Liabilities:CreditCard:0001 USD
1900-01-01 open Assets:Car:ModelX USD
1900-01-01 open Expenses:Depreciation:Car:ModelX USD
2022-03-31 * "Tesla" "Model X"
  Liabilities:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly =80000"
        """
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_normal(datetime.date(2022, 3, 31), 'Model X'),
            tx_depreciated(datetime.date(2022, 3, 31), 'Model X Depreciated(1/5)'),
            tx_depreciated(datetime.date(2023, 3, 31), 'Model X Depreciated(2/5)'),
            tx_depreciated(datetime.date(2024, 3, 31), 'Model X Depreciated(3/5)'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)


if __name__ == '__main__':
    unittest.main()
