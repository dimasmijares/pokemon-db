from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import sqlite3


BASE = Path(__file__).resolve().parents[1]
DB_SRC = BASE / "data_build" / "pokemon_champions.sqlite"
BUNDLE = BASE / "data_bundle"

DOCS_TO_COPY = [
    "schema.md",
    "specifications.md",
    "validation_report.md",
    "source_policy.md",
]

SCRIPTS_TO_COPY = [
    "build_db.py",
    "validate_data.py",
    "export_views.py",
    "sync_current_champions.py",
    "derive_competitive_layer.py",
]

EXPORT_QUERIES = {
    "pokemon_list.json": "SELECT * FROM v_team_builder_pool",
    "pokemon_detail_index.json": "SELECT * FROM v_pokemon_summary",
    "pokemon_home_context_detail.json": "CUSTOM_EXPORT",
    "speed_profiles.json": "SELECT * FROM v_speed_table",
    "move_users.json": "SELECT * FROM v_move_users",
    "pokemon_abilities_summary.json": "SELECT * FROM v_pokemon_abilities_summary",
    "pokemon_moves_summary.json": "SELECT * FROM v_pokemon_moves_summary",
    "pokemon_roles_summary.json": "SELECT * FROM v_pokemon_roles_summary",
    "pokemon_archetypes_summary.json": "SELECT * FROM v_pokemon_archetypes_summary",
    "rain_candidates.json": "SELECT * FROM v_rain_candidates",
    "sun_candidates.json": "SELECT * FROM v_sun_candidates",
    "trick_room_candidates.json": "SELECT * FROM v_trick_room_candidates",
    "charizard_answers.json": "SELECT * FROM v_charizard_answers",
    "types.json": "SELECT * FROM types",
    "sources.json": "SELECT * FROM sources",
}


def fetch_rows(conn: sqlite3.Connection, query: str) -> list[dict]:
    return [dict(row) for row in conn.execute(query).fetchall()]


def build_pokemon_list_export(conn: sqlite3.Connection) -> list[dict]:
    rows = fetch_rows(conn, "SELECT * FROM v_team_builder_pool")
    role_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_roles_summary WHERE format = 'doubles'")
    archetype_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_archetypes_summary WHERE format = 'doubles'")

    roles_by_pokemon: dict[int, list[dict]] = {}
    for row in role_rows:
        roles_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(
            {
                "role_key": row["role_key"],
                "name_en": row["name_en"],
                "name_es": row["name_es"] or row["name_en"],
                "description_en": row["description_en"] or "",
                "description_es": row["description_es"] or "",
                "confidence": row["confidence"],
            }
        )

    archetypes_by_pokemon: dict[int, list[dict]] = {}
    for row in archetype_rows:
        archetypes_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(
            {
                "archetype_key": row["archetype_key"],
                "name_en": row["name_en"],
                "name_es": row["name_es"] or row["name_en"],
                "description_en": row["description_en"] or "",
                "description_es": row["description_es"] or "",
                "fit_score": row["fit_score"],
            }
        )

    output = []
    for row in rows:
        pokemon_id = int(row["pokemon_id"])
        output.append(
            {
                "pokemon_id": pokemon_id,
                "species_key": row["species_key"],
                "form_key": row["form_key"] or "",
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "form_name_en": row.get("form_name_en") or "",
                "form_name_es": row.get("form_name_es") or "",
                "type1_key": row["type1_key"],
                "type2_key": row.get("type2_key") or "",
                "tier_value": row.get("tier_value") or "",
                "roles": roles_by_pokemon.get(pokemon_id, []),
                "archetypes": archetypes_by_pokemon.get(pokemon_id, []),
            }
        )
    return output


