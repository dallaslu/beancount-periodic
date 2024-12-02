import datetime
import re
import sys
from typing import Tuple

from . import *

from dateutil.relativedelta import relativedelta

try:
    from beancount.utils.date_utils import parse_date_liberally
except ImportError:
    from beangulp.date_utils import parse_date_liberally

RE_TOTAL = '\\s*(?P<total>\\d+(?:\\.\\d+)?)\\s*-'
PART_DURATION_NAMED = "(?:Day|Week|Month|Quarter|Year)"
PART_DURATION_NAMED_SHORTEN = "[DWMQY]"
DURATION_NUM = f'(?P<num>\\d+)?\\s*(?:(?P<unit_named>{PART_DURATION_NAMED}s?)|(?P<unit_named_shorten>' \
               f'{PART_DURATION_NAMED_SHORTEN}))?'
RE_DATE_START = "@\\s*(?P<date_start>\\d{4}-\\d{2}-\\d{2})"
RE_DATE_END = "~\\s*(?P<date_end>\\d{4}-\\d{2}-\\d{2})"
RE_DURATION = f'(?:{DURATION_NUM}\\s*(?:{RE_DATE_START}\\s*)?(?:{RE_DATE_END})?)'
RE_STEP_A = f'(?P<step_num>\\d+)\\s*(?:(?P<step_unit_named>{PART_DURATION_NAMED}s?[!]?)|(?P<step_unit_named_shorten>' \
            f'{PART_DURATION_NAMED_SHORTEN}[!]?))?'
RE_STEP_B = f'(?P<step_named>(?:Dai|Week|Month|Quarter|Year)ly[!]?)'
RE_STEP = f'{RE_STEP_A}|{RE_STEP_B}'
RE_VALUE = "[\\+\\=]\\s*(?P<value>\\d+(?:\\.\\d+)?%?)"
RE_FORMULA = "\\s*\\*(?P<formula>linear|straight|line|load|work-load|accelerated-sum|sum|accelerated-declining" \
             "|declining)"
RE = fr'^\s*(?:{RE_TOTAL}\s*)?(?:{RE_DURATION}\s*)?(?:/\s*(?:{RE_STEP})\s*)?(?:{RE_FORMULA}\s*)?(?:{RE_VALUE}\s*)?$'
# sys.stderr.write('%s\n' % RE)
CONFIG_STR_PATTERN = re.compile(RE)
CONFIG_STR_PATTERN_DURATION = re.compile(fr'{RE_DURATION}')
CONFIG_STR_PATTERN_STEP = re.compile(fr'{RE_STEP}')


def get_duration(start_date, num, unit_named, unit_named_shorten):
    """
    Calculate the number of days by natural date
    :param start_date:
    :param num:
    :param unit_named:
    :param unit_named_shorten:
    :return: days num
    """
    unit = unit_named if unit_named else unit_named_shorten
    if unit:
        key_letter = unit[:1]
        if key_letter == 'D':
            return 1 * num
        elif key_letter == 'W':
            return 7 * num
        elif key_letter == 'M':
            delta = (start_date + relativedelta(months=num)) - start_date
            return delta.days
        elif key_letter == 'Q':
            delta = (start_date + relativedelta(months=num * 3)) - start_date
            return delta.days
            pass
        elif key_letter == 'Y':
            delta = (start_date + relativedelta(years=num)) - start_date
            return delta.days
    else:
        return num


def get_steps(start_date, duration, num, unit_named, unit_named_shorten):
    """
    Calculate the step length of each settlement based on the natural date (the actual number of days)
    :param start_date:
    :param duration:
    :param num:
    :param unit_named:
    :param unit_named_shorten:
    :return:
    """
    unit = unit_named if unit_named else unit_named_shorten
    if unit:
        key_letter = unit[:1]
        if key_letter == 'D':
            return get_steps_simple(duration, num)
        elif key_letter == 'W':
            return get_steps_simple(duration, 7 * num)
        elif key_letter == 'M':
            return __get_steps(start_date, duration, lambda i: relativedelta(months=i))
        elif key_letter == 'Q':
            return __get_steps(start_date, duration, lambda i: relativedelta(months=i * 3))
        elif key_letter == 'Y':
            return __get_steps(start_date, duration, lambda i: relativedelta(years=i))
    else:
        return get_steps_simple(duration, num)


def get_steps_simple(duration, step):
    """
    Simple calculation of the step length for each settlement
    :param duration:
    :param step:
    :return:
    """
    steps = []
    remainder = duration
    while True:
        if step <= remainder:
            steps.append((step, 1))
            remainder -= step
        else:
            if remainder > 0:
                steps.append((remainder, Decimal(remainder) / step))
            break
    return steps


def __get_steps(start_date, duration, delta_callback):
    steps = []
    start = start_date
    remainder = duration
    for i in range(duration):
        tail_date = start_date + delta_callback(i + 1)
        delta = tail_date - start
        if delta.days <= remainder:
            steps.append((delta.days, 1))
            start = tail_date
            remainder -= delta.days
        else:
            if remainder > 0:
                steps.append((remainder, Decimal(remainder) / delta.days))
            break
    return steps


