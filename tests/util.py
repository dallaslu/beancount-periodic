import datetime
from decimal import Decimal
from typing import List

from beancount.core.amount import Amount
from beancount.core.data import Transaction, Posting


def get_transactions_cleaned(entries: List) -> List[Transaction]:
    for e in entries:
        if not isinstance(e, Transaction):
            continue
        e = e._replace(meta={'lineno': 0})
        e = e._replace(postings=[
            p._replace(meta={'lineno': 0}) for p in e.postings
        ])
        yield e


def make_transaction(date: datetime.date, payee: str, narration: str, account_from: str, account_to: str,
                     amount: str) -> Transaction:
    tx = Transaction(
        date=date,
        flag='*',
        payee=payee,
        narration=narration,
        postings=[
            Posting(
                account=account_from,
                units=Amount(
                    number=-Decimal(amount),
                    currency='USD'
                ),
                cost=None,
                price=None,
                flag=None,
                meta={'lineno': 0},
            ),
            Posting(
                account=account_to,
                units=Amount(
                    number=Decimal(amount),
                    currency='USD'
                ),
                cost=None,
                price=None,
                flag=None,
                meta={'lineno': 0},
            ),
        ],
        meta={'lineno': 0},
        tags=frozenset(),
        links=frozenset(),
    )
    return tx
