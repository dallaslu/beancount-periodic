import datetime
from decimal import Decimal

from beancount.core import data, account, account_types
from beancount.parser import options

from .common.utils import create_meta
from .common.utils import create_step_entry
from .common.config import parse, PluginConfig

__plugins__ = ('recur',)


def recur(entries: data.Entries, unused_options_map, config_string=""):
    plugin_config = PluginConfig.from_string(config_string)
    new_entries = []
    errors = []
    account_types_option = options.get_account_types(unused_options_map)
    entries_to_remove = []
    for entry in entries:
        if isinstance(entry, data.Transaction):
            entry_config_str = entry.meta.get('recur') if entry.meta else None
            if entry_config_str:
                entry_config, entry_config_err = parse(entry_config_str, Decimal('0'), entry.date, 'M', 'D', Decimal('0'),'line')

                if entry_config:
                    new_entry_meta = create_meta(entry.meta, deletions=     ['recur', 'narration'])
                    start_date = entry_config.start
                    new_entry_narration_template = (entry.narration + ' ' if entry.narration else '') + 'Recurring(%d/%d)'
                    
                    for step_i, (step_days, step_ratio) in enumerate(entry_config.steps):
                        # skip all steps that are past the given date
                        if plugin_config.generate_until and start_date > plugin_config.generate_until:
                            break

                        new_entry_narration = new_entry_narration_template % (step_i + 1, len(entry_config.steps))
                        end_date = start_date + datetime.timedelta(days=step_days)

                        new_entry = create_step_entry(entry, start_date, new_entry_meta, new_entry_narration, entry.postings)
                        new_entries.append(new_entry)
                        start_date = end_date
                        pass
                    pass
                    entries_to_remove.append(entry)
                else:
                    errors.append(entry_config_err._replace(source=entry.meta))
                    continue
                pass
            pass

    for entry_to_remove in entries_to_remove:
        entries.remove(entry_to_remove)

    if new_entries:
        entries.extend(new_entries)
        entries.sort(key=data.entry_sortkey)

    return entries, errors
