import datetime
from decimal import Decimal
from typing import List, Tuple, Optional

from beancount.core import data, account, account_types
from beancount.parser import options

from .common.utils import create_meta
from .common.utils import create_step_entry
from .common.config import parse, PluginConfig, PeriodicConfig

__plugins__ = ("split",)


def _create_split_step(entry, step_i, total_steps, date, step_multiplier, entry_meta):
    new_entry_narration = (entry.narration + " " if entry.narration else "") + f"Split({step_i + 1}/{total_steps})"
    
    return create_step_entry(
        entry,
        date,
        entry_meta,
        new_entry_narration,
        [
            posting._replace(
                units=data.Amount(
                    posting.units.number * step_multiplier,
                    posting.units.currency,
                )
            )
            for posting in entry.postings
        ],
    )


def _split_entry(entry: data.Transaction, plugin_config: PluginConfig) -> Tuple[List[data.Transaction], List[str]]:
    entry_config, entry_config_err = parse(
        entry.meta.get("split"),
        Decimal("0"),
        entry.date,
        "M",
        "D",
        Decimal("0"),
        "line",
    )
    if not entry_config:
        return [], [entry_config_err._replace(source=entry.meta)]

    new_entries = []
    new_entry_meta = create_meta(entry.meta, deletions=["split", "narration"])
    start_date = entry_config.start
    total_days = Decimal(sum(step_days for (step_days, _) in entry_config.steps))

    for step_i, (step_days, step_ratio) in enumerate(entry_config.steps):
        # skip all steps that are past the given date
        if plugin_config.generate_until and start_date > plugin_config.generate_until:
            break

        new_entry = _create_split_step(
            entry,
            step_i,
            len(entry_config.steps),
            start_date,
            step_days / total_days,
            new_entry_meta,
        )
        new_entries.append(new_entry)
        start_date += datetime.timedelta(days=step_days)

    return new_entries, []


def split(entries: data.Entries, unused_options_map, config_string=""):
    plugin_config = PluginConfig.from_string(config_string)
    new_entries = []
    errors = []
    entries_to_remove = []
    splittable_entries = [
        entry
        for entry in entries
        if isinstance(entry, data.Transaction) and entry.meta and "split" in entry.meta
    ]

    for entry in splittable_entries:
        entry_new_entries, entry_errors = _split_entry(entry, plugin_config)
        new_entries.extend(entry_new_entries)
        errors.extend(entry_errors)
        if entry_new_entries:  # Only remove the original entry if we created new ones
            entries_to_remove.append(entry)

    for entry_to_remove in entries_to_remove:
        entries.remove(entry_to_remove)

    if new_entries:
        entries.extend(new_entries)
        entries.sort(key=data.entry_sortkey)

    return entries, errors