def parse(
        config,
        default_total,
        default_start_date: datetime.date,
        default_duration_str: str,
        default_step_str: str,
        default_value: Decimal,
        default_formula_str,
) -> Tuple[PeriodicConfig, PeriodicConfigError]:
    """
    Parse the configuration
    :param config:
    :param default_total:
    :param default_start_date:
    :param default_duration_str:
    :param default_step_str:
    :param default_value:
    :param default_formula_str:
    :return:
    """
    if isinstance(config, str):
        match = CONFIG_STR_PATTERN.search(config)
        if match:
            total = match.group('total')
            num = match.group('num')
            unit_named = match.group('unit_named')
            unit_named_shorten = match.group('unit_named_shorten')
            date_start = match.group('date_start')
            date_end = match.group('date_end')
            step_num = match.group('step_num')
            step_unit_named = match.group('step_unit_named')
            step_unit_named_shorten = match.group('step_unit_named_shorten')
            step_named = match.group('step_named')
            value = match.group('value')
            formula = match.group('formula')
            __print_config_match_result(date_end, date_start, formula, num, step_named, step_num, step_unit_named,
                                        step_unit_named_shorten, total, unit_named, unit_named_shorten, value)

            total = Decimal(total if total else default_total)
            if value:
                if value.endswith('%'):
                    salvage_value = Decimal(value[:-1]) / 100 * total
                else:
                    salvage_value = Decimal(value)
            else:
                salvage_value = default_value
            start_date = parse_date_liberally(date_start, {}) if date_start else default_start_date

            if num or unit_named or unit_named_shorten:
                num = int(num) if num else 1
                duration = get_duration(start_date, num, unit_named, unit_named_shorten)
            elif date_end:
                duration = (parse_date_liberally(date_end, {}) - start_date).days
            else:
                duration_math = CONFIG_STR_PATTERN_DURATION.match(default_duration_str)
                if duration_math:
                    num = duration_math.group('num')
                    unit_named = duration_math.group('unit_named')
                    unit_named_shorten = duration_math.group('unit_named_shorten')
                    num = int(num) if num else 1
                    duration = get_duration(start_date, num, unit_named, unit_named_shorten)
                else:
                    return None, PeriodicConfigError(None, 'fail to parse default duration: %s' % default_duration_str,
                                                     None)

            if step_num or step_named or step_unit_named or step_unit_named_shorten:
                if step_named:
                    steps = get_steps(start_date, duration, 1, step_named, None)
                else:
                    step_num = int(step_num) if step_num else 1
                    steps = get_steps(start_date, duration, step_num, step_unit_named, step_unit_named_shorten)
            else:
                step_match = CONFIG_STR_PATTERN_STEP.match(default_step_str)
                if step_match:
                    step_num = step_match.group('step_num')
                    step_unit_named = step_match.group('step_unit_named')
                    step_unit_named_shorten = step_match.group('step_unit_named_shorten')
                    step_named = step_match.group('step_named')
                    if step_named:
                        steps = get_steps(start_date, duration, 1, step_named, None)
                    else:
                        step_num = int(step_num) if step_num else 1
                        steps = get_steps(start_date, duration, step_num, step_unit_named, step_unit_named_shorten)
                else:
                    return None, PeriodicConfigError(None, 'fail to parse default steps: %s' % default_step_str, None)

            use_real_days_for_step_amount = next(
                (unit for unit in [step_named, step_unit_named, step_unit_named_shorten] if unit is not None),
                '').endswith('!')

            config_obj = PeriodicConfig(
                total=total,
                start=start_date,
                duration=duration,
                steps=steps,
                equal_amount=not use_real_days_for_step_amount,
                salvage_value=salvage_value,
                formula=formula if formula else default_formula_str
            )
            return config_obj, None
        else:
            return None, PeriodicConfigError(None, 'fail to parse: %s' % config, None)
    return None, None


def __print_config_match_result(date_end, date_start, formula, num, step_named, step_num, step_unit_named,
                                step_unit_named_shorten, total, unit_named, unit_named_shorten, value):
    # sys.stderr.write('total: %s\n' % total)
    # sys.stderr.write('num: %s\n' % num)
    # sys.stderr.write('unit_named: %s\n' % unit_named)
    # sys.stderr.write('unit_named_shorten: %s\n' % unit_named_shorten)
    # sys.stderr.write('date_start: %s\n' % date_start)
    # sys.stderr.write('date_end: %s\n' % date_end)
    # sys.stderr.write('step_num: %s\n' % step_num)
    # sys.stderr.write('step_unit_named: %s\n' % step_unit_named)
    # sys.stderr.write('step_unit_named_shorten: %s\n' % step_unit_named_shorten)
    # sys.stderr.write('step_named: %s\n' % step_named)
    # sys.stderr.write('value: %s\n' % value)
    # sys.stderr.write('formula: %s\n' % ear)
    pass
