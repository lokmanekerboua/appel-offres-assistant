import json
from pathlib import Path

REFERENCES_PATH = Path(__file__).parent.parent / "data" / "references.json"


def search_past_references(keywords: list[str]) -> list[dict]:
    """
    Simple keyword-overlap search against the reference project dataset.
    Deliberately not a real vector search — good enough to demonstrate
    the tool-calling flow without the setup cost of embeddings.
    """
    with open(REFERENCES_PATH, encoding="utf-8") as f:
        references = json.load(f)

    keywords_lower = {k.lower() for k in keywords}
    results = []

    for ref in references:
        ref_keywords = {k.lower() for k in ref["keywords"]}
        overlap = keywords_lower & ref_keywords
        if overlap:
            score = round(len(overlap) / len(ref_keywords), 2)
            results.append(
                {
                    "project_name": ref["project_name"],
                    "client": ref["client"],
                    "relevance_score": score,
                }
            )

    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    return results[:5]