import datetime
from decimal import Decimal

from beancount.core import data

from .config import parse
from .number import remove_exponent_zero
from .number import round_and_remainder
from .number import smart_place_num


def select_periodic_posting_groups(entry, meta_name, errors):
    config_group_postings = {}
    entry_config_str = entry.meta.get(meta_name) if entry.meta else None
    if entry_config_str:
        entry_config, entry_config_err = parse(entry_config_str, Decimal('0'), entry.date, 'M', 'D', Decimal('0'),
                                               'line')
        if entry_config:
            config_group_postings[entry_config_str] = []
        else:
            errors.append(entry_config_err._replace(source=entry.meta))

    for i, posting in enumerate(entry.postings):
        config_str = posting.meta.get(meta_name) if posting.meta else None
        if config_str:
            config, config_err = parse(config_str, posting.units.number, entry.date, 'M', 'D', Decimal('0'),
                                       'line')
            if config:
                if config_str not in config_group_postings:
                    config_group_postings[config_str] = []
                config_group_postings[config_str].append((i, config, config_str))
            else:
                errors.append(config_err._replace(source=posting.meta))
                continue
        elif entry_config_str and entry_config:
            config_group_postings[entry_config_str].append(
                (i, entry_config._replace(total=posting.units.number), entry_config_str))

    return [v for k, v in config_group_postings.items()]


def build_steps(meta_key, entry, new_postings_config, positive=True,
                narration_suffix='(% d / % d)'):
    new_entries = []

    if len(new_postings_config) == 1:
        posting = new_postings_config[0][1];
        narration = next(
            n for n in [posting.meta.get('narration') if posting.meta else None, entry.narration]
            if n is not None)
        new_entry_meta = create_meta(entry.meta, deletions=[meta_key],
                                     extends={'lineno': posting.meta['lineno']})
    else:
        narration = entry.narration
        new_entry_meta = create_meta(entry.meta, deletions=[meta_key])

    new_entry_narration_template = (narration + ' ' if narration else '') + narration_suffix

    for config, posting, new_account in new_postings_config:
        total = config.total - config.salvage_value
        amount_remainder = remove_exponent_zero(total)
        start_date = config.start

        new_posting_meta = create_meta(posting.meta, deletions=[meta_key, 'narration'])

        if config.equal_amount:
            place_num = smart_place_num(total, len(config.steps))
        else:
            place_num = smart_place_num(total, config.duration)

        round_remainder = Decimal('0')
        step_num = sum_step_ratio(config)
        for step_i, (step_days, step_ratio) in enumerate(config.steps):
            if step_i < len(config.steps) - 1:
                if config.equal_amount:
                    step_amount, remainder = round_and_remainder(step_ratio * total / step_num, place_num)
                else:
                    step_amount, remainder = round_and_remainder(Decimal(step_days) / config.duration * total,
                                                                 place_num)

                round_remainder_amount, round_remainder_remainder = round_and_remainder(round_remainder,
                                                                                        place_num)
                if abs(round_remainder_amount) > 0:
                    step_amount += round_remainder_amount
                    round_remainder = round_remainder_remainder

                round_remainder += remainder
                amount_remainder -= step_amount
            else:  # the last step
                step_amount = amount_remainder
            step_amount = remove_exponent_zero(step_amount)
            end_date = start_date + datetime.timedelta(days=step_days)

            new_entry_narration = new_entry_narration_template % (step_i + 1, len(config.steps))
            new_postings = create_step_postings(posting,
                                                new_account, new_posting_meta,
                                                step_amount if positive else -step_amount)
            if len(new_entries) > step_i and new_entries[step_i]:
                new_entry = new_entries[step_i]
                combine_to_entry_posting(new_entry, new_postings, new_account)
            else:
                new_entry = create_step_entry(entry, start_date, new_entry_meta, new_entry_narration, new_postings)
                new_entries.append(new_entry)
            start_date = end_date

    return new_entries


def combine_to_entry_posting(entry: data.Transaction, new_postings, new_account):
    existing_index = next(
        (i for i, posting in enumerate(entry.postings) if posting.account == new_account), None)
    if existing_index is not None:
        new_postings_to_extended = []
        for new_posting in new_postings:
            existing_posting: data.Posting = entry.postings[existing_index]
            if new_posting.account == new_account \
                    and new_posting.units.currency == existing_posting.units.currency \
                    and new_posting.cost == existing_posting.cost \
                    and new_posting.price == existing_posting.price:
                entry.postings[existing_index] = existing_posting._replace(
                    units=data.Amount(existing_posting.units.number + new_posting.units.number,
                                      existing_posting.units.currency))
            else:
                new_postings_to_extended.append(new_posting)
        entry.postings.extend(new_postings_to_extended)
    else:
        entry.postings.extend(new_postings)


def sum_step_ratio(config):
    step_num = Decimal('0')
    for step_days, step_ratio in config.steps:
        step_num += step_ratio
    return step_num


def create_step_postings(posting_template: data.Posting,
                         new_account,
                         posting_meta, amount):
    amount = remove_exponent_zero(amount)
    new_postings = [data.Posting(
        account=new_account,
        units=data.Amount(-amount, posting_template.units.currency),
        cost=posting_template.cost,
        price=posting_template.price,
        flag=posting_template.flag,
        meta=data.new_metadata(posting_template.meta['filename'], posting_template.meta['lineno'])
    ), posting_template._replace(units=data.Amount(amount, posting_template.units.currency),
                                 meta=posting_meta)]

    return new_postings


def create_step_entry(entry_template, entry_date, entry_meta, entry_narration, entry_postings):
    new_entry = data.Transaction(
        date=entry_date,
        meta=entry_meta,
        flag=entry_template.flag,
        payee=entry_template.payee,
        narration=entry_narration,
        tags=entry_template.tags,
        links=entry_template.links,
        postings=entry_postings
    )
    return new_entry


def create_meta(template_meta, deletions, extends={}):
    new_meta = {}
    new_meta.update(template_meta)
    for key in deletions:
        if key in new_meta:
            del new_meta[key]
    for k, v in extends.items():
        new_meta[k] = v
    return new_meta
