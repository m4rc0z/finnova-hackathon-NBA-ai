# Skill: Finnova NBA Hackathon Backend

Knowledge of the hackathon backend API used to gather customer context for
Next Best Action (NBA) evaluation. Use the `list_collection` / `get_item`
tools (see `src/tools/backend_tools.py`) instead of calling the HTTP API
directly.

## Base URL

`BACKEND_BASE_URL` env var, defaults to `http://localhost:8000`. No
authentication is required.

## Collections

One of: `accounts`, `account-balances`, `employers`, `events`,
`transactions`, `interactions`, `individuals`, `individual-states`.

| Collection | ID field |
|---|---|
| accounts | account_id |
| account-balances | account_id |
| employers | employer_id |
| events | event_id |
| transactions | txn_id |
| interactions | interaction_id |
| individuals | individual_id |
| individual-states | individual_id |

## Endpoints

- `GET /api/v1/{collection}?limit=&offset=&run_id=&period=&individual_id=&account_id=`
  → `{"collection", "total", "offset", "limit", "items": [...]}`
- `GET /api/v1/{collection}/{item_id}?run_id=`
  → a single item, or `{"items": [...]}` if multiple periods match
  (e.g. account-balances over time).

## Key fields per collection

- **individuals**: individual_id, run_id, period, income_chf, employer_id,
  marital_status, household_id, education_level, employment.
- **individual-states**: individual_id, run_id, birth_period, sex,
  death_period, attributes (age, canton, plz, city, products[],
  interests{}, values{}, bigfive{}, risk_appetite, wallet_share,
  health_score, life_sat, stress, owns_property, mortgage_*, ...).
  This is the richest source of customer profile data.
- **accounts**: account_id, run_id, individual_id, kind, opened_period,
  closed_period, product_name.
- **account-balances**: account_id, run_id, period, balance_chf.
- **transactions**: txn_id, run_id, account_id, period, amount_chf,
  category, source_event, day_of_month.
- **interactions**: interaction_id, run_id, individual_id, period, type,
  channel, direction, category, subject, priority, status, resolution,
  product, stage, probability, expected_value, generated_by. This is the
  main source of past NBA-relevant advisor interactions — useful both as
  input context and as ground truth for evaluation.
- **events**: event_id, run_id, individual_id, counterparty, period, type,
  effects, generated_by.
- **employers**: employer_id, run_id, sector, region, size_band.

## Typical NBA evaluation workflow

1. Look up the individual's profile via `individuals` + `individual-states`.
2. Gather their `accounts`, recent `transactions`, and `interactions`
   history for context.
3. Recommend the next best action (e.g. an offer/product or advisory
   action), grounded only in the retrieved data.
