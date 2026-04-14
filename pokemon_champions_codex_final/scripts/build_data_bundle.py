from __future__ import annotations

from pathlib import Path
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
    "speed_profiles.json": "SELECT * FROM v_speed_table",
    "move_users.json": "SELECT * FROM v_move_users",
    "rain_candidates.json": "SELECT * FROM v_rain_candidates",
    "sun_candidates.json": "SELECT * FROM v_sun_candidates",
    "trick_room_candidates.json": "SELECT * FROM v_trick_room_candidates",
    "charizard_answers.json": "SELECT * FROM v_charizard_answers",
    "types.json": "SELECT * FROM types",
    "sources.json": "SELECT * FROM sources",
}


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
        for filename, query in EXPORT_QUERIES.items():
            rows = [dict(row) for row in conn.execute(query).fetchall()]
            (BUNDLE / "exports" / filename).write_text(
                json.dumps(rows, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    finally:
        conn.close()
    return EXPORT_QUERIES.copy()


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

### Detalle de Pokemon

- `v_pokemon_summary`

Usa esta vista para:

- ficha base
- tipos
- stats base
- habilidades actuales
- roles y arquetipos derivados
- tier actual

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

Interpretación:

- `move_pool_user_count`: cuantos Pokemon tienen ese movimiento en el move pool actual de Champions
- `observed_set_user_count`: cuantos Pokemon lo llevan en sets observados
- `observed_set_coverage_pct`: proporcion observada respecto al move pool

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

## Recomendación de consumo web

Si quieres minimizar complejidad:

1. usa `v_team_builder_pool` para listados
2. usa `v_pokemon_summary` para detalle
3. usa `v_speed_table` para speed logic
4. usa `v_move_users` para búsquedas por movimiento

Si necesitas páginas estáticas o caché:

- puedes consumir directamente los JSON de `exports/`
- cada JSON está exportado desde una vista o query documentada en `manifest.json`
"""
    (BUNDLE / "docs" / "handoff.md").write_text(handoff, encoding="utf-8")


def build_manifest(export_sources: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_SRC)
    try:
        manifest = {
            "bundle_version": "2026.04.14.1",
            "generated_at": "2026-04-14",
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
                "search_and_filters": "v_team_builder_pool",
                "speed_filters": "v_speed_table",
                "move_lookup": "v_move_users",
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
