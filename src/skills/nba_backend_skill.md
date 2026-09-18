# Skill: Finnova NBA Hackathon Backend

Knowledge of the hackathon backend API used to gather customer context for
Next Best Action (NBA) evaluation. Use the tools in
`src/tools/backend_tools.py` instead of calling the HTTP API directly.

## Base URL

`BACKEND_BASE_URL` env var, defaults to `http://localhost:8000`. No
authentication is required. All endpoints can be slow or briefly
unreachable; the client handles timeouts/HTTP errors and returns an
`{"error": ...}` dict instead of raising.

## Status endpoints

- `GET /health`, `GET /api/status` → `{"status": "ok", "data": "loaded"|"loading"}`

## Product catalog

`accounts.product_name` holds the concrete product a customer already
owns; `accounts.kind` is its category. Use exact `product_name` matches
(not just the category) to detect duplicates before recommending an
action - e.g. don't propose `offer_pillar3a` if the customer already has
a "Säule 3a-Konto" *or* a "Säule 3a Fondssparplan" *or* a
"Lebensversicherung 3a".

| `kind` | Products (`product_name`) | Related action |
|---|---|---|
| checking | Privatkonto, Jugendkonto, Geschaeftskonto * | (base account, not an "offer") |
| savings | Sparkonto, Sparkonto Young, Jugendsparkonto, Anlagesparkonto | `offer_savings_account` |
| pillar3a | Säule 3a-Konto, Säule 3a Fondssparplan, Lebensversicherung 3a | `offer_pillar3a` |
| investment | Anlagekonto, Fondssparplan, Wertschriftendepot | `offer_investment` |
| mortgage | Festhypothek | `offer_mortgage` |
| credit_card | Kreditkarte Visa/Mastercard | `upsell_premium` |
| insurance | Rechtsschutzversicherung | `upsell_premium` / `financial_advice` |
| - | Freizügigkeitskonto (vested benefits / 2nd-pillar account) | `retirement_planning` |

`Jugendkonto`/`Jugendsparkonto`/`Sparkonto Young` are the youth-appropriate
products - these are the only savings-type products to consider for
minors (see Jugendschutz rule below).

## Customer features (preferred for analysis)

`GET /api/v1/individuals/{individual_id}/features` →
`{"detail": "Individual not found"}` for unknown customers, otherwise a
flat dict including at least:

`individual_id, age, income_chf, employment, marital_status, num_accounts,
has_savings, has_checking, has_pillar3a, unique_products,
total_balance_chf, avg_balance_chf, min_balance_chf, max_balance_chf,
has_negative_balance, total_spent_chf, total_income_chf,
num_transactions, unique_categories, top_spend_category,
num_interactions, num_open_interactions, preferred_channel, stress,
canton, is_deceased, ...` plus a `product_inventory` dict:
`{"product_names": [...], "kinds": [...], "account_count", "has_pillar3a",
"has_savings", "has_mortgage", "has_investment"}` - use
`product_inventory.product_names` for exact duplicate-product checks
(more reliable than the individual `has_*` flags alone).

These are already aggregated across the customer's accounts/transactions -
do not resum raw historical balances yourself; use `total_balance_chf`
(latest balance per account, summed) as the current balance.

## Recommendations (preferred for NBA)

`GET /api/v1/individuals/{individual_id}/recommendations` →
```json
{
  "individual_id": "CUSTOMER_ID",
  "recommendations": [
    {"action": "retirement_planning", "score": 75, "reasons": ["..."]}
  ],
  "product_suggestions": [
    {"action": "retirement_planning", "product_name": "Freizügigkeitskonto", "score": 75, "reasons": ["..."]}
  ]
}
```
`{"detail": "Individual not found"}` for unknown customers. `action` is
one of: `offer_savings_account`, `offer_pillar3a`, `offer_mortgage`,
`offer_investment`, `retention_call`, `upsell_premium`, `financial_advice`,
`retirement_planning`. Both lists are already sorted by score (highest
first). Use `product_suggestions` to attach a concrete `product_name` to
each chosen action (fall back to the product catalog table above if an
action has no matching entry); pick the top 1-3 recommendations and cite
their `reasons`. `product_suggestions` can list actions the customer
already owns a matching product for (e.g. a low-score
`offer_savings_account` even when `has_savings` is true) - always
cross-check against `product_inventory`/`has_*` before accepting a
suggestion, per the compliance rules below.

## ML model status

A logistic-regression model was trained offline as a baseline but is
**not** exposed via an API yet. Do not call `/api/v1/individuals/{id}/ml-recommendations`
- it does not exist yet. The current `/recommendations` endpoint always
uses the explainable, rule-based scoring above, not the ML model.

Training stats show the model is not production-ready: 64,368 examples
but only 3 positive labels (test set: 0 positives, conversion rate 0.0,
top-10 precision 0.0) - too few customers have a complete follow-up
window with a matching event/transaction in the next 7 periods. Mention
this limitation if asked about ML-based scoring, and rely only on the
rule-based recommendations for now.

## Raw collections (for supplementary evidence only)

`GET /api/v1/{collection}?limit=&offset=&run_id=&period=&individual_id=&account_id=`
→ `{"collection", "total", "offset", "limit", "items": [...]}`

`GET /api/v1/{collection}/{item_id}?run_id=` → a single item, or
`{"items": [...]}` if multiple periods match (e.g. account-balances over
time - these are historical snapshots, never sum them as a current total).

Collections: `accounts`, `account-balances`, `employers`, `events`,
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

Never confuse `account_id` and `individual_id` - always look up an account
first if you only have an `account_id`, to find its `individual_id`.

## Compliance rules the agent must apply

- **No duplicate products**: never propose a product the customer already
  holds. Check `features.product_inventory.product_names` (exact match)
  and `has_savings`/`has_checking`/`has_pillar3a` as a first signal, then
  confirm against the product catalog above (e.g. don't suggest
  `offer_pillar3a` if the customer already has any of "Säule 3a-Konto",
  "Säule 3a Fondssparplan" or "Lebensversicherung 3a") before accepting a
  `product_suggestions` entry or proposing `offer_savings_account`,
  `offer_pillar3a`, `offer_investment` or `offer_mortgage`.
- **Jugendschutz (minors, age < 18)**: minors have limited legal capacity
  and need parental/legal-guardian consent for binding financial products.
  Only youth-appropriate actions are allowed (e.g. a youth savings account
  or `financial_advice`); never `offer_mortgage`, `offer_investment`,
  `offer_pillar3a`, `upsell_premium` or `retirement_planning`. If `age` is
  missing, treat the customer cautiously rather than assuming adulthood.
- **Regulatory checks**: `offer_investment` requires no negative balances
  and no distress signals (suitability/Eignungsprüfung); `offer_mortgage`
  requires evidence of affordability (Verschuldungsprüfung) - negative
  balances or retention signals disqualify it. Never fabricate customer
  facts; flag missing key data (age, income, employment) instead of
  guessing. All output remains a non-binding suggestion subject to the
  bank's formal advisory/compliance process.

## Typical NBA evaluation workflow

1. Check `/health` or `/api/status` once per session.
2. Load `get_customer_features(individual_id)`. If not found, report this
   clearly instead of guessing.
3. Optionally validate accounts/products via `list_collection("accounts",
   individual_id=...)` for extra evidence.
4. Load `get_recommendations(individual_id)`.
5. Select the top 1-3 recommendations by score and explain each with its
   `reasons`, grounded only in retrieved data. Missing data must never be
   treated as a negative fact (e.g. no interactions found ≠ "no interest").

