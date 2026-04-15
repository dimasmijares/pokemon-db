from pathlib import Path
import csv
import json
import sys
from typing import Optional

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data_raw"
BUILD = BASE / "data_build"


def read_csv(csv_name: str) -> list[dict[str, str]]:
    with (RAW / csv_name).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def count_rows(csv_name: str) -> int:
    return len(read_csv(csv_name))


def duplicate_values(rows: list[dict[str, str]], columns: list[str]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for row in rows:
        key = " | ".join((row.get(column) or "").strip() for column in columns)
        if not key.strip():
            continue
        counts[key] = counts.get(key, 0) + 1
    return sorted((item for item in counts.items() if item[1] > 1), key=lambda item: item[0])


def missing_translation_count(rows: list[dict[str, str]], en_col: str, es_col: str) -> int:
    return sum(1 for row in rows if row.get(en_col) and not row.get(es_col))


def filled_translation_count(rows: list[dict[str, str]], column: str) -> int:
    return sum(1 for row in rows if (row.get(column) or "").strip())


def orphan_count(rows: list[dict[str, str]], key: str, valid_keys: set[str]) -> int:
    return sum(1 for row in rows if row.get(key) and row.get(key) not in valid_keys)


def print_section(title: str) -> None:
    print(f"\n{title}")


def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def percent_drop(previous: int, current: int) -> float:
    if previous <= 0:
        return 0.0
    return (previous - current) / previous


def main() -> int:
    files = sorted(path.name for path in RAW.glob("*.csv"))
    datasets = {name: read_csv(name) for name in files}

    print("Validación básica:")
    for name in files:
        print(f"- {name}: {count_rows(name)} filas de datos")

    pokemon_rows = datasets["pokemon.csv"]
    stats_rows = datasets["stats_base.csv"]
    tiers_rows = datasets["tiers.csv"]
    roles_rows = datasets["roles.csv"]
    pokemon_roles_rows = datasets["pokemon_roles.csv"]
    archetypes_rows = datasets["archetypes.csv"]
    pokemon_archetypes_rows = datasets["pokemon_archetypes.csv"]
    abilities_rows = datasets["abilities.csv"]
    pokemon_abilities_rows = datasets["pokemon_abilities.csv"]
    moves_rows = datasets["moves.csv"]
    pokemon_moves_rows = datasets["pokemon_moves.csv"]
    mega_rows = datasets["mega_forms.csv"]
    items_rows = datasets["items.csv"]
    speed_rows = datasets["speed_profiles.csv"]
    season_rows = datasets["seasons_rules.csv"]
    sources_rows = datasets["sources.csv"]
    matchups_rows = datasets["matchups.csv"]
    cores_rows = datasets["cores.csv"]

    pokemon_ids = {row["pokemon_id"] for row in pokemon_rows if row.get("pokemon_id")}
    role_keys = {row["role_key"] for row in roles_rows if row.get("role_key")}
    archetype_keys = {row["archetype_key"] for row in archetypes_rows if row.get("archetype_key")}
    ability_keys = {row["ability_key"] for row in abilities_rows if row.get("ability_key")}
    move_keys = {row["move_key"] for row in moves_rows if row.get("move_key")}
    item_keys = {row["item_key"] for row in items_rows if row.get("item_key")}
    source_keys = {row["source_key"] for row in sources_rows if row.get("source_key")}
    season_keys = {row["season_key"] for row in season_rows if row.get("season_key")}

    failures: list[str] = []
    warnings: list[str] = []
    sync_summary = load_json(BUILD / "sync_summary.json")
    previous_summary = load_json(BUILD / "validation_summary.json")

    print_section("Validaciones de claves")
    pokemon_id_duplicates = duplicate_values(pokemon_rows, ["pokemon_id"])
    if pokemon_id_duplicates:
        failures.append(f"pokemon_id duplicados: {len(pokemon_id_duplicates)}")
        print(f"- FAIL: pokemon_id duplicados: {pokemon_id_duplicates[:10]}")
    else:
        print("- OK: pokemon_id únicos")

    pokemon_natural_duplicates = duplicate_values(pokemon_rows, ["species_key", "form_key"])
    if pokemon_natural_duplicates:
        failures.append(f"duplicados en species_key + form_key: {len(pokemon_natural_duplicates)}")
        print(f"- FAIL: duplicados en species_key + form_key: {pokemon_natural_duplicates[:10]}")
    else:
        print("- OK: species_key + form_key únicos")

    species_only_duplicates = duplicate_values(pokemon_rows, ["species_key"])
    if species_only_duplicates:
        warnings.append(f"species_key repetido en {len(species_only_duplicates)} especies con formas")
        print(f"- WARN: species_key repetido en {len(species_only_duplicates)} especies; usar junto con form_key")
    else:
        print("- OK: species_key sin repeticiones")

    print_section("Validaciones de traducción")
    missing_name_es = missing_translation_count(pokemon_rows, "name_en", "name_es")
    if missing_name_es:
        warnings.append(f"faltan {missing_name_es} traducciones en pokemon.csv")
        print(f"- WARN: faltan {missing_name_es} traducciones en pokemon.csv")
    else:
        print("- OK: traducciones presentes en pokemon.csv")

    print_section("Cobertura localizada ES")
    localization_metrics = {
        "pokemon_name_es": (filled_translation_count(pokemon_rows, "name_es"), len(pokemon_rows)),
        "abilities_name_es": (filled_translation_count(abilities_rows, "name_es"), len(abilities_rows)),
        "abilities_description_es": (filled_translation_count(abilities_rows, "description_es"), len(abilities_rows)),
        "moves_name_es": (filled_translation_count(moves_rows, "name_es"), len(moves_rows)),
        "moves_effect_short_es": (filled_translation_count(moves_rows, "effect_short_es"), len(moves_rows)),
        "moves_effect_long_es": (filled_translation_count(moves_rows, "effect_long_es"), len(moves_rows)),
        "items_name_es": (filled_translation_count(items_rows, "name_es"), len(items_rows)),
        "items_effect_short_es": (filled_translation_count(items_rows, "effect_short_es"), len(items_rows)),
        "items_effect_long_es": (filled_translation_count(items_rows, "effect_long_es"), len(items_rows)),
        "roles_name_es": (filled_translation_count(roles_rows, "name_es"), len(roles_rows)),
        "roles_description_es": (filled_translation_count(roles_rows, "description_es"), len(roles_rows)),
        "archetypes_name_es": (filled_translation_count(archetypes_rows, "name_es"), len(archetypes_rows)),
        "archetypes_description_es": (filled_translation_count(archetypes_rows, "description_es"), len(archetypes_rows)),
    }
    for metric_name, (filled, total) in localization_metrics.items():
        pct = (filled / total * 100) if total else 0
        print(f"- {metric_name}: {filled}/{total} ({pct:.1f}%)")

    if localization_metrics["abilities_description_es"][0] < localization_metrics["abilities_description_es"][1]:
        warnings.append("cobertura ES incompleta en descriptions de abilities")
    if localization_metrics["moves_effect_short_es"][0] < localization_metrics["moves_effect_short_es"][1]:
        warnings.append("cobertura ES incompleta en effect_short de moves")
    if localization_metrics["items_effect_short_es"][0] < localization_metrics["items_effect_short_es"][1]:
        warnings.append("cobertura ES incompleta en effect_short de items")

    print_section("Validaciones referenciales")
    ref_checks = [
        ("stats_base.csv", orphan_count(stats_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("pokemon_abilities.csv", orphan_count(pokemon_abilities_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("pokemon_abilities.csv", orphan_count(pokemon_abilities_rows, "ability_key", ability_keys), "ability_key huérfanos"),
        ("pokemon_moves.csv", orphan_count(pokemon_moves_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("pokemon_moves.csv", orphan_count(pokemon_moves_rows, "move_key", move_keys), "move_key huérfanos"),
        ("tiers.csv", orphan_count(tiers_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("tiers.csv", orphan_count(tiers_rows, "season_key", season_keys), "season_key huérfanos"),
        ("pokemon_roles.csv", orphan_count(pokemon_roles_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("pokemon_roles.csv", orphan_count(pokemon_roles_rows, "role_key", role_keys), "role_key huérfanos"),
        ("pokemon_roles.csv", orphan_count(pokemon_roles_rows, "season_key", season_keys), "season_key huérfanos"),
        ("pokemon_archetypes.csv", orphan_count(pokemon_archetypes_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("pokemon_archetypes.csv", orphan_count(pokemon_archetypes_rows, "archetype_key", archetype_keys), "archetype_key huérfanos"),
        ("pokemon_archetypes.csv", orphan_count(pokemon_archetypes_rows, "season_key", season_keys), "season_key huérfanos"),
        ("speed_profiles.csv", orphan_count(speed_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("speed_profiles.csv", orphan_count(speed_rows, "season_key", season_keys), "season_key huérfanos"),
        ("mega_forms.csv", orphan_count(mega_rows, "pokemon_id", pokemon_ids), "pokemon_id huérfanos"),
        ("mega_forms.csv", orphan_count(mega_rows, "mega_stone_key", item_keys), "mega_stone_key huérfanos"),
        ("matchups.csv", orphan_count(matchups_rows, "threat_pokemon_id", pokemon_ids), "threat_pokemon_id huérfanos"),
        ("matchups.csv", orphan_count(matchups_rows, "answer_pokemon_id", pokemon_ids), "answer_pokemon_id huérfanos"),
        ("matchups.csv", orphan_count(matchups_rows, "season_key", season_keys), "season_key huérfanos"),
        ("cores.csv", orphan_count(cores_rows, "pokemon_1_id", pokemon_ids), "pokemon_1_id huérfanos"),
        ("cores.csv", orphan_count(cores_rows, "pokemon_2_id", pokemon_ids), "pokemon_2_id huérfanos"),
        ("cores.csv", orphan_count(cores_rows, "pokemon_3_id", pokemon_ids), "pokemon_3_id huérfanos"),
        ("cores.csv", orphan_count(cores_rows, "season_key", season_keys), "season_key huérfanos"),
    ]
    for csv_name, count, description in ref_checks:
        if count:
            failures.append(f"{csv_name}: {description} = {count}")
            print(f"- FAIL: {csv_name}: {description} = {count}")
        else:
            print(f"- OK: {csv_name}: {description}")

    print_section("Validaciones de fuente")
    for csv_name, rows, source_column in [
        ("pokemon.csv", pokemon_rows, "roster_source_key"),
        ("stats_base.csv", stats_rows, "source_key"),
        ("pokemon_abilities.csv", pokemon_abilities_rows, "source_key"),
        ("pokemon_moves.csv", pokemon_moves_rows, "source_key"),
        ("items.csv", items_rows, "source_key"),
        ("tiers.csv", tiers_rows, "tier_source_key"),
        ("pokemon_roles.csv", pokemon_roles_rows, "curation_source_key"),
    ]:
        missing = orphan_count(rows, source_column, source_keys)
        if missing:
            warnings.append(f"{csv_name}: {source_column} sin registrar = {missing}")
            print(f"- WARN: {csv_name}: {source_column} sin registrar = {missing}")
        else:
            print(f"- OK: {csv_name}: {source_column}")

    print_section("Cobertura funcional")
    current_season = season_rows[0]["season_key"] if season_rows else ""
    legal_pokemon_count = sum(1 for row in pokemon_rows if row.get("is_currently_legal") == "1")
    stats_coverage = len({row["pokemon_id"] for row in stats_rows if row.get("pokemon_id")})
    tier_coverage = len(
        {
            row["pokemon_id"]
            for row in tiers_rows
            if row.get("season_key") == current_season and row.get("format") == "doubles"
        }
    )
    speed_coverage = len(
        {
            row["pokemon_id"]
            for row in speed_rows
            if row.get("season_key") == current_season and row.get("format") == "doubles"
        }
    )
    print(f"- legal_pokemon_count: {legal_pokemon_count}")
    print(f"- stats_coverage: {stats_coverage}/{len(pokemon_ids)}")
    print(f"- tier_coverage_doubles_current: {tier_coverage}/{legal_pokemon_count}")
    print(f"- speed_coverage_doubles_current: {speed_coverage}/{legal_pokemon_count}")
    if stats_coverage < len(pokemon_ids):
        warnings.append("cobertura de stats incompleta")
    if tier_coverage < legal_pokemon_count:
        warnings.append("cobertura de tiers incompleta")
    if speed_coverage < legal_pokemon_count:
        warnings.append("cobertura de speed profiles incompleta")

    print_section("Validaciones de scraping")
    if not sync_summary:
        warnings.append("falta data_build/sync_summary.json; no hay trazabilidad de scraping")
        print("- WARN: falta data_build/sync_summary.json")
    else:
        source_health = sync_summary.get("source_health", {})
        dataset_metrics = sync_summary.get("dataset_metrics", {})
        automation_signals = sync_summary.get("automation_signals", {})

        home_expected = int(source_health.get("championslab_home_expected_roster_count") or 0)
        home_actual = int(source_health.get("championslab_home_extracted_roster_count") or 0)
        if home_expected and home_expected != home_actual:
            failures.append("Champions Lab roster count no coincide con lo esperado")
            print(f"- FAIL: Champions Lab roster count {home_actual}/{home_expected}")
        else:
            print(f"- OK: Champions Lab roster count {home_actual}/{home_expected}")

        bulba_parse_method = source_health.get("bulbapedia_parse_method", "")
        print(f"- INFO: Bulbapedia parse method = {bulba_parse_method}")
        if automation_signals.get("has_bulbapedia_fallback_parser"):
            warnings.append("Bulbapedia se extrajo con parser fallback de bloques de texto")

        if int(source_health.get("championslab_pokedex_entries") or 0) < legal_pokemon_count:
            failures.append("Pokédex de Champions Lab insuficiente para el roster actual")
            print("- FAIL: pokedex entries de Champions Lab por debajo del roster legal")
        else:
            print(f"- OK: pokedex entries de Champions Lab = {source_health.get('championslab_pokedex_entries')}")

        if int(dataset_metrics.get("pokemon_move_pool_rows") or 0) <= 0:
            failures.append("pokemon_moves sin capa champions_move_pool")
            print("- FAIL: pokemon_moves sin champions_move_pool")
        else:
            print(f"- OK: champions_move_pool rows = {dataset_metrics.get('pokemon_move_pool_rows')}")

        if int(dataset_metrics.get("pokemon_observed_set_rows") or 0) <= 0:
            warnings.append("pokemon_moves sin observed_set")
            print("- WARN: pokemon_moves sin observed_set")
        else:
            print(f"- OK: observed_set rows = {dataset_metrics.get('pokemon_observed_set_rows')}")

        manual_mega_ratio = float(automation_signals.get("manual_curation_mega_ratio") or 0)
        if manual_mega_ratio > 0.35:
            warnings.append("exceso de megas con fallback manual")
            print(f"- WARN: manual_curation_mega_ratio = {manual_mega_ratio:.2%}")
        else:
            print(f"- OK: manual_curation_mega_ratio = {manual_mega_ratio:.2%}")

    print_section("Comparativa con ejecución anterior")
    current_summary = {
        "generated_at": (sync_summary or {}).get("generated_at", ""),
        "season_key": current_season,
        "metrics": {
            "legal_pokemon_count": legal_pokemon_count,
            "stats_coverage": stats_coverage,
            "tier_coverage_doubles_current": tier_coverage,
            "speed_coverage_doubles_current": speed_coverage,
            "mega_forms_count": len(mega_rows),
            "moves_catalog_count": len(moves_rows),
            "pokemon_moves_count": len(pokemon_moves_rows),
            "champions_move_pool_count": sum(1 for row in pokemon_moves_rows if row.get("availability_status") == "champions_move_pool"),
            "observed_set_count": sum(1 for row in pokemon_moves_rows if row.get("availability_status") == "observed_set"),
            "matchups_count": len(matchups_rows),
            "abilities_description_es_coverage": localization_metrics["abilities_description_es"][0],
            "moves_effect_short_es_coverage": localization_metrics["moves_effect_short_es"][0],
            "moves_effect_long_es_coverage": localization_metrics["moves_effect_long_es"][0],
            "items_effect_short_es_coverage": localization_metrics["items_effect_short_es"][0],
            "items_effect_long_es_coverage": localization_metrics["items_effect_long_es"][0],
        },
        "localization_metrics": {
            metric_name: {
                "filled": filled,
                "total": total,
                "pct": round((filled / total * 100), 1) if total else 0,
            }
            for metric_name, (filled, total) in localization_metrics.items()
        },
        "warnings": warnings,
        "failures": failures,
        "sync_summary": sync_summary or {},
    }
    if previous_summary and previous_summary.get("metrics"):
        for metric_name, current_value in current_summary["metrics"].items():
            previous_value = int(previous_summary["metrics"].get(metric_name) or 0)
            if previous_value <= 0:
                continue
            drop = percent_drop(previous_value, int(current_value))
            if drop > 0.25:
                failures.append(f"regresión fuerte en {metric_name}: {current_value}/{previous_value}")
                print(f"- FAIL: {metric_name} cayó a {current_value} desde {previous_value}")
            elif drop > 0.10:
                warnings.append(f"regresión moderada en {metric_name}: {current_value}/{previous_value}")
                print(f"- WARN: {metric_name} cayó a {current_value} desde {previous_value}")
            else:
                print(f"- OK: {metric_name} = {current_value} (previo {previous_value})")
    else:
        print("- INFO: no hay validation_summary.json previo para comparar")

    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "validation_summary.json").write_text(
        json.dumps(current_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print_section("Resultado")
    if failures:
        print(f"- FAIL: {len(failures)} errores críticos")
        for failure in failures:
            print(f"  {failure}")
    else:
        print("- OK: sin errores críticos")

    if warnings:
        print(f"- WARN: {len(warnings)} avisos")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("- OK: sin avisos")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
