from pathlib import Path
import sqlite3
import csv

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data_raw"
BUILD = BASE / "data_build"
DB = BUILD / "pokemon_champions.sqlite"

def ensure_dirs():
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "exports").mkdir(parents=True, exist_ok=True)

def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = OFF;
    DROP TABLE IF EXISTS pokemon;
    DROP TABLE IF EXISTS stats_base;
    DROP TABLE IF EXISTS abilities;
    DROP TABLE IF EXISTS pokemon_abilities;
    DROP TABLE IF EXISTS moves;
    DROP TABLE IF EXISTS pokemon_moves;
    DROP TABLE IF EXISTS mega_forms;
    DROP TABLE IF EXISTS items;
    DROP TABLE IF EXISTS seasons_rules;
    DROP TABLE IF EXISTS tiers;
    DROP TABLE IF EXISTS roles;
    DROP TABLE IF EXISTS pokemon_roles;
    DROP TABLE IF EXISTS archetypes;
    DROP TABLE IF EXISTS pokemon_archetypes;
    DROP TABLE IF EXISTS cores;
    DROP TABLE IF EXISTS matchups;
    DROP TABLE IF EXISTS speed_profiles;
    DROP TABLE IF EXISTS sources;
    DROP TABLE IF EXISTS types;
    CREATE TABLE pokemon (
        pokemon_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dex_number INTEGER,
        species_key TEXT,
        form_key TEXT,
        name_en TEXT,
        name_es TEXT,
        form_name_en TEXT,
        form_name_es TEXT,
        type1_key TEXT,
        type2_key TEXT,
        generation INTEGER,
        is_legendary INTEGER,
        is_mythical INTEGER,
        has_mega INTEGER,
        mega_key TEXT,
        is_currently_legal INTEGER,
        season_key TEXT,
        tier_current TEXT,
        tier_source_key TEXT,
        roster_source_key TEXT,
        format_availability TEXT,
        notes TEXT
    );
    CREATE TABLE stats_base (
        pokemon_key TEXT,
        hp INTEGER,
        attack INTEGER,
        defense INTEGER,
        sp_attack INTEGER,
        sp_defense INTEGER,
        speed INTEGER,
        bst INTEGER,
        source_key TEXT
    );
    CREATE TABLE abilities (
        ability_key TEXT PRIMARY KEY,
        name_en TEXT,
        name_es TEXT,
        description_en TEXT,
        description_es TEXT,
        is_signature INTEGER,
        source_key TEXT
    );
    CREATE TABLE pokemon_abilities (
        pokemon_key TEXT,
        ability_key TEXT,
        slot_type TEXT,
        is_currently_available INTEGER,
        source_key TEXT
    );
    CREATE TABLE moves (
        move_key TEXT PRIMARY KEY,
        name_en TEXT,
        name_es TEXT,
        type_key TEXT,
        category_key TEXT,
        power INTEGER,
        accuracy REAL,
        pp INTEGER,
        priority INTEGER,
        targeting_key TEXT,
        makes_contact INTEGER,
        is_sound INTEGER,
        is_pulse INTEGER,
        is_punch INTEGER,
        is_bite INTEGER,
        is_slashing INTEGER,
        is_status INTEGER,
        effect_short_en TEXT,
        effect_short_es TEXT,
        effect_long_en TEXT,
        effect_long_es TEXT,
        source_key TEXT
    );
    CREATE TABLE pokemon_moves (
        pokemon_key TEXT,
        move_key TEXT,
        availability_status TEXT,
        learn_method TEXT,
        learn_method_es TEXT,
        is_confirmed_in_champions INTEGER,
        source_key TEXT,
        notes TEXT
    );
    CREATE TABLE mega_forms (
        mega_key TEXT PRIMARY KEY,
        pokemon_key TEXT,
        mega_name_en TEXT,
        mega_name_es TEXT,
        mega_stone_key TEXT,
        mega_stone_name_en TEXT,
        mega_stone_name_es TEXT,
        type1_key TEXT,
        type2_key TEXT,
        ability_key TEXT,
        hp INTEGER,
        attack INTEGER,
        defense INTEGER,
        sp_attack INTEGER,
        sp_defense INTEGER,
        speed INTEGER,
        bst INTEGER,
        is_currently_available INTEGER,
        source_key TEXT
    );
    CREATE TABLE items (
        item_key TEXT PRIMARY KEY,
        name_en TEXT,
        name_es TEXT,
        category_key TEXT,
        effect_short_en TEXT,
        effect_short_es TEXT,
        effect_long_en TEXT,
        effect_long_es TEXT,
        is_mega_stone INTEGER,
        source_key TEXT
    );
    CREATE TABLE seasons_rules (
        season_key TEXT PRIMARY KEY,
        season_name TEXT,
        start_date TEXT,
        end_date TEXT,
        battle_format TEXT,
        bring_pick_rule TEXT,
        level_rule TEXT,
        mega_allowed INTEGER,
        duplicate_pokemon_allowed INTEGER,
        duplicate_items_allowed INTEGER,
        timer_minutes INTEGER,
        notes TEXT,
        source_key TEXT
    );
    CREATE TABLE tiers (
        pokemon_key TEXT,
        season_key TEXT,
        format TEXT,
        tier_value TEXT,
        tier_source_key TEXT,
        last_checked_at TEXT,
        notes TEXT
    );
    CREATE TABLE roles (
        role_key TEXT PRIMARY KEY,
        name_en TEXT,
        name_es TEXT,
        description_en TEXT,
        description_es TEXT,
        format TEXT
    );
    CREATE TABLE pokemon_roles (
        pokemon_key TEXT,
        role_key TEXT,
        format TEXT,
        confidence TEXT,
        season_key TEXT,
        curation_source_key TEXT,
        notes TEXT
    );
    CREATE TABLE archetypes (
        archetype_key TEXT PRIMARY KEY,
        name_en TEXT,
        name_es TEXT,
        description_en TEXT,
        description_es TEXT,
        format TEXT
    );
    CREATE TABLE pokemon_archetypes (
        pokemon_key TEXT,
        archetype_key TEXT,
        format TEXT,
        fit_score INTEGER,
        season_key TEXT,
        notes TEXT
    );
    CREATE TABLE cores (
        core_id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_key TEXT,
        format TEXT,
        core_name_en TEXT,
        core_name_es TEXT,
        archetype_key TEXT,
        pokemon_1_key TEXT,
        pokemon_2_key TEXT,
        pokemon_3_key TEXT,
        description_en TEXT,
        description_es TEXT,
        confidence TEXT,
        source_key TEXT,
        notes TEXT
    );
    CREATE TABLE matchups (
        matchup_id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_key TEXT,
        format TEXT,
        threat_pokemon_key TEXT,
        answer_pokemon_key TEXT,
        answer_type TEXT,
        confidence TEXT,
        notes TEXT
    );
    CREATE TABLE speed_profiles (
        pokemon_key TEXT,
        season_key TEXT,
        format TEXT,
        base_speed INTEGER,
        speed_min_negative INTEGER,
        speed_min_neutral INTEGER,
        speed_max_neutral INTEGER,
        speed_max_positive INTEGER,
        speed_max_positive_boosted_1 INTEGER,
        speed_max_positive_boosted_2 INTEGER,
        trick_room_rating TEXT,
        notes TEXT
    );
    CREATE TABLE sources (
        source_key TEXT PRIMARY KEY,
        source_name TEXT,
        source_type TEXT,
        url TEXT,
        trust_level TEXT,
        last_checked_at TEXT,
        license_notes TEXT,
        notes TEXT
    );
    CREATE TABLE types (
        type_key TEXT PRIMARY KEY,
        name_en TEXT,
        name_es TEXT
    );
