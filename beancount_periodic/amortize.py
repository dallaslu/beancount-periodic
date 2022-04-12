from beancount.core import data, account, account_types
from beancount.parser import options

from .common.utils import build_steps
from .common.utils import create_meta
from .common.utils import select_periodic_posting_groups

__plugins__ = ('amortize',)


def amortize(entries: data.Entries, unused_options_map, config_string=""):
    new_entries = []
    errors = []
    account_types_option = options.get_account_types(unused_options_map)
    for entry in entries:
        if isinstance(entry, data.Transaction):
            selected_postings_groups = select_periodic_posting_groups(entry, 'amortize', errors)
            postings_to_insert_original_entry = []
            for selected_postings in selected_postings_groups:
                new_postings_config = []
                for i, config, config_str in selected_postings:
                    posting: data.Posting = entry.postings[i]
                    if account_types.is_account_type(account_types_option.expenses, posting.account):
                        new_account = str.join(account.sep,
                                               [account_types_option.equity, 'Amortization',
                                                account.sans_root(posting.account)])
                    elif account_types.is_account_type(account_types_option.income, posting.account):
                        new_account = str.join(account.sep,
                                               [account_types_option.equity, 'Received',
                                                account.sans_root(posting.account)])
                    else:
                        continue
                    total = config.total - config.salvage_value

                    new_posting_meta = create_meta(posting.meta, deletions=['amortize', 'narration'])

                    if total == posting.units.number:
                        entry.postings[i] = posting._replace(account=new_account)
                    else:
                        entry.postings[i] = posting._replace(
                            units=data.Amount(posting.units.number - total, posting.units.currency))
                        postings_to_insert_original_entry.append((
                            i + 1,
                            posting._replace(account=new_account,
                                             units=data.Amount(total, posting.units.currency),
                                             meta=new_posting_meta)
                        ))
                    new_postings_config.append((config, posting, new_account))

                new_entries.extend(
                    build_steps('amortize', entry, new_postings_config, positive=True,
                                narration_suffix='Amortized(%d/%d)'))

            postings_to_insert_original_entry.reverse()
            for i, element in postings_to_insert_original_entry:
                entry.postings.insert(i, element)

    if new_entries:
        entries.extend(new_entries)
        entries.sort(key=data.entry_sortkey)

    return entries, errors
