"""One-off script: evaluate the NBA agent over a batch of individual_ids and
summarize the diversity of recommended actions/products (manual QA aid, not
part of the app)."""

import json
from collections import Counter

from src.agents.nba_agent import build_agent, evaluate_individual

IDS = [
    "0002546a-e1aa-4023-b1e2-01b8e4c6fb93",
    "0003b06e-7032-448b-992c-fe386d56da56",
    "000e852c-3e17-4561-871a-6bf12f8b557c",
    "0014a7c6-6ece-49d8-a8bc-1ed8ac66e206",
    "002b828d-1e2f-4b22-8776-52e7d51b0351",
    "0038214e-6e63-4679-a712-90fe0f03c570",
    "00434cb7-8f24-4bf2-9d8d-7afc8c03fc8d",
    "00446816-0fe1-4301-a0f0-8f2c2595b49b",
    "004e01c6-350a-46a4-b230-3da252e732d8",
    "005065f3-a585-4d7f-8fc5-c1c25ff1f332",
    "00512e0a-d8ca-40bb-bbdb-cf75a5c06d16",
    "00559047-a455-45b5-9493-9390b447fa0b",
    "00720b86-35df-466c-98a4-379fe4049355",
    "007f88a4-50b4-4612-9fab-ddfadda87347",
    "0086f6b9-0507-4936-b286-4787747004d7",
    "0089d95b-d03b-40b4-9a59-e83ffe172407",
    "008b377e-c24e-47b5-85a7-01e73ec6267c",
    "00a6e674-f417-4b2a-805f-8b297a0161ec",
    "00b81d95-143c-48f4-93b5-e370e7260143",
    "00bbd587-423a-4112-8b03-f164b330a653",
]


def main():
    agent = build_agent("openai")
    results = []
    for i, individual_id in enumerate(IDS, 1):
        print(f"[{i}/{len(IDS)}] evaluating {individual_id} ...", flush=True)
        result = evaluate_individual(agent, individual_id)
        results.append(result)

    with open("/tmp/nba_batch_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    top_actions = Counter()
    top_products = Counter()
    all_actions = Counter()
    empty_or_error = 0
    for r in results:
        recs = r.get("recommendations")
        if not recs:
            empty_or_error += 1
            continue
        top_actions[recs[0].get("action")] += 1
        top_products[recs[0].get("product_name")] += 1
        for rec in recs:
            all_actions[rec.get("action")] += 1

    print("\n=== Top-1 action distribution ===")
    for action, count in top_actions.most_common():
        print(f"{action}: {count}")

    print("\n=== Top-1 product distribution ===")
    for product, count in top_products.most_common():
        print(f"{product}: {count}")

    print("\n=== All recommended actions (any rank) ===")
    for action, count in all_actions.most_common():
        print(f"{action}: {count}")

    print(f"\nEmpty/error results: {empty_or_error}/{len(IDS)}")


if __name__ == "__main__":
    main()
