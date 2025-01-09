# Beancount plugin to generate periodic transactions

## Usage

### Install

```python
pip3 install beancount-periodic
```
### Examples
#### `recur`

`main.bean`
```
plugin "beancount_periodic.recur"
```

```beancount
2022-03-31 * "Provider" "Net Fee"
  recur: "1 Year /Monthly"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Provider" "Net Fee Recurring(1/12)"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee

2022-04-30 * "Provider" "Net Fee Recurring(2/12)"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee

2022-05-31 * "Provider" "Net Fee Recurring(3/12)"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee

;...

2023-02-28 * "Provider" "Net Fee Recurring(12/12)"
  Liabilities:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee
```

### `split`

Similar to recur, except instead of just repeating the same transaction
multiple times, the original transaction is split into multiple, smaller
transactions that sum up to the same postings as the original.

`main.bean`
```
plugin "beancount_periodic.split"
```

```beancount
2025-01-01 * "Tax Estimate"
  split: "Year / Monthly"
  Liabilities:Tax
  Expenses:Tax:Income 4380.00 USD; 365*12
```

Then this plugin will transform the transaction into:

```beancount
; The amounts are not simply 365 USD per month, since some months are longer
; than others
2025-01-01 * "Tax Estimate Split(1/12)"
  Liabilities:Tax -372 USD
  Expenses:Tax:Income 372 USD

2025-02-01 * "Tax Estimate Split(2/12)"
  Liabilities:Tax -336 USD 
  Expenses:Tax:Income 336 USD

;...

2025-12-01 * "Tax Estimate Split(1/12)"
  Liabilities:Tax -372 USD
  Expenses:Tax:Income 372 USD

```

#### `amortize`

`main.bean`
```
plugin "beancount_periodic.amortize"
```

```beancount
2022-03-31 * "Landlord" "2022-04 Rent"
  Liabilities:CreditCard:0001    -12000 USD
  Expenses:Home:Rent
    amortize: "1 Year @2022-04-01 /Monthly"
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Landlord" "2022-04 Rent"
  Liabilities:CreditCard:0001    -12000 USD
  Equity:Amortization:Home:Rent
    amortize: "1 Year @2022-04-01 /Monthly"

2022-04-01 * "Landlord" "2022-04 Rent Amortized(1/12)"
  Equity:Amortization:Home:Rent    -1000 USD
  Expenses:Home:CommunicationFee

2022-05-01 * "Landlord" "2022-04 Rent Amortized(2/12)"
  Equity:Amortization:Home:Rent    -1000 USD
  Expenses:Home:CommunicationFee

2022-06-01 * "Landlord" "2022-04 Rent Amortized(3/12)"
  Equity:Amortization:Home:Rent    -1000 USD
  Expenses:Home:CommunicationFee

;...

2023-03-01 * "Landlord" "2022-04 Rent Amortized(12/12)"
  Equity:Amortization:Home:Rent    -1000 USD
  Expenses:Home:CommunicationFee
```

#### `depreciate`

`main.bean`
```
plugin "beancount_periodic.depreciate"
```

```beancount
2022-03-31 * "Tesla" "Model X"
  Liabilities:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly =80000"
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Tesla" "Model X"
  Liabilities:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly =80000"
  

2022-03-31 * "Tesla" "Model X Depreciated(1/5)"
  Assets:Car:ModelX    -24000 USD
  Expenses:Depreciation:Car:ModelX

2023-03-31 * "Tesla" "Model X Depreciated(2/5)"
  Assets:Car:ModelX    -24000 USD
  Expenses:Depreciation:Car:ModelX
;...

2026-03-31 * "Tesla" "Model X Depreciated(5/5)"
  Assets:Car:ModelX    -24000 USD
  Expenses:Depreciation:Car:ModelX
```

At last, the balance of the account `Assets:Car:ModelX` is 80000 USD.

