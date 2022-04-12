import collections
from typing import List
from datetime import date
from decimal import Decimal
from typing import NamedTuple

PeriodicConfig = NamedTuple('PeriodicConfig', [
    ('total', Decimal),
    ('start', date),
    ('duration', int),
    ('steps', List),
    ('equal_amount', bool),
    ('salvage_value', Decimal),
    ('formula', str)
])

PeriodicConfigError = collections.namedtuple('ReserveConfigError', 'source message entry')
