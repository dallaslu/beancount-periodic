from decimal import Decimal, DecimalException
import math


def smart_place_num(ref: Decimal, div: Decimal):
    round_place_added = int(round(math.log10(abs(div)), 0)) + 1 if div != 0 else 0
    return min(max(- ref.as_tuple().exponent + round_place_added, 2), 6)


def round_and_remainder(target: Decimal, place_num):
    try:
      round_value = round(target, place_num)
      remainder = target - round_value
      return round_value, remainder
    except DecimalException as e:
      print(e)
      return target, 0


def remove_exponent_zero(num: Decimal):
    integral = num.to_integral()
    return integral if integral == num else num.normalize()