def load_csv_to_table(conn: sqlite3.Connection, csv_path: Path, table_name: str) -> None:
    """Carga datos de un CSV a una tabla SQLite."""
    cur = conn.cursor()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        print(f"[SKIP] {csv_path.name}: vacío")
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" * len(columns))
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    data = [[row[col] for col in columns] for row in rows]
    cur.executemany(query, data)
    conn.commit()
    print(f"[OK] Cargado {len(rows)} filas en {table_name}")

def load_all_data(conn: sqlite3.Connection) -> None:
    """Carga todos los CSV a las tablas correspondientes."""
    mappings = {
        "pokemon.csv": "pokemon",
        "stats_base.csv": "stats_base",
        "abilities.csv": "abilities",
        "pokemon_abilities.csv": "pokemon_abilities",
        "moves.csv": "moves",
        "pokemon_moves.csv": "pokemon_moves",
        "mega_forms.csv": "mega_forms",
        "items.csv": "items",
        "seasons_rules.csv": "seasons_rules",
        "tiers.csv": "tiers",
        "roles.csv": "roles",
        "pokemon_roles.csv": "pokemon_roles",
        "archetypes.csv": "archetypes",
        "pokemon_archetypes.csv": "pokemon_archetypes",
        "cores.csv": "cores",
        "matchups.csv": "matchups",
        "speed_profiles.csv": "speed_profiles",
        "sources.csv": "sources",
        "types.csv": "types",
    }
    for csv_file, table in mappings.items():
        csv_path = RAW / csv_file
        if csv_path.exists():
            load_csv_to_table(conn, csv_path, table)
        else:
            print(f"[WARN] {csv_file} no encontrado")

def main():
    ensure_dirs()
    conn = sqlite3.connect(DB)
    create_schema(conn)
    load_all_data(conn)
    conn.close()
    print(f"[OK] BD construida en {DB}")

if __name__ == "__main__":
    main()
