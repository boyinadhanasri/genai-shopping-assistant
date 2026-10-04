"""
Analytics Service for GenAI Shopping Assistant

Tracks search events and product clicks in data/search_logs.csv.
Provides metrics via GET /api/analytics:
- total searches
- total clicks
- recent logs
- top queries
- top clicked products
"""

import os
import csv
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "search_logs.csv"

FIELDNAMES = ["timestamp", "query", "clicked_product", "results_count"]


def ensure_log_file():
    """Initializes search_logs.csv with headers if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_search_event(query: str, results_count: int, clicked_product: Optional[str] = None):
    """Appends a search or click event to search_logs.csv."""
    try:
        ensure_log_file()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow({
                "timestamp": timestamp,
                "query": query or "",
                "clicked_product": clicked_product or "",
                "results_count": results_count,
            })
    except Exception as e:
        # Non-blocking logging
        print(f"Failed to log search event: {e}")


def get_analytics_summary() -> Dict[str, Any]:
    """Generates analytics report from data/search_logs.csv."""
    ensure_log_file()
    try:
        df = pd.read_csv(LOG_FILE).fillna("")
    except Exception:
        return {
            "total_searches": 0,
            "total_clicks": 0,
            "top_queries": [],
            "top_clicked_products": [],
            "recent_logs": [],
        }

    total_records = len(df)
    clicks_df = df[df["clicked_product"] != ""]
    total_clicks = len(clicks_df)

    # Top queries
    queries_df = df[df["query"] != ""]
    top_queries = []
    if not queries_df.empty:
        counts = queries_df["query"].value_counts().head(5)
        top_queries = [{"query": q, "count": int(c)} for q, c in counts.items()]

    # Top clicked products
    top_clicked = []
    if not clicks_df.empty:
        counts = clicks_df["clicked_product"].value_counts().head(5)
        top_clicked = [{"product_id": p, "clicks": int(c)} for p, c in counts.items()]

    # Recent 15 logs
    recent_logs = df.tail(15).to_dict(orient="records")
    recent_logs.reverse()

    return {
        "total_searches": total_records,
        "total_clicks": total_clicks,
        "top_queries": top_queries,
        "top_clicked_products": top_clicked,
        "recent_logs": recent_logs,
    }


if __name__ == "__main__":
    ensure_log_file()
    log_search_event("samsung phone under 20000", 6)
    log_search_event("samsung phone under 20000", 6, "FKP0000100")
    print(get_analytics_summary())
