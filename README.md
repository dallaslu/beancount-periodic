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
    depreciate: "5 Year /Yearly 120000"
```

Then this plugin will transform the transaction into:

```beancount
2022-03-31 * "Tesla" "Model X"
  Liababilies:CreditCard:0001    -200000 USD
  Assets:Car:ModelX
    depreciate: "5 Year /Yearly 120000"
  

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

At last, the balance of the account `Assets:Car:ModelX` is 80000 USD (200000 - 120000).
