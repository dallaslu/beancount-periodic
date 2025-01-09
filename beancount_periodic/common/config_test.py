import unittest

from .config import *


class MyTestCase(unittest.TestCase):
    def test_parse(self):
        default_start_date = datetime.datetime.strptime('2021-01-31', '%Y-%m-%d')
        config_1, config_err_1 = parse('90', default_total=1000, default_start_date=default_start_date,
                                       default_duration_str='1M', default_step_str='1D', default_value=Decimal('0.1'),
                                       default_formula_str='line')
        self.assertEqual(config_1.duration, 90)

        config_2, config_err_2 = parse('2000 - 3 Months @ 2021-10-10 / Weekly +20%', default_total=1000,
                                       default_start_date=default_start_date,
                                       default_duration_str='1M', default_step_str='1D', default_value=Decimal('0.1'),
                                       default_formula_str='line')
        self.assertEqual(config_2.duration, 92)
        self.assertEqual(config_2.steps, [(7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (7, 1),
                                          (1, Decimal('0.1428571428571428571428571429'))])

    def test_get_duration(self):
        self.assertEqual(get_duration(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 1, 'Months', None), 28)
        self.assertEqual(get_duration(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 2, 'M', None), 59)
        self.assertEqual(get_duration(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 2, 'W', None), 14)
        self.assertEqual(get_duration(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 10, None, None), 10)
        self.assertEqual(get_duration(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 2, 'Year', None), 730)
        self.assertEqual(get_duration(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 4, 'Year', None), 1461)

    def test_get_steps(self):
        self.assertEqual(get_steps(datetime.datetime.strptime('2021-01-31', '%Y-%m-%d'), 10, 1, None, None),
                         [(1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)])
        self.assertEqual(get_steps(datetime.datetime.strptime('2021-01-01', '%Y-%m-%d'), 365, 1, 'Month', None),
                         [(31, 1), (28, 1), (31, 1), (30, 1), (31, 1), (30, 1), (31, 1), (31, 1), (30, 1), (31, 1), (30, 1), (31, 1)])
        self.assertEqual(get_steps(datetime.datetime.strptime('2020-11-30', '%Y-%m-%d'), 365, 1, 'Month', None),
                         [(30, 1), (31, 1), (29, 1), (30, 1), (31, 1), (30, 1), (31, 1), (30, 1), (31, 1), (31, 1), (30, 1), (31, 1)])
        self.assertEqual(get_steps(datetime.datetime.strptime('2020-11-30', '%Y-%m-%d'), 365, 1, 'Month', None),
                         [(30, 1), (31, 1), (29, 1), (30, 1), (31, 1), (30, 1), (31, 1), (30, 1), (31, 1), (31, 1), (30, 1), (31, 1)])


if __name__ == '__main__':
    unittest.main()