To change the depreciation expense account, add the `depreciate_account` meta to the `open` statement of the depreciated asset account:
```beancount
1900-01-01 open Assets:Car:ModelX  EUR
  depreciate_account: "Expenses:Car:Value"

2022-03-31 * "Tesla" "Model X"
  Liabilities:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly =80000"


; generated transation
2022-03-31 * "Tesla" "Model X Depreciated(1/5)"
  Assets:Car:ModelX    -24000 USD
  Expenses:Car:Value

; ...
```

### Plugin Configuration
All plugins support the following configuration options, which can be specified in the `plugin` directive:
```beancount
plugin "beancount_periodic.recur" "{...}"
plugin "beancount_periodic.split" "{...}"
plugin "beancount_periodic.amortize" "{...}"
plugin "beancount_periodic.depreciate" "{...}"
```

#### generate_until
The `generate_until` configuration option prevents the plugin from generating transactions which occur after the given date.
It supports a ISO 8601 date string or the string literal 'today', which is replaced with today's date.

```beancount
; the plugin will only generate transactions until today
plugin "beancount_periodic.amortize" "{'generate_until':'today'}"

; the plugin will only generate transactions up until (including) 2025-01-01
plugin "beancount_periodic.amortize" "{'generate_until':'2025-01-01'}"
```

### Config string in meta

All settings follow the same rules. These are some examples:

```
"200000- 5 Years @2022-03-31 /Yearly *line =80000"
"200000- @2022-03-31~2027-03-30 /Year *line =80000"
"200000 - 5 Year @2022-03-31 /1 Year *line =80000"
"200000 - 5 Y @2022-03-31 /12 Months =80000"
"5Y @ 2022-03-31 / 12M = 80000"
"5Y / 12M =80000"
"5Y / 12M"
```

#### Total value

`200000-` means that the total value is `200000`.

The default value of total is same as the account of posting if missing.

#### Duration & Start date

`5 Years` means the duration is 5 years, and `@2022-03-31` means the first transformed transaction will start at 2022-03-31.

`5 Years @2022-03-31` is same as `@2022-03-31~2027-03-30`. You can also use `Day` and others.

```
"6 Months @2022-03-31"
"6 M @2022-03-31"
"5 Y @2022-03-31"
```

And the start date is optional, using the entry date as default value if missing. 

```
"6 Months"
```

The default value of duration is 1 month if missing.

#### Step

`Yearly` means one transformed transaction per year. You can also use `Daily`, `Monthly`, `Day` and others.

If step string ends with `!` means that the amount of every step will be calculated with real days. For example:

```beancount
2022-01-01 *
  Liabilities:CreditCard:0001    -365 USD
  Expenses:BlaBla
    amortize: "1 Year /Monthly!"
```

Then this plugin will transform the transaction into:

```beancount
2022-01-01 *
  Liabilities:CreditCard:0001    -365 USD
  Expenses:BlaBla
    amortize: "1 Year /Monthly!"

2022-01-01 * "Amortized(1/12)"
  Equity:Amortization:BlaBla    -31 USD
  Expenses:BlaBla

2022-02-01 * "Amortized(2/12)"
  Equity:Amortization:BlaBla    -28 USD
  Expenses:BlaBla

2022-03-01 * "Amortized(3/12)"
  Equity:Amortization:BlaBla    -31 USD
  Expenses:BlaBla

;...

2022-12-01 * "Amortized(12/12)"
  Equity:Amortization:BlaBla    -31 USD
  Expenses:BlaBla
```

The default value of step is 1 day if missing.

#### Formula(not yet implemented)

`*line` means that the formula is `line`. You can also use `linear`, `straight`, `line`, `load`, `work-load`, `accelerated-sum`, `sum`, `accelerated-declining`.

The default value of formula is `line`.

#### Salvage value

`=80000` means that the salvage value is 80000.

The default value of salvage value is 0 if missing.
