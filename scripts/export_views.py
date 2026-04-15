from pathlib import Path
import sqlite3
import csv

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data_build" / "pokemon_champions.sqlite"
EXPORTS = BASE / "data_build" / "exports"

QUERIES = {
    "pokemon_summary.csv": "SELECT * FROM v_pokemon_summary",
    "speed_table.csv": "SELECT * FROM v_speed_table",
    "move_users.csv": "SELECT * FROM v_move_users",
    "move_user_links.csv": "SELECT * FROM v_move_user_links",
    "pokemon_abilities_summary.csv": "SELECT * FROM v_pokemon_abilities_summary",
    "pokemon_moves_summary.csv": "SELECT * FROM v_pokemon_moves_summary",
    "pokemon_roles_summary.csv": "SELECT * FROM v_pokemon_roles_summary",
    "pokemon_archetypes_summary.csv": "SELECT * FROM v_pokemon_archetypes_summary",
    "team_builder_pool.csv": "SELECT * FROM v_team_builder_pool",
    "rain_candidates.csv": "SELECT * FROM v_rain_candidates",
    "sun_candidates.csv": "SELECT * FROM v_sun_candidates",
    "trick_room_candidates.csv": "SELECT * FROM v_trick_room_candidates",
    "charizard_answers.csv": "SELECT * FROM v_charizard_answers",
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
