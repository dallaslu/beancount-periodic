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
  Liababilies:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Provider" "Net Fee Recurring(1/12)"
  Liababilies:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee

2022-04-30 * "Provider" "Net Fee Recurring(2/12)"
  Liababilies:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee

2022-05-31 * "Provider" "Net Fee Recurring(3/12)"
  Liababilies:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee

;...

2023-02-28 * "Provider" "Net Fee Recurring(12/12)"
  Liababilies:CreditCard:0001    -50 USD
  Expenses:Home:CommunicationFee
```

#### `amortize`

`main.bean`
```
plugin "beancount_periodic.amortize"
```

```beancount
2022-03-31 * "Landlord" "2022-04 Rent"
  Liababilies:CreditCard:0001    -12000 USD
  Expenses:Home:Rent
    amortize: "1 Year @2022-04-01 /Monthly"
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Landlord" "2022-04 Rent"
  Liababilies:CreditCard:0001    -12000 USD
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
  Liababilies:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly =80000"
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Tesla" "Model X"
  Liababilies:CreditCard:0001    -200000 USD
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
  Liababilies:CreditCard:0001    -365 USD
  Expenses:BlaBla
    amortize: "1 Year /Monthly!"
```

Then this plugin will transform the transaction into:

```beancount
2022-01-01 *
  Liababilies:CreditCard:0001    -365 USD
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