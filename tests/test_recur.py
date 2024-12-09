import datetime
import unittest

from beancount.core.compare import compare_entries
from beancount.core.data import Transaction
from beancount.loader import load_string

import tests.util


def tx_recurring(date: datetime.date, narration: str) -> Transaction:
    return tests.util.make_transaction(
        date=date,
        payee='Provider',
        narration=narration,
        account_from='Liabilities:CreditCard:0001',
        account_to='Expenses:Home:CommunicationFee',
        amount='50',
    )


class RecurTest(unittest.TestCase):
    def test_simple(self):
        journal_str = """
plugin "beancount_periodic.recur"
1900-01-01 open Liabilities:CreditCard:0001 USD
1900-01-01 open Expenses:Home:CommunicationFee USD
2022-03-31 * "Provider" "Net Fee"
  recur: "1 Year /Monthly"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee
"""
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_recurring(datetime.date(2022, 3, 31), 'Net Fee Recurring(1/12)'),
            tx_recurring(datetime.date(2022, 4, 30), 'Net Fee Recurring(2/12)'),
            tx_recurring(datetime.date(2022, 5, 31), 'Net Fee Recurring(3/12)'),
            tx_recurring(datetime.date(2022, 6, 30), 'Net Fee Recurring(4/12)'),
            tx_recurring(datetime.date(2022, 7, 31), 'Net Fee Recurring(5/12)'),
            tx_recurring(datetime.date(2022, 8, 31), 'Net Fee Recurring(6/12)'),
            tx_recurring(datetime.date(2022, 9, 30), 'Net Fee Recurring(7/12)'),
            tx_recurring(datetime.date(2022, 10, 31), 'Net Fee Recurring(8/12)'),
            tx_recurring(datetime.date(2022, 11, 30), 'Net Fee Recurring(9/12)'),
            tx_recurring(datetime.date(2022, 12, 31), 'Net Fee Recurring(10/12)'),
            tx_recurring(datetime.date(2023, 1, 31), 'Net Fee Recurring(11/12)'),
            tx_recurring(datetime.date(2023, 2, 28), 'Net Fee Recurring(12/12)'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)

    def test_generate_until_01(self):
        journal_str = """
plugin "beancount_periodic.recur" "{'generate_until':'2022-11-30'}"
1900-01-01 open Liabilities:CreditCard:0001 USD
1900-01-01 open Expenses:Home:CommunicationFee USD
2022-03-31 * "Provider" "Net Fee"
  recur: "1 Year /Monthly"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee
"""
        entries, errors, options_map = load_string(journal_str)
        self.assertEqual(len(errors), 0)

        expected_entries = [
            tx_recurring(datetime.date(2022, 3, 31), 'Net Fee Recurring(1/12)'),
            tx_recurring(datetime.date(2022, 4, 30), 'Net Fee Recurring(2/12)'),
            tx_recurring(datetime.date(2022, 5, 31), 'Net Fee Recurring(3/12)'),
            tx_recurring(datetime.date(2022, 6, 30), 'Net Fee Recurring(4/12)'),
            tx_recurring(datetime.date(2022, 7, 31), 'Net Fee Recurring(5/12)'),
            tx_recurring(datetime.date(2022, 8, 31), 'Net Fee Recurring(6/12)'),
            tx_recurring(datetime.date(2022, 9, 30), 'Net Fee Recurring(7/12)'),
            tx_recurring(datetime.date(2022, 10, 31), 'Net Fee Recurring(8/12)'),
            tx_recurring(datetime.date(2022, 11, 30), 'Net Fee Recurring(9/12)'),
        ]

        same, missing1, missing2 = compare_entries(list(tests.util.get_transactions_cleaned(entries)), expected_entries)
        self.assertTrue(same)


if __name__ == '__main__':
    unittest.main()