def build_pokemon_detail_export(conn: sqlite3.Connection) -> list[dict]:
    detail_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_summary")
    ability_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_abilities_summary")
    role_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_roles_summary WHERE format = 'doubles'")
    archetype_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_archetypes_summary WHERE format = 'doubles'")

    abilities_by_pokemon: dict[int, list[dict]] = {}
    for row in ability_rows:
        abilities_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(
            {
                "ability_key": row["ability_key"],
                "slot_type": row["slot_type"],
                "is_currently_available": int(row["is_currently_available"] or 0),
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "description_en": row.get("description_en") or "",
                "description_es": row.get("description_es") or "",
            }
        )

    roles_by_pokemon: dict[int, list[dict]] = {}
    for row in role_rows:
        roles_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(
            {
                "role_key": row["role_key"],
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "description_en": row.get("description_en") or "",
                "description_es": row.get("description_es") or "",
                "confidence": row["confidence"],
            }
        )

    archetypes_by_pokemon: dict[int, list[dict]] = {}
    for row in archetype_rows:
        archetypes_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(
            {
                "archetype_key": row["archetype_key"],
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "description_en": row.get("description_en") or "",
                "description_es": row.get("description_es") or "",
                "fit_score": row["fit_score"],
            }
        )

    output = []
    for row in detail_rows:
        pokemon_id = int(row["pokemon_id"])
        output.append(
            {
                **row,
                "name_es": row.get("name_es") or row["name_en"],
                "form_name_en": row.get("form_name_en") or "",
                "form_name_es": row.get("form_name_es") or "",
                "type2_key": row.get("type2_key") or "",
                "tier_value": row.get("tier_value") or "",
                "format_availability": row.get("format_availability") or "",
                "abilities_structured": abilities_by_pokemon.get(pokemon_id, []),
                "roles_structured": roles_by_pokemon.get(pokemon_id, []),
                "archetypes_structured": archetypes_by_pokemon.get(pokemon_id, []),
            }
        )
    return output


def build_move_users_export(conn: sqlite3.Connection) -> list[dict]:
    summary_rows = fetch_rows(conn, "SELECT * FROM v_move_users")
    user_rows = fetch_rows(conn, "SELECT * FROM v_move_user_links")
    users_by_move: dict[str, list[dict]] = {}
    for row in user_rows:
        users_by_move.setdefault(row["move_key"], []).append(
            {
                "pokemon_id": int(row["pokemon_id"]),
                "name_en": row["pokemon_name_en"],
                "name_es": row.get("pokemon_name_es") or row["pokemon_name_en"],
                "form_name_en": row.get("form_name_en") or "",
                "form_name_es": row.get("form_name_es") or "",
                "is_in_move_pool": int(row["is_in_move_pool"] or 0),
                "is_observed_in_sets": int(row["is_observed_in_sets"] or 0),
            }
        )
    output = []
    for row in summary_rows:
        output.append(
            {
                **row,
                "name_es": row.get("name_es") or row["name_en"],
                "users": users_by_move.get(row["move_key"], []),
            }
        )
    return output


def build_pokemon_home_context_detail_export(conn: sqlite3.Connection) -> list[dict]:
    detail_rows = fetch_rows(conn, "SELECT pokemon_id, name_en, name_es, form_name_en, form_name_es, has_mega FROM pokemon")
    ability_rows = fetch_rows(conn, "SELECT * FROM v_pokemon_abilities_summary")
    move_rows = fetch_rows(
        conn,
        """
        SELECT
            pms.pokemon_id,
            pms.move_key,
            pms.name_en,
            pms.name_es,
            pms.is_in_move_pool,
            pms.is_observed_in_sets,
            m.type_key,
            m.category_key,
            m.power,
            m.accuracy,
            m.priority,
            m.effect_short_en,
            m.effect_short_es
        FROM v_pokemon_moves_summary pms
        JOIN moves m ON m.move_key = pms.move_key
        """,
    )
    mega_rows = fetch_rows(
        conn,
        """
        SELECT
            mf.pokemon_id,
            mf.mega_key,
            mf.mega_name_en,
            mf.mega_name_es,
            mf.mega_stone_key,
            mf.mega_stone_name_en,
            mf.mega_stone_name_es,
            mf.type1_key,
            mf.type2_key,
            mf.hp,
            mf.attack,
            mf.defense,
            mf.sp_attack,
            mf.sp_defense,
            mf.speed,
            mf.bst,
            a.ability_key,
            a.name_en AS ability_name_en,
            a.name_es AS ability_name_es,
            a.description_en AS ability_description_en,
            a.description_es AS ability_description_es
        FROM mega_forms mf
        LEFT JOIN abilities a ON a.ability_key = mf.ability_key
        WHERE mf.is_currently_available = 1
        """,
    )

    abilities_by_pokemon: dict[int, list[dict]] = {}
    for row in ability_rows:
        abilities_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(
            {
                "ability_key": row["ability_key"],
                "slot_type": row["slot_type"],
                "is_currently_available": int(row["is_currently_available"] or 0),
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "description_en": row.get("description_en") or "",
                "description_es": row.get("description_es") or "",
            }
        )

    def move_sort_key(row: dict) -> tuple:
        power = row["power"] if row["power"] is not None else -1
        priority = row["priority"] if row["priority"] is not None else -9
        category = row.get("category_key") or ""
        return (
            -int(row.get("is_observed_in_sets") or 0),
            -int(row.get("is_in_move_pool") or 0),
            0 if category != "status" else 1,
            -int(priority),
            -int(power),
            row["name_en"],
        )

    highlighted_moves_by_pokemon: dict[int, list[dict]] = {}
    move_rows_by_pokemon: dict[int, list[dict]] = {}
    for row in move_rows:
        move_rows_by_pokemon.setdefault(int(row["pokemon_id"]), []).append(row)
    for pokemon_id, rows in move_rows_by_pokemon.items():
        selected = sorted(rows, key=move_sort_key)[:5]
        highlighted_moves_by_pokemon[pokemon_id] = [
            {
                "move_key": row["move_key"],
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "type_key": row["type_key"],
                "category_key": row["category_key"],
                "power": row["power"],
                "accuracy": row["accuracy"],
                "priority": row["priority"],
                "effect_short_en": row.get("effect_short_en") or "",
                "effect_short_es": row.get("effect_short_es") or "",
                "is_in_move_pool": int(row.get("is_in_move_pool") or 0),
                "is_observed_in_sets": int(row.get("is_observed_in_sets") or 0),
            }
            for row in selected
        ]

    mega_by_pokemon: dict[int, dict] = {}
    for row in mega_rows:
        pokemon_id = int(row["pokemon_id"])
        mega_by_pokemon[pokemon_id] = {
            "mega_key": row["mega_key"],
            "mega_name_en": row["mega_name_en"],
            "mega_name_es": row.get("mega_name_es") or row["mega_name_en"],
            "mega_stone_key": row["mega_stone_key"],
            "mega_stone_name_en": row["mega_stone_name_en"],
            "mega_stone_name_es": row.get("mega_stone_name_es") or row["mega_stone_name_en"],
            "type1_key": row["type1_key"],
            "type2_key": row.get("type2_key") or "",
            "stats": {
                "hp": row["hp"],
                "attack": row["attack"],
                "defense": row["defense"],
                "sp_attack": row["sp_attack"],
                "sp_defense": row["sp_defense"],
                "speed": row["speed"],
                "bst": row["bst"],
            },
            "ability": {
                "ability_key": row.get("ability_key") or "",
                "name_en": row.get("ability_name_en") or "",
                "name_es": row.get("ability_name_es") or row.get("ability_name_en") or "",
                "description_en": row.get("ability_description_en") or "",
                "description_es": row.get("ability_description_es") or "",
            },
        }

    output = []
    for row in detail_rows:
        pokemon_id = int(row["pokemon_id"])
        output.append(
            {
                "pokemon_id": pokemon_id,
                "name_en": row["name_en"],
                "name_es": row.get("name_es") or row["name_en"],
                "form_name_en": row.get("form_name_en") or "",
                "form_name_es": row.get("form_name_es") or "",
                "abilities": abilities_by_pokemon.get(pokemon_id, []),
                "highlighted_moves": highlighted_moves_by_pokemon.get(pokemon_id, []),
                "mega_evolution": mega_by_pokemon.get(pokemon_id),
            }
        )
    return output


