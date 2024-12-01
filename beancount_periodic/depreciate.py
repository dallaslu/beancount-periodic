from typing import Dict, Tuple

import beancount.core.getters
from beancount.core import data, account, account_types
from beancount.parser import options

from .common.utils import build_steps
from .common.utils import select_periodic_posting_groups

__plugins__ = ('depreciate',)


def get_depreciation_account(
        accounts_open_close: Dict[str, Tuple[beancount.core.data.Open, beancount.core.data.Close]],
        expenses_parent: str,
        asset_account: beancount.core.data.Account,
) -> str:
    new_account = str.join(
        account.sep,
        [expenses_parent, 'Depreciation', account.sans_root(asset_account)]
    )

    asset_account_open_statement = accounts_open_close.get(asset_account, None)[0]
    open_meta = asset_account_open_statement.meta
    depreciate_account = open_meta.get('depreciate_account', None)

    if depreciate_account:
        return depreciate_account

    return new_account


def depreciate(entries: data.Entries, unused_options_map, config_string=""):
    new_entries = []
    errors = []
    account_types_option = options.get_account_types(unused_options_map)
    accounts_open_close = beancount.core.getters.get_account_open_close(entries)
    for entry in entries:
        if isinstance(entry, data.Transaction):
            selected_postings_groups = select_periodic_posting_groups(entry, 'depreciate', errors)
            for selected_postings in selected_postings_groups:
                new_postings_config = []
                for i, config, config_str in selected_postings:
                    posting: data.Posting = entry.postings[i]
                    if account_types.is_account_type(account_types_option.assets, posting.account):
                        new_account = get_depreciation_account(
                            accounts_open_close,
                            account_types_option.expenses,
                            posting.account
                        )
                    else:
                        continue
                    new_postings_config.append((config, posting, new_account))

                new_entries.extend(
                    build_steps('depreciate', entry, new_postings_config,
                                positive=False,
                                narration_suffix='Depreciated(%d/%d)'))

    if new_entries:
        entries.extend(new_entries)
        entries.sort(key=data.entry_sortkey)

    return entries, errors
