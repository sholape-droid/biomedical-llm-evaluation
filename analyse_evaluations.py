"""
Biomedical LLM Evaluation — analysis script
Author: Oluwasolape Ikuesan

What it does
1. Loads your rubric scores from evaluations.csv (pandas)
2. Cleans and validates the data (pandas)
3. Stores it in a SQLite database (SQL)
4. Answers evaluation questions with SQL queries
5. Saves summary tables and a chart to results/

Run:  python analyse_evaluations.py
Needs: pip install pandas matplotlib
"""

import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

DATA = Path("evaluations.csv")
DB = Path("evaluations.db")
OUT = Path("results")
OUT.mkdir(exist_ok=True)

SCORE_COLS = ["accuracy", "reasoning", "completeness", "safety"]  # each scored 1-4

# ---------- 1. Load ----------
df = pd.read_csv(DATA)
print(f"Loaded {len(df)} rows")

# ---------- 2. Clean and validate ----------
df.columns = df.columns.str.strip().str.lower()
df["model"] = df["model"].str.strip()
df["topic"] = df["topic"].str.strip().str.title()
df["error_type"] = df["error_type"].fillna("none").str.strip().str.lower()

before = len(df)
df = df.drop_duplicates(subset=["question_id", "model"])
print(f"Removed {before - len(df)} duplicate rows")

bad = df[~df[SCORE_COLS].isin([1, 2, 3, 4]).all(axis=1)]
if not bad.empty:
    print(f"WARNING: {len(bad)} rows have scores outside 1-4; they are excluded:")
    print(bad[["question_id", "model"]].to_string(index=False))
    df = df.drop(bad.index)

df["total_score"] = df[SCORE_COLS].sum(axis=1)  # out of 16

# ---------- 3. Store in SQLite ----------
with sqlite3.connect(DB) as con:
    df.to_sql("evaluations", con, if_exists="replace", index=False)

    # ---------- 4. SQL questions ----------
    queries = {
        "average_by_model": """
            SELECT model,
                   COUNT(*)                     AS responses,
                   ROUND(AVG(accuracy), 2)      AS avg_accuracy,
                   ROUND(AVG(reasoning), 2)     AS avg_reasoning,
                   ROUND(AVG(completeness), 2)  AS avg_completeness,
                   ROUND(AVG(safety), 2)        AS avg_safety,
                   ROUND(AVG(total_score), 2)   AS avg_total_out_of_16
            FROM evaluations
            GROUP BY model
            ORDER BY avg_total_out_of_16 DESC;""",
        "accuracy_by_topic": """
            SELECT topic, model, ROUND(AVG(accuracy), 2) AS avg_accuracy
            FROM evaluations
            GROUP BY topic, model
            ORDER BY topic, avg_accuracy DESC;""",
        "error_types": """
            SELECT model, error_type, COUNT(*) AS n
            FROM evaluations
            WHERE error_type <> 'none'
            GROUP BY model, error_type
            ORDER BY model, n DESC;""",
        "unsafe_or_wrong_answers": """
            SELECT question_id, topic, model, accuracy, safety, error_type, notes
            FROM evaluations
            WHERE accuracy <= 2 OR safety <= 2
            ORDER BY safety, accuracy;""",
    }

    results = {}
    for name, sql in queries.items():
        results[name] = pd.read_sql_query(sql, con)
        results[name].to_csv(OUT / f"{name}.csv", index=False)
        print(f"\n=== {name} ===")
        print(results[name].to_string(index=False))

# ---------- 5. Chart ----------
avg = results["average_by_model"].set_index("model")[
    ["avg_accuracy", "avg_reasoning", "avg_completeness", "avg_safety"]
]
ax = avg.T.plot(kind="bar", figsize=(8, 4.5), ylim=(0, 4), rot=0)
ax.set_title("Average rubric score by criterion (1-4)")
ax.set_ylabel("Mean score")
ax.set_xticklabels(["Accuracy", "Reasoning", "Completeness", "Safety"])
plt.tight_layout()
plt.savefig(OUT / "scores_by_model.png", dpi=150)
print(f"\nSaved tables and chart to {OUT}/")