def ensure_bundle_dirs() -> None:
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    (BUNDLE / "db").mkdir(parents=True, exist_ok=True)
    (BUNDLE / "docs").mkdir(parents=True, exist_ok=True)
    (BUNDLE / "scripts").mkdir(parents=True, exist_ok=True)
    (BUNDLE / "exports").mkdir(parents=True, exist_ok=True)


def copy_bundle_files() -> None:
    shutil.copy2(DB_SRC, BUNDLE / "db" / "pokemon_champions.sqlite")
    for doc_name in DOCS_TO_COPY:
        shutil.copy2(BASE / "docs" / doc_name, BUNDLE / "docs" / doc_name)
    for script_name in SCRIPTS_TO_COPY:
        shutil.copy2(BASE / "scripts" / script_name, BUNDLE / "scripts" / script_name)


def export_json() -> dict[str, str]:
    conn = sqlite3.connect(DB_SRC)
    conn.row_factory = sqlite3.Row
    try:
        custom_exports = {
            "pokemon_list.json": build_pokemon_list_export(conn),
            "pokemon_detail_index.json": build_pokemon_detail_export(conn),
            "pokemon_home_context_detail.json": build_pokemon_home_context_detail_export(conn),
            "move_users.json": build_move_users_export(conn),
        }
        export_sources = {
            "pokemon_list.json": "Derived from v_team_builder_pool + v_pokemon_roles_summary + v_pokemon_archetypes_summary",
            "pokemon_detail_index.json": "Derived from v_pokemon_summary + v_pokemon_abilities_summary + v_pokemon_roles_summary + v_pokemon_archetypes_summary",
            "pokemon_home_context_detail.json": "Derived from pokemon + v_pokemon_abilities_summary + v_pokemon_moves_summary + moves + mega_forms + abilities",
            "move_users.json": "Derived from v_move_users + v_move_user_links",
        }
        for filename, query in EXPORT_QUERIES.items():
            rows = custom_exports.get(filename)
            if rows is None:
                rows = fetch_rows(conn, query)
                export_sources[filename] = query
            (BUNDLE / "exports" / filename).write_text(
                json.dumps(rows, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    finally:
        conn.close()
    return export_sources


def fetch_scalar(conn: sqlite3.Connection, query: str) -> int:
    return int(conn.execute(query).fetchone()[0])


def build_handoff() -> None:
    handoff = """# Handoff para Agente Web

## Qué archivo debes consumir primero

1. `manifest.json`
2. `docs/handoff.md`

Con esos dos archivos ya deberías poder empezar a trabajar sin inspección manual larga.

## Qué SQLite debes usar

- Archivo principal: `db/pokemon_champions.sqlite`

No uses CSV sueltos como fuente primaria en el repo web. El contrato operativo de consumo es la SQLite y, cuando convenga, los JSON de `exports/`.

## Qué vistas usar en frontend

### Listado principal

- `v_team_builder_pool`

Usa esta vista para:

- listados de Pokemon legales
- búsqueda por nombre
- filtros por tier
- filtros por rol o arquetipo ya derivados
- nombres localizados desde el propio export de listado

### Detalle de Pokemon

- `v_pokemon_summary`

Usa esta vista para:

- ficha base
- tipos
- stats base
- habilidades actuales
- roles y arquetipos derivados
- tier actual

Y usa estos exports estructurados para evitar joins locales:

- `exports/pokemon_detail_index.json`
- `exports/pokemon_home_context_detail.json`
- `exports/pokemon_abilities_summary.json`
- `exports/pokemon_moves_summary.json`

### Búsqueda y filtros de velocidad

- `v_speed_table`

Usa esta vista para:

- speed tiers
- filtros por velocidad base
- candidatos de Espacio Raro

### Búsqueda y filtros de movimientos

- `v_move_users`

Campos relevantes:

- `move_key`
- `name_en`
- `move_pool_user_count`
- `observed_set_user_count`
- `observed_set_coverage_pct`
- `users`
- `name_es`

Interpretación:

- `move_pool_user_count`: cuantos Pokemon tienen ese movimiento en el move pool actual de Champions
- `observed_set_user_count`: cuantos Pokemon lo llevan en sets observados
- `observed_set_coverage_pct`: proporcion observada respecto al move pool
- en el export JSON, `users` sale estructurado y enlazable por `pokemon_id`

### Filtros temáticos rápidos

- `v_rain_candidates`
- `v_sun_candidates`
- `v_trick_room_candidates`
- `v_charizard_answers`

## Qué campos son estables

Trátalos como identificadores estables para integración:

- `pokemon_id`
- `species_key`
- `form_key`
- `move_key`
- `ability_key`
- `item_key`
- `season_key`

Notas:

- `species_key` no es único por sí solo
- la clave funcional de especie+forma es `species_key + form_key`
- para detalle y joins, prioriza `pokemon_id`

## Qué partes son derivadas y no debes presentar como oficiales

Estas tablas no son dato oficial del juego:

- `pokemon_roles`
- `pokemon_archetypes`
- `cores`
- `matchups`

Regla de presentación:

- pueden mostrarse como análisis, sugerencia o clasificación táctica
- no deben mostrarse como si fueran reglas oficiales, tier oficial o dato interno del juego

## Qué partes sí son dato confirmado o estructural

Base estructural confirmada para el estado actual del bundle:

- `pokemon`
- `stats_base`
- `pokemon_abilities`
- `moves`
- `pokemon_moves`
- `items`
- `mega_forms`
- `tiers`
- `speed_profiles`
- `seasons_rules`
- `types`
- `sources`

Importante sobre `pokemon_moves`:

- ya no sale de un learnset genérico de Scarlet/Violet
- sale del move pool actual visible en Champions Lab
- además puede incluir capa `observed_set` para movimientos vistos en sets

## Cobertura localizada a tener en cuenta

- `name_es` ya tiene cobertura completa en Pokemon, habilidades, movimientos e ítems
- `description_es` de habilidades y `effect_*_es` de movimientos tienen cobertura alta pero no total
- `effect_*_es` de ítems sigue sin cobertura fiable; la app debe prever fallback limpio al inglés en ese punto
- `roles` y `archetypes` sí tienen nombres y descripciones bilingües completas

## Recomendación de consumo web

Si quieres minimizar complejidad:

1. usa `v_team_builder_pool` para listados
2. usa `v_pokemon_summary` para detalle
3. usa `v_speed_table` para speed logic
4. usa `v_move_users` para búsquedas por movimiento
5. usa los exports `pokemon_abilities_summary.json`, `pokemon_moves_summary.json`, `pokemon_roles_summary.json` y `pokemon_archetypes_summary.json` para detalle y localización sin joins locales
6. para contexto ligero en home, usa `pokemon_home_context_detail.json`; ya trae habilidades, 5 movimientos destacados y megaevolución resumida por `pokemon_id`

Si necesitas páginas estáticas o caché:

- puedes consumir directamente los JSON de `exports/`
- cada JSON está exportado desde una vista o query documentada en `manifest.json`
"""
    (BUNDLE / "docs" / "handoff.md").write_text(handoff, encoding="utf-8")


def build_manifest(export_sources: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_SRC)
    try:
        generated_at = datetime.now(timezone.utc)
        manifest = {
            "bundle_version": generated_at.strftime("%Y.%m.%d.1"),
            "generated_at": generated_at.date().isoformat(),
            "sqlite_path": "db/pokemon_champions.sqlite",
            "recommended_frontend_views": [
                "v_team_builder_pool",
                "v_pokemon_summary",
                "v_speed_table",
                "v_move_users",
                "v_rain_candidates",
                "v_sun_candidates",
                "v_trick_room_candidates",
                "v_charizard_answers",
            ],
            "recommended_frontend_usage": {
                "listing": "v_team_builder_pool",
                "detail": "v_pokemon_summary",
                "home_context_detail": "exports/pokemon_home_context_detail.json",
                "search_and_filters": "v_team_builder_pool",
                "speed_filters": "v_speed_table",
                "move_lookup": "v_move_users",
                "pokemon_abilities": "v_pokemon_abilities_summary",
                "pokemon_moves": "v_pokemon_moves_summary",
                "pokemon_roles": "v_pokemon_roles_summary",
                "pokemon_archetypes": "v_pokemon_archetypes_summary",
                "threat_answers": "v_charizard_answers",
            },
            "derived_or_non_official_tables": {
                "pokemon_roles": "Derived from Champions move pool, observed sets, stats and heuristics. Do not present as official game data.",
                "pokemon_archetypes": "Derived from Champions Lab curated teams, core pairs and heuristics. Do not present as official game data.",
                "cores": "Parsed from Champions Lab Meta. Useful but not official game data.",
                "matchups": "Derived matchup layer. Do not present as official game data.",
            },
            "reading_order": [
                "manifest.json",
                "docs/handoff.md",
                "docs/schema.md",
                "docs/specifications.md",
                "docs/validation_report.md",
                "docs/source_policy.md",
            ],
            "exact_commands": {
                "validate": ["python scripts\\validate_data.py"],
                "rebuild_current_data": [
                    "python scripts\\sync_current_champions.py",
                    "python scripts\\derive_competitive_layer.py",
                    "python scripts\\build_db.py",
                    "python scripts\\export_views.py",
                    "python scripts\\build_data_bundle.py",
                ],
                "release_bundle": ["powershell -ExecutionPolicy Bypass -File scripts\\release_bundle.ps1"],
                "export": ["python scripts\\export_views.py"],
            },
            "compatibility_notes": [
                "This bundle format replaces the old web_ready_bundle handoff.",
                "v_move_users returns one row per move and exposes move_pool_user_count, observed_set_user_count and observed_set_coverage_pct.",
                "pokemon_moves is sourced from Champions Lab current move pool plus observed sets, not from generic Scarlet/Violet learnsets.",
                "pokemon_list.json now includes localized display names and structured role/archetype relations.",
                "pokemon_detail_index.json now includes structured abilities, roles and archetypes for detail pages.",
                "pokemon_home_context_detail.json provides lightweight contextual detail for home cards or previews, including abilities, five highlighted moves and mega evolution summary.",
                "move_users.json now exposes localized move names and structured users linked by pokemon_id.",
                "Localized ES names are complete for pokemon, abilities, moves and items; descriptive ES coverage remains partial for abilities and moves, and absent for items.",
            ],
            "stable_identifiers": [
                "pokemon_id",
                "species_key",
                "form_key",
                "move_key",
                "ability_key",
                "item_key",
                "season_key",
            ],
            "exports": [{"file": name, "source": query} for name, query in export_sources.items()],
            "bundle_contents_summary": {
                "v_pokemon_summary_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM v_pokemon_summary"),
                "v_move_users_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM v_move_users"),
                "v_pokemon_abilities_summary_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM v_pokemon_abilities_summary"),
                "v_pokemon_moves_summary_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM v_pokemon_moves_summary"),
                "pokemon_roles_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM pokemon_roles"),
                "pokemon_archetypes_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM pokemon_archetypes"),
                "cores_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM cores"),
                "matchups_rows": fetch_scalar(conn, "SELECT COUNT(*) FROM matchups"),
            },
        }
    finally:
        conn.close()
    (BUNDLE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ensure_bundle_dirs()
    copy_bundle_files()
    export_sources = export_json()
    build_handoff()
    build_manifest(export_sources)
    print(f"[OK] data_bundle generado en {BUNDLE}")


if __name__ == "__main__":
    main()
