import datetime
import unittest

from beancount.core.compare import compare_entries
from beancount.core.data import Transaction
from beancount.loader import load_string

import tests.util


def tx_normal(date: datetime.date, narration: str) -> Transaction:
    return tests.util.make_transaction(
        date=date,
        payee='Landlord',
        narration=narration,
        account_from='Liabilities:CreditCard:0001',
        account_to='Equity:Amortization:Home:Rent',
        amount='12000',
    )


def tx_amortized(date: datetime.date, narration: str) -> Transaction:
    return tests.util.make_transaction(
        date=date,
        payee='Landlord',
        narration=narration,
        account_from='Equity:Amortization:Home:Rent',
        account_to='Expenses:Home:Rent',
        amount='1000',
    )


class AmortizeTest(unittest.TestCase):
    def test_simple(self):
        journal_str = """
plugin "beancount_periodic.amortize"
1900-01-01 open Liabilities:CreditCard:0001 USD
1900-01-01 open Expenses:Home:Rent USD
1900-01-01 open Equity:Amortization:Home:Rent USD
2022-03-31 * "Landlord" "2022-04 Rent"
  Liabilities:CreditCard:0001    -12000 USD
  Expenses:Home:Rent
    amortize: "1 Year @2022-04-01 /Monthly"
"""
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_normal(datetime.date(2022, 3, 31), '2022-04 Rent'),
            tx_amortized(datetime.date(2022, 4, 1), '2022-04 Rent Amortized(1/12)'),
            tx_amortized(datetime.date(2022, 5, 1), '2022-04 Rent Amortized(2/12)'),
            tx_amortized(datetime.date(2022, 6, 1), '2022-04 Rent Amortized(3/12)'),
            tx_amortized(datetime.date(2022, 7, 1), '2022-04 Rent Amortized(4/12)'),
            tx_amortized(datetime.date(2022, 8, 1), '2022-04 Rent Amortized(5/12)'),
            tx_amortized(datetime.date(2022, 9, 1), '2022-04 Rent Amortized(6/12)'),
            tx_amortized(datetime.date(2022, 10, 1), '2022-04 Rent Amortized(7/12)'),
            tx_amortized(datetime.date(2022, 11, 1), '2022-04 Rent Amortized(8/12)'),
            tx_amortized(datetime.date(2022, 12, 1), '2022-04 Rent Amortized(9/12)'),
            tx_amortized(datetime.date(2023, 1, 1), '2022-04 Rent Amortized(10/12)'),
            tx_amortized(datetime.date(2023, 2, 1), '2022-04 Rent Amortized(11/12)'),
            tx_amortized(datetime.date(2023, 3, 1), '2022-04 Rent Amortized(12/12)'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)

    def test_generate_until_01(self):
        journal_str = """
plugin "beancount_periodic.amortize" "{'generate_until':'2022-10-01'}"
1900-01-01 open Liabilities:CreditCard:0001 USD
1900-01-01 open Expenses:Home:Rent USD
1900-01-01 open Equity:Amortization:Home:Rent USD
2022-03-31 * "Landlord" "2022-04 Rent"
  Liabilities:CreditCard:0001    -12000 USD
  Expenses:Home:Rent
    amortize: "1 Year @2022-04-01 /Monthly"
        """
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_normal(datetime.date(2022, 3, 31), '2022-04 Rent'),
            tx_amortized(datetime.date(2022, 4, 1), '2022-04 Rent Amortized(1/12)'),
            tx_amortized(datetime.date(2022, 5, 1), '2022-04 Rent Amortized(2/12)'),
            tx_amortized(datetime.date(2022, 6, 1), '2022-04 Rent Amortized(3/12)'),
            tx_amortized(datetime.date(2022, 7, 1), '2022-04 Rent Amortized(4/12)'),
            tx_amortized(datetime.date(2022, 8, 1), '2022-04 Rent Amortized(5/12)'),
            tx_amortized(datetime.date(2022, 9, 1), '2022-04 Rent Amortized(6/12)'),
            tx_amortized(datetime.date(2022, 10, 1), '2022-04 Rent Amortized(7/12)'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)


if __name__ == '__main__':
    unittest.main()
