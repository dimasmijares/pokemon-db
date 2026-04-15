from pathlib import Path
import csv
import sqlite3

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data_raw"
BUILD = BASE / "data_build"
DB = BUILD / "pokemon_champions.sqlite"
KEEP_EMPTY_STRING_COLUMNS = {
    ("pokemon", "form_key"),
}

TABLE_MAPPINGS = {
    "pokemon.csv": "pokemon",
    "stats_base.csv": "stats_base",
    "abilities.csv": "abilities",
    "pokemon_abilities.csv": "pokemon_abilities",
    "moves.csv": "moves",
    "pokemon_moves.csv": "pokemon_moves",
    "items.csv": "items",
    "mega_forms.csv": "mega_forms",
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


def ensure_dirs() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "exports").mkdir(parents=True, exist_ok=True)


def reset_database() -> None:
    if DB.exists():
        try:
            DB.unlink()
        except PermissionError:
            print("[WARN] No se pudo borrar la SQLite; se recreara el esquema dentro del archivo existente")


def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        DROP VIEW IF EXISTS v_charizard_answers;
        DROP VIEW IF EXISTS v_trick_room_candidates;
        DROP VIEW IF EXISTS v_sun_candidates;
        DROP VIEW IF EXISTS v_rain_candidates;
        DROP VIEW IF EXISTS v_pokemon_archetypes_summary;
        DROP VIEW IF EXISTS v_pokemon_roles_summary;
        DROP VIEW IF EXISTS v_pokemon_moves_summary;
        DROP VIEW IF EXISTS v_pokemon_abilities_summary;
        DROP VIEW IF EXISTS v_move_user_links;
        DROP VIEW IF EXISTS v_team_builder_pool;
        DROP VIEW IF EXISTS v_move_users;
        DROP VIEW IF EXISTS v_speed_table;
        DROP VIEW IF EXISTS v_pokemon_summary;

        DROP TABLE IF EXISTS matchups;
        DROP TABLE IF EXISTS cores;
        DROP TABLE IF EXISTS pokemon_archetypes;
        DROP TABLE IF EXISTS archetypes;
        DROP TABLE IF EXISTS pokemon_roles;
        DROP TABLE IF EXISTS roles;
        DROP TABLE IF EXISTS tiers;
        DROP TABLE IF EXISTS mega_forms;
        DROP TABLE IF EXISTS pokemon_moves;
        DROP TABLE IF EXISTS moves;
        DROP TABLE IF EXISTS pokemon_abilities;
        DROP TABLE IF EXISTS abilities;
        DROP TABLE IF EXISTS speed_profiles;
        DROP TABLE IF EXISTS stats_base;
        DROP TABLE IF EXISTS pokemon;
        DROP TABLE IF EXISTS seasons_rules;
        DROP TABLE IF EXISTS items;
        DROP TABLE IF EXISTS sources;
        DROP TABLE IF EXISTS types;

        CREATE TABLE pokemon (
            pokemon_id INTEGER PRIMARY KEY,
            dex_number INTEGER NOT NULL,
            species_key TEXT NOT NULL,
            form_key TEXT NOT NULL DEFAULT '',
            name_en TEXT NOT NULL,
            name_es TEXT,
            form_name_en TEXT,
            form_name_es TEXT,
            type1_key TEXT NOT NULL,
            type2_key TEXT,
            generation INTEGER,
            is_legendary INTEGER NOT NULL DEFAULT 0,
            is_mythical INTEGER NOT NULL DEFAULT 0,
            has_mega INTEGER NOT NULL DEFAULT 0,
            mega_key TEXT,
            is_currently_legal INTEGER NOT NULL DEFAULT 0,
            season_key TEXT,
            tier_current TEXT,
            tier_source_key TEXT,
            roster_source_key TEXT,
            format_availability TEXT,
            notes TEXT,
            UNIQUE(species_key, form_key)
        );

        CREATE TABLE stats_base (
            pokemon_id INTEGER PRIMARY KEY,
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            sp_attack INTEGER NOT NULL,
            sp_defense INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            bst INTEGER,
            source_key TEXT,
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id)
        );

        CREATE TABLE abilities (
            ability_key TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_es TEXT,
            description_en TEXT,
            description_es TEXT,
            is_signature INTEGER NOT NULL DEFAULT 0,
            source_key TEXT
        );

        CREATE TABLE pokemon_abilities (
            pokemon_id INTEGER NOT NULL,
            ability_key TEXT NOT NULL,
            slot_type TEXT,
            is_currently_available INTEGER NOT NULL DEFAULT 0,
            source_key TEXT,
            PRIMARY KEY (pokemon_id, ability_key, slot_type),
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (ability_key) REFERENCES abilities(ability_key)
        );

        CREATE TABLE moves (
            move_key TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_es TEXT,
            type_key TEXT,
            category_key TEXT,
            power INTEGER,
            accuracy REAL,
            pp INTEGER,
            priority INTEGER,
            targeting_key TEXT,
            makes_contact INTEGER NOT NULL DEFAULT 0,
            is_sound INTEGER NOT NULL DEFAULT 0,
            is_pulse INTEGER NOT NULL DEFAULT 0,
            is_punch INTEGER NOT NULL DEFAULT 0,
            is_bite INTEGER NOT NULL DEFAULT 0,
            is_slashing INTEGER NOT NULL DEFAULT 0,
            is_status INTEGER NOT NULL DEFAULT 0,
            effect_short_en TEXT,
            effect_short_es TEXT,
            effect_long_en TEXT,
            effect_long_es TEXT,
            source_key TEXT
        );

        CREATE TABLE pokemon_moves (
            pokemon_id INTEGER NOT NULL,
            move_key TEXT NOT NULL,
            availability_status TEXT,
            learn_method TEXT,
            learn_method_es TEXT,
            is_confirmed_in_champions INTEGER NOT NULL DEFAULT 0,
            source_key TEXT,
            notes TEXT,
            PRIMARY KEY (pokemon_id, move_key, learn_method),
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (move_key) REFERENCES moves(move_key)
        );

        CREATE TABLE items (
            item_key TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_es TEXT,
            category_key TEXT,
            effect_short_en TEXT,
            effect_short_es TEXT,
            effect_long_en TEXT,
            effect_long_es TEXT,
            is_mega_stone INTEGER NOT NULL DEFAULT 0,
            source_key TEXT
        );

        CREATE TABLE mega_forms (
            mega_key TEXT PRIMARY KEY,
            pokemon_id INTEGER NOT NULL,
            mega_name_en TEXT NOT NULL,
            mega_name_es TEXT,
            mega_stone_key TEXT,
            mega_stone_name_en TEXT,
            mega_stone_name_es TEXT,
            type1_key TEXT NOT NULL,
            type2_key TEXT,
            ability_key TEXT,
            hp INTEGER,
            attack INTEGER,
            defense INTEGER,
            sp_attack INTEGER,
            sp_defense INTEGER,
            speed INTEGER,
            bst INTEGER,
            is_currently_available INTEGER NOT NULL DEFAULT 0,
            source_key TEXT,
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (ability_key) REFERENCES abilities(ability_key),
            FOREIGN KEY (mega_stone_key) REFERENCES items(item_key)
        );

        CREATE TABLE seasons_rules (
            season_key TEXT PRIMARY KEY,
            season_name TEXT NOT NULL,
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
            pokemon_id INTEGER NOT NULL,
            season_key TEXT NOT NULL,
            format TEXT NOT NULL,
            tier_value TEXT NOT NULL,
            tier_source_key TEXT,
            last_checked_at TEXT,
            notes TEXT,
            PRIMARY KEY (pokemon_id, season_key, format),
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (season_key) REFERENCES seasons_rules(season_key)
        );

        CREATE TABLE roles (
            role_key TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_es TEXT,
            description_en TEXT,
            description_es TEXT
        );

        CREATE TABLE pokemon_roles (
            pokemon_id INTEGER NOT NULL,
            role_key TEXT NOT NULL,
            confidence TEXT,
            season_key TEXT NOT NULL,
            format TEXT NOT NULL,
            curation_source_key TEXT,
            notes TEXT,
            PRIMARY KEY (pokemon_id, role_key, season_key, format),
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (role_key) REFERENCES roles(role_key),
            FOREIGN KEY (season_key) REFERENCES seasons_rules(season_key)
        );

        CREATE TABLE archetypes (
            archetype_key TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_es TEXT,
            description_en TEXT,
            description_es TEXT
        );

        CREATE TABLE pokemon_archetypes (
            pokemon_id INTEGER NOT NULL,
            archetype_key TEXT NOT NULL,
            fit_score INTEGER,
            season_key TEXT NOT NULL,
            format TEXT NOT NULL,
            notes TEXT,
            PRIMARY KEY (pokemon_id, archetype_key, season_key, format),
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (archetype_key) REFERENCES archetypes(archetype_key),
            FOREIGN KEY (season_key) REFERENCES seasons_rules(season_key)
        );

        CREATE TABLE cores (
            core_id INTEGER PRIMARY KEY,
            season_key TEXT NOT NULL,
            format TEXT NOT NULL,
            core_name_en TEXT NOT NULL,
            core_name_es TEXT,
            archetype_key TEXT,
            pokemon_1_id INTEGER NOT NULL,
            pokemon_2_id INTEGER NOT NULL,
            pokemon_3_id INTEGER,
            description_en TEXT,
            description_es TEXT,
            confidence TEXT,
            source_key TEXT,
            notes TEXT,
            FOREIGN KEY (season_key) REFERENCES seasons_rules(season_key),
            FOREIGN KEY (archetype_key) REFERENCES archetypes(archetype_key),
            FOREIGN KEY (pokemon_1_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (pokemon_2_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (pokemon_3_id) REFERENCES pokemon(pokemon_id)
        );

        CREATE TABLE matchups (
            matchup_id INTEGER PRIMARY KEY,
            season_key TEXT NOT NULL,
            format TEXT NOT NULL,
            threat_pokemon_id INTEGER NOT NULL,
            answer_pokemon_id INTEGER NOT NULL,
            answer_type TEXT NOT NULL,
            confidence TEXT,
            notes TEXT,
            FOREIGN KEY (season_key) REFERENCES seasons_rules(season_key),
            FOREIGN KEY (threat_pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (answer_pokemon_id) REFERENCES pokemon(pokemon_id)
        );

        CREATE TABLE speed_profiles (
            pokemon_id INTEGER NOT NULL,
            season_key TEXT NOT NULL,
            format TEXT NOT NULL,
            base_speed INTEGER NOT NULL,
            speed_min_negative INTEGER,
            speed_min_neutral INTEGER,
            speed_max_neutral INTEGER,
            speed_max_positive INTEGER,
            speed_max_positive_boosted_1 INTEGER,
            speed_max_positive_boosted_2 INTEGER,
            trick_room_rating TEXT,
            notes TEXT,
            PRIMARY KEY (pokemon_id, season_key, format),
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
            FOREIGN KEY (season_key) REFERENCES seasons_rules(season_key)
        );

        CREATE TABLE sources (
            source_key TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_type TEXT,
            url TEXT,
            trust_level TEXT,
            last_checked_at TEXT,
            license_notes TEXT,
            notes TEXT
        );

        CREATE TABLE types (
            type_key TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_es TEXT
        );

        CREATE INDEX idx_pokemon_species ON pokemon(species_key, form_key);
        CREATE INDEX idx_tiers_lookup ON tiers(season_key, format, tier_value);
        CREATE INDEX idx_speed_profiles_lookup ON speed_profiles(season_key, format, base_speed);
        """
    )
    conn.commit()


def read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def load_csv_to_table(conn: sqlite3.Connection, csv_path: Path, table_name: str) -> None:
    columns, rows = read_csv_rows(csv_path)
    if not rows:
        print(f"[SKIP] {csv_path.name}: vacío")
        return

    usable_columns = [column for column in columns if column and column.strip()]
    placeholders = ", ".join("?" for _ in usable_columns)
    query = f"INSERT INTO {table_name} ({', '.join(usable_columns)}) VALUES ({placeholders})"
    data = []
    for row in rows:
        normalized_row = []
        for column in usable_columns:
            value = row.get(column, "")
            if value == "" and (table_name, column) not in KEEP_EMPTY_STRING_COLUMNS:
                normalized_row.append(None)
            else:
                normalized_row.append(value)
        data.append(normalized_row)
    conn.executemany(query, data)
    conn.commit()
    print(f"[OK] Cargado {len(rows)} filas en {table_name}")


def load_all_data(conn: sqlite3.Connection) -> None:
    for csv_name, table_name in TABLE_MAPPINGS.items():
        csv_path = RAW / csv_name
        if not csv_path.exists():
            print(f"[WARN] {csv_name} no encontrado")
            continue
        load_csv_to_table(conn, csv_path, table_name)


def normalize_loaded_data(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        UPDATE stats_base
        SET bst = COALESCE(
            bst,
            COALESCE(hp, 0) +
            COALESCE(attack, 0) +
            COALESCE(defense, 0) +
            COALESCE(sp_attack, 0) +
            COALESCE(sp_defense, 0) +
            COALESCE(speed, 0)
        );

        UPDATE pokemon
        SET tier_current = (
            SELECT t.tier_value
            FROM tiers t
            WHERE t.pokemon_id = pokemon.pokemon_id
              AND t.season_key = pokemon.season_key
              AND t.format = 'doubles'
            LIMIT 1
        )
        WHERE tier_current IS NULL OR tier_current = '';
        """
    )
    conn.commit()


def create_views(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE VIEW v_pokemon_summary AS
        SELECT
            p.pokemon_id,
            p.dex_number,
            p.species_key,
            p.form_key,
            p.name_en,
            p.name_es,
            p.form_name_en,
            p.form_name_es,
            p.type1_key,
            p.type2_key,
            sb.hp,
            sb.attack,
            sb.defense,
            sb.sp_attack,
            sb.sp_defense,
            sb.speed,
            sb.bst,
            (
                SELECT GROUP_CONCAT(pa.ability_key, ', ')
                FROM pokemon_abilities pa
                JOIN abilities ab ON ab.ability_key = pa.ability_key
                WHERE pa.pokemon_id = p.pokemon_id
                  AND pa.is_currently_available = 1
            ) AS ability_keys,
            (
                SELECT GROUP_CONCAT(ab.name_en, ', ')
                FROM pokemon_abilities pa
                JOIN abilities ab ON ab.ability_key = pa.ability_key
                WHERE pa.pokemon_id = p.pokemon_id
                  AND pa.is_currently_available = 1
            ) AS abilities,
            (
                SELECT GROUP_CONCAT(COALESCE(ab.name_es, ab.name_en), ', ')
                FROM pokemon_abilities pa
                JOIN abilities ab ON ab.ability_key = pa.ability_key
                WHERE pa.pokemon_id = p.pokemon_id
                  AND pa.is_currently_available = 1
            ) AS abilities_es,
            (
                SELECT GROUP_CONCAT(r.name_en, ', ')
                FROM pokemon_roles pr
                JOIN roles r ON r.role_key = pr.role_key
                WHERE pr.pokemon_id = p.pokemon_id
                  AND pr.season_key = p.season_key
                  AND pr.format = 'doubles'
            ) AS roles,
            (
                SELECT GROUP_CONCAT(COALESCE(r.name_es, r.name_en), ', ')
                FROM pokemon_roles pr
                JOIN roles r ON r.role_key = pr.role_key
                WHERE pr.pokemon_id = p.pokemon_id
                  AND pr.season_key = p.season_key
                  AND pr.format = 'doubles'
            ) AS roles_es,
            (
                SELECT GROUP_CONCAT(a.name_en, ', ')
                FROM pokemon_archetypes pa2
                JOIN archetypes a ON a.archetype_key = pa2.archetype_key
                WHERE pa2.pokemon_id = p.pokemon_id
                  AND pa2.season_key = p.season_key
                  AND pa2.format = 'doubles'
            ) AS archetypes,
            (
                SELECT GROUP_CONCAT(COALESCE(a.name_es, a.name_en), ', ')
                FROM pokemon_archetypes pa2
                JOIN archetypes a ON a.archetype_key = pa2.archetype_key
                WHERE pa2.pokemon_id = p.pokemon_id
                  AND pa2.season_key = p.season_key
                  AND pa2.format = 'doubles'
            ) AS archetypes_es,
            t.tier_value,
            p.is_currently_legal,
            p.season_key,
            p.format_availability
        FROM pokemon p
        LEFT JOIN stats_base sb ON sb.pokemon_id = p.pokemon_id
        LEFT JOIN tiers t
            ON t.pokemon_id = p.pokemon_id
           AND t.season_key = p.season_key
           AND t.format = 'doubles';

        CREATE VIEW v_speed_table AS
        SELECT
            p.pokemon_id,
            p.species_key,
            p.form_key,
            p.name_en,
            p.form_name_en,
            sp.base_speed,
            sp.speed_min_negative,
            sp.speed_min_neutral,
            sp.speed_max_neutral,
            sp.speed_max_positive,
            sp.speed_max_positive_boosted_1,
            sp.speed_max_positive_boosted_2,
            sp.trick_room_rating,
            sp.season_key,
            sp.format
        FROM speed_profiles sp
        JOIN pokemon p ON p.pokemon_id = sp.pokemon_id;

        CREATE VIEW v_move_users AS
        SELECT
            m.move_key,
            m.name_en,
            m.name_es,
            COUNT(DISTINCT CASE WHEN pm.is_confirmed_in_champions = 1 THEN pm.pokemon_id END) AS confirmed_user_count,
            COUNT(DISTINCT CASE WHEN pm.is_confirmed_in_champions = 0 THEN pm.pokemon_id END) AS inferred_user_count,
            COUNT(DISTINCT CASE WHEN pm.availability_status = 'champions_move_pool' THEN pm.pokemon_id END) AS move_pool_user_count,
            COUNT(DISTINCT CASE WHEN pm.availability_status = 'observed_set' THEN pm.pokemon_id END) AS observed_set_user_count,
            ROUND(
                100.0 * COUNT(DISTINCT CASE WHEN pm.availability_status = 'observed_set' THEN pm.pokemon_id END)
                / NULLIF(COUNT(DISTINCT CASE WHEN pm.availability_status = 'champions_move_pool' THEN pm.pokemon_id END), 0),
                1
            ) AS observed_set_coverage_pct,
            GROUP_CONCAT(
                DISTINCT p.name_en || CASE
                    WHEN p.form_name_en IS NOT NULL AND p.form_name_en <> '' THEN ' (' || p.form_name_en || ')'
                    ELSE ''
                END
            ) AS users
        FROM pokemon_moves pm
        JOIN moves m ON m.move_key = pm.move_key
        JOIN pokemon p ON p.pokemon_id = pm.pokemon_id
        GROUP BY m.move_key, m.name_en, m.name_es;

        CREATE VIEW v_move_user_links AS
        SELECT
            m.move_key,
            m.name_en,
            m.name_es,
            p.pokemon_id,
            p.name_en AS pokemon_name_en,
            p.name_es AS pokemon_name_es,
            p.form_name_en,
            p.form_name_es,
            MAX(CASE WHEN pm.availability_status = 'champions_move_pool' THEN 1 ELSE 0 END) AS is_in_move_pool,
            MAX(CASE WHEN pm.availability_status = 'observed_set' THEN 1 ELSE 0 END) AS is_observed_in_sets
        FROM pokemon_moves pm
        JOIN moves m ON m.move_key = pm.move_key
        JOIN pokemon p ON p.pokemon_id = pm.pokemon_id
        GROUP BY
            m.move_key,
            m.name_en,
            m.name_es,
            p.pokemon_id,
            p.name_en,
            p.name_es,
            p.form_name_en,
            p.form_name_es;

        CREATE VIEW v_team_builder_pool AS
        SELECT
            p.pokemon_id,
            p.species_key,
            p.form_key,
            p.name_en,
            p.name_es,
            p.form_name_en,
            p.form_name_es,
            p.type1_key,
            p.type2_key,
            t.tier_value,
            (
                SELECT GROUP_CONCAT(r.name_en, ', ')
                FROM pokemon_roles pr
                JOIN roles r ON r.role_key = pr.role_key
                WHERE pr.pokemon_id = p.pokemon_id
                  AND pr.season_key = p.season_key
                  AND pr.format = 'doubles'
            ) AS roles,
            (
                SELECT GROUP_CONCAT(COALESCE(r.name_es, r.name_en), ', ')
                FROM pokemon_roles pr
                JOIN roles r ON r.role_key = pr.role_key
                WHERE pr.pokemon_id = p.pokemon_id
                  AND pr.season_key = p.season_key
                  AND pr.format = 'doubles'
            ) AS roles_es,
            (
                SELECT GROUP_CONCAT(a.name_en, ', ')
                FROM pokemon_archetypes pa2
                JOIN archetypes a ON a.archetype_key = pa2.archetype_key
                WHERE pa2.pokemon_id = p.pokemon_id
                  AND pa2.season_key = p.season_key
                  AND pa2.format = 'doubles'
            ) AS archetypes
            ,
            (
                SELECT GROUP_CONCAT(COALESCE(a.name_es, a.name_en), ', ')
                FROM pokemon_archetypes pa2
                JOIN archetypes a ON a.archetype_key = pa2.archetype_key
                WHERE pa2.pokemon_id = p.pokemon_id
                  AND pa2.season_key = p.season_key
                  AND pa2.format = 'doubles'
            ) AS archetypes_es
        FROM pokemon p
        LEFT JOIN tiers t
            ON t.pokemon_id = p.pokemon_id
           AND t.season_key = p.season_key
           AND t.format = 'doubles'
        WHERE p.is_currently_legal = 1;

        CREATE VIEW v_rain_candidates AS
        SELECT
            p.pokemon_id,
            p.species_key,
            p.form_key,
            p.name_en,
            p.form_name_en,
            t.tier_value,
            (
                SELECT GROUP_CONCAT(pa.ability_key, ', ')
                FROM pokemon_abilities pa
                WHERE pa.pokemon_id = p.pokemon_id
            ) AS abilities
        FROM pokemon p
        LEFT JOIN tiers t
            ON t.pokemon_id = p.pokemon_id
           AND t.season_key = p.season_key
           AND t.format = 'doubles'
        WHERE EXISTS (
            SELECT 1
            FROM pokemon_abilities pa
            WHERE pa.pokemon_id = p.pokemon_id
              AND pa.ability_key IN ('drizzle', 'swift-swim', 'rain-dish')
        )
        OR p.type1_key = 'water'
        OR p.type2_key = 'water';

        CREATE VIEW v_sun_candidates AS
        SELECT
            p.pokemon_id,
            p.species_key,
            p.form_key,
            p.name_en,
            p.form_name_en,
            t.tier_value,
            (
                SELECT GROUP_CONCAT(pa.ability_key, ', ')
                FROM pokemon_abilities pa
                WHERE pa.pokemon_id = p.pokemon_id
            ) AS abilities
        FROM pokemon p
        LEFT JOIN tiers t
            ON t.pokemon_id = p.pokemon_id
           AND t.season_key = p.season_key
           AND t.format = 'doubles'
        WHERE EXISTS (
            SELECT 1
            FROM pokemon_abilities pa
            WHERE pa.pokemon_id = p.pokemon_id
              AND pa.ability_key IN ('drought', 'chlorophyll', 'solar-power')
        )
        OR p.type1_key = 'fire'
        OR p.type2_key = 'fire';

        CREATE VIEW v_trick_room_candidates AS
        SELECT
            p.pokemon_id,
            p.species_key,
            p.form_key,
            p.name_en,
            p.form_name_en,
            sp.base_speed,
            sp.trick_room_rating,
            (
                SELECT GROUP_CONCAT(r.name_en, ', ')
                FROM pokemon_roles pr
                JOIN roles r ON r.role_key = pr.role_key
                WHERE pr.pokemon_id = p.pokemon_id
                  AND pr.season_key = sp.season_key
                  AND pr.format = sp.format
            ) AS roles
        FROM speed_profiles sp
        JOIN pokemon p ON p.pokemon_id = sp.pokemon_id
        WHERE sp.format = 'doubles'
          AND (
              LOWER(COALESCE(sp.trick_room_rating, '')) IN ('high', 'very high', 'excellent')
              OR sp.base_speed <= 60
          );

        CREATE VIEW v_charizard_answers AS
        SELECT
            threat.pokemon_id AS threat_pokemon_id,
            threat.name_en AS threat_name_en,
            threat.form_name_en AS threat_form_name_en,
            answer.pokemon_id AS answer_pokemon_id,
            answer.name_en AS answer_name_en,
            answer.form_name_en AS answer_form_name_en,
            m.answer_type,
            m.confidence,
            m.notes,
            m.season_key,
            m.format
        FROM matchups m
        JOIN pokemon threat ON threat.pokemon_id = m.threat_pokemon_id
        JOIN pokemon answer ON answer.pokemon_id = m.answer_pokemon_id
        WHERE m.format = 'doubles'
          AND threat.species_key = 'charizard';

        CREATE VIEW v_pokemon_abilities_summary AS
        SELECT
            p.pokemon_id,
            p.name_en AS pokemon_name_en,
            p.name_es AS pokemon_name_es,
            p.form_name_en,
            p.form_name_es,
            pa.ability_key,
            pa.slot_type,
            pa.is_currently_available,
            a.name_en,
            a.name_es,
            a.description_en,
            a.description_es
        FROM pokemon_abilities pa
        JOIN pokemon p ON p.pokemon_id = pa.pokemon_id
        JOIN abilities a ON a.ability_key = pa.ability_key
        WHERE pa.is_currently_available = 1;

        CREATE VIEW v_pokemon_moves_summary AS
        SELECT
            p.pokemon_id,
            p.name_en AS pokemon_name_en,
            p.name_es AS pokemon_name_es,
            p.form_name_en,
            p.form_name_es,
            m.move_key,
            m.name_en,
            m.name_es,
            MAX(CASE WHEN pm.availability_status = 'champions_move_pool' THEN 1 ELSE 0 END) AS is_in_move_pool,
            MAX(CASE WHEN pm.availability_status = 'observed_set' THEN 1 ELSE 0 END) AS is_observed_in_sets
        FROM pokemon_moves pm
        JOIN pokemon p ON p.pokemon_id = pm.pokemon_id
        JOIN moves m ON m.move_key = pm.move_key
        GROUP BY
            p.pokemon_id,
            p.name_en,
            p.name_es,
            p.form_name_en,
            p.form_name_es,
            m.move_key,
            m.name_en,
            m.name_es;

        CREATE VIEW v_pokemon_roles_summary AS
        SELECT
            pr.pokemon_id,
            pr.role_key,
            r.name_en,
            r.name_es,
            r.description_en,
            r.description_es,
            pr.confidence,
            pr.season_key,
            pr.format,
            pr.curation_source_key,
            pr.notes
        FROM pokemon_roles pr
        JOIN roles r ON r.role_key = pr.role_key;

        CREATE VIEW v_pokemon_archetypes_summary AS
        SELECT
            pa.pokemon_id,
            pa.archetype_key,
            a.name_en,
            a.name_es,
            a.description_en,
            a.description_es,
            pa.fit_score,
            pa.season_key,
            pa.format,
            pa.notes
        FROM pokemon_archetypes pa
        JOIN archetypes a ON a.archetype_key = pa.archetype_key;
        """
    )
    conn.commit()
    print("[OK] Vistas creadas")


def main() -> None:
    ensure_dirs()
    reset_database()
    conn = sqlite3.connect(DB)
    try:
        create_schema(conn)
        load_all_data(conn)
        normalize_loaded_data(conn)
        create_views(conn)
    finally:
        conn.close()
    print(f"[OK] BD construida en {DB}")


if __name__ == "__main__":
    main()
