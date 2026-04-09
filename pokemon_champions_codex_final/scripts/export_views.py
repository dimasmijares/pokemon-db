from pathlib import Path
import sqlite3
import csv

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data_build" / "pokemon_champions.sqlite"
EXPORTS = BASE / "data_build" / "exports"

QUERIES = {
    "pokemon_summary.csv": "SELECT * FROM pokemon",
    "types.csv": "SELECT * FROM types",
    "sources.csv": "SELECT * FROM sources",
}

def export_query(conn: sqlite3.Connection, filename: str, query: str) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]
    with (EXPORTS / filename).open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def main():
    conn = sqlite3.connect(DB)
    for filename, query in QUERIES.items():
        export_query(conn, filename, query)
        print(f"[OK] Exportado: {filename}")
    conn.close()

if __name__ == "__main__":
    main()
