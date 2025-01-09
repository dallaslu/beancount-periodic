import datetime
import unittest

from beancount.core.compare import compare_entries
from beancount.core.data import Transaction
from beancount.loader import load_string

import tests.util


def tx_split(date: datetime.date, narration: str, amount: str) -> Transaction:
    return tests.util.make_transaction(
        date=date,
        payee=None,
        narration=narration,
        account_from='Liabilities:Tax',
        account_to='Expenses:Tax:Income',
        amount=amount,
    )


class SplitTest(unittest.TestCase):
    def test_simple(self):
        journal_str = """
plugin "beancount_periodic.split"
1900-01-01 open Liabilities:Tax USD
1900-01-01 open Expenses:Tax:Income USD
2025-01-01 * "Tax Estimate"
  split: "Year / Monthly"
  Liabilities:Tax
  Expenses:Tax:Income 4380 USD
"""
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_split(datetime.date(2025, 1, 1), 'Tax Estimate Split(1/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 2, 1), 'Tax Estimate Split(2/12)', '336.0000000000000000000000000'),
            tx_split(datetime.date(2025, 3, 1), 'Tax Estimate Split(3/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 4, 1), 'Tax Estimate Split(4/12)', '360.0000000000000000000000000'),
            tx_split(datetime.date(2025, 5, 1), 'Tax Estimate Split(5/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 6, 1), 'Tax Estimate Split(6/12)', '360.0000000000000000000000000'),
            tx_split(datetime.date(2025, 7, 1), 'Tax Estimate Split(7/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 8, 1), 'Tax Estimate Split(8/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 9, 1), 'Tax Estimate Split(9/12)', '360.0000000000000000000000000'),
            tx_split(datetime.date(2025, 10, 1), 'Tax Estimate Split(10/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 11, 1), 'Tax Estimate Split(11/12)', '360.0000000000000000000000000'),
            tx_split(datetime.date(2025, 12, 1), 'Tax Estimate Split(12/12)', '372.0000000000000000000000000'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)

    def test_generate_until_01(self):
        journal_str = """
plugin "beancount_periodic.split" "{'generate_until':'2025-04-30'}"
1900-01-01 open Liabilities:Tax USD
1900-01-01 open Expenses:Tax:Income USD
2025-01-01 * "Tax Estimate"
  split: "Year / Monthly"
  Liabilities:Tax
  Expenses:Tax:Income 4380 USD
"""
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_split(datetime.date(2025, 1, 1), 'Tax Estimate Split(1/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 2, 1), 'Tax Estimate Split(2/12)', '336.0000000000000000000000000'),
            tx_split(datetime.date(2025, 3, 1), 'Tax Estimate Split(3/12)', '372.0000000000000000000000000'),
            tx_split(datetime.date(2025, 4, 1), 'Tax Estimate Split(4/12)', '360.0000000000000000000000000'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)


if __name__ == '__main__':
    unittest.main()
