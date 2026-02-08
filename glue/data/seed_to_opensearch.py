"""Bulk-index strategy seed documents into OpenSearch.

Reads strategy documents from a JSON file and indexes them into the
'strategies' index using the OpenSearch _bulk API.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "strategies"
BATCH_SIZE = 50
DEFAULT_JSON_PATH = Path(__file__).resolve().parents[2] / "volumes" / "data" / "strategy_seed_docs.json"


def load_docs(path: Path) -> list[dict]:
    """Load strategy documents from JSON file."""
    with open(path) as f:
        return json.load(f)


def bulk_index(docs: list[dict], base_url: str, index: str, batch_size: int = BATCH_SIZE) -> int:
    """Bulk index documents into OpenSearch.

    Returns the number of successfully indexed documents.
    """
    total_ok = 0
    total_err = 0

    for start in range(0, len(docs), batch_size):
        batch = docs[start : start + batch_size]
        lines: list[str] = []
        for doc in batch:
            doc_id = doc.pop("_id", doc.get("doc_id", ""))
            action = json.dumps({"index": {"_index": index, "_id": doc_id}})
            body = json.dumps(doc)
            lines.append(action)
            lines.append(body)

        payload = "\n".join(lines) + "\n"
        resp = requests.post(
            f"{base_url}/_bulk",
            headers={"Content-Type": "application/x-ndjson"},
            data=payload,
            timeout=30,
        )
        resp.raise_for_status()

        result = resp.json()
        if result.get("errors"):
            for item in result["items"]:
                op = item.get("index", {})
                if op.get("error"):
                    total_err += 1
                    print(f"  ERROR indexing {op.get('_id', '?')}: {op['error'].get('reason', '')}", file=sys.stderr)
                else:
                    total_ok += 1
        else:
            total_ok += len(batch)

        batch_end = min(start + batch_size, len(docs))
        print(f"  Batch {start+1}-{batch_end}/{len(docs)}: indexed OK")

    if total_err:
        print(f"[seed_to_opensearch] WARNING: {total_err} documents had errors", file=sys.stderr)

    return total_ok


def refresh_index(base_url: str, index: str) -> None:
    """Force refresh the index so documents are searchable."""
    resp = requests.post(f"{base_url}/{index}/_refresh", timeout=10)
    resp.raise_for_status()
    print(f"[seed_to_opensearch] Index '{index}' refreshed.")


def get_doc_count(base_url: str, index: str) -> int:
    """Get current document count in index."""
    resp = requests.get(f"{base_url}/{index}/_count", timeout=10)
    resp.raise_for_status()
    return resp.json().get("count", 0)


def main() -> None:
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_JSON_PATH

    if not json_path.exists():
        print(f"[seed_to_opensearch] ERROR: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    docs = load_docs(json_path)
    print(f"[seed_to_opensearch] Loaded {len(docs)} documents from {json_path}")

    indexed = bulk_index(docs, OPENSEARCH_URL, INDEX_NAME)
    refresh_index(OPENSEARCH_URL, INDEX_NAME)

    count = get_doc_count(OPENSEARCH_URL, INDEX_NAME)
    print(f"[seed_to_opensearch] Complete: {indexed} indexed, {count} total in '{INDEX_NAME}'")


if __name__ == "__main__":
    main()
