from __future__ import annotations

from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import csv
import json
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data_raw"
BUILD = BASE / "data_build"
TODAY = datetime.now(timezone.utc).date().isoformat()
SEASON_KEY = "season_m1_reg_ma"

CHAMPIONS_LAB_HOME = "https://championslab.xyz/"
CHAMPIONS_LAB_META = "https://championslab.xyz/meta"
BULBAPEDIA_ROSTER_URL = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_in_Pok%C3%A9mon_Champions"
POKEAPI_BASE = "https://pokeapi.co/api/v2"

GENERATION_MAP = {
    "generation-i": 1,
    "generation-ii": 2,
    "generation-iii": 3,
    "generation-iv": 4,
    "generation-v": 5,
    "generation-vi": 6,
    "generation-vii": 7,
    "generation-viii": 8,
    "generation-ix": 9,
}

TYPE_COLORS = {
    "normal",
    "fighting",
    "flying",
    "poison",
    "ground",
    "rock",
    "bug",
    "ghost",
    "steel",
    "fire",
    "water",
    "grass",
    "electric",
    "psychic",
    "ice",
    "dragon",
    "dark",
    "fairy",
}

BULBAPEDIA_TYPES = {
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy",
}

ROLE_ROWS = [
    {"role_key": "speed_control", "name_en": "Speed Control", "name_es": "Control de Velocidad", "description_en": "Provides proactive or reverse speed control.", "description_es": "Aporta control de velocidad directo o inverso."},
    {"role_key": "pivot", "name_en": "Pivot", "name_es": "Pivot", "description_en": "Creates positioning or tempo through switching and utility.", "description_es": "Genera posicion o tempo mediante cambios y utilidad."},
    {"role_key": "wallbreaker", "name_en": "Wallbreaker", "name_es": "Muroperforador", "description_en": "Breaks through bulky cores using strong offensive pressure.", "description_es": "Rompe nucleos defensivos con presion ofensiva alta."},
    {"role_key": "bulky_support", "name_en": "Bulky Support", "name_es": "Soporte Resistente", "description_en": "Supports allies while maintaining defensive presence.", "description_es": "Apoya al equipo manteniendo presencia defensiva."},
    {"role_key": "weather_setter", "name_en": "Weather Setter", "name_es": "Setter de Clima", "description_en": "Sets weather that defines the game plan.", "description_es": "Activa el clima que define el plan de partida."},
]

ARCHETYPE_ROWS = [
    {"archetype_key": "sun", "name_en": "Sun", "name_es": "Sol", "description_en": "Structures built around sun.", "description_es": "Estructuras basadas en sol."},
    {"archetype_key": "rain", "name_en": "Rain", "name_es": "Lluvia", "description_en": "Structures built around rain.", "description_es": "Estructuras basadas en lluvia."},
    {"archetype_key": "sand", "name_en": "Sand", "name_es": "Arena", "description_en": "Structures built around sand.", "description_es": "Estructuras basadas en arena."},
    {"archetype_key": "trick_room", "name_en": "Trick Room", "name_es": "Espacio Raro", "description_en": "Structures built around reverse speed control.", "description_es": "Estructuras basadas en control inverso de velocidad."},
    {"archetype_key": "tailwind", "name_en": "Tailwind", "name_es": "Viento Afin", "description_en": "Structures built around Tailwind speed control.", "description_es": "Estructuras basadas en Viento Afin."},
    {"archetype_key": "balance", "name_en": "Balance", "name_es": "Balance", "description_en": "Flexible structures with both defensive and offensive pieces.", "description_es": "Estructuras flexibles con piezas ofensivas y defensivas."},
    {"archetype_key": "hyper_offense", "name_en": "Hyper Offense", "name_es": "Hiperofensiva", "description_en": "High-pressure offensive structures.", "description_es": "Estructuras ofensivas de alta presion."},
]

ITEM_FIELDNAMES = [
    "item_key",
    "name_en",
    "name_es",
    "category_key",
    "effect_short_en",
    "effect_short_es",
    "effect_long_en",
    "effect_long_es",
    "is_mega_stone",
    "source_key",
]

MOVE_FIELDNAMES = [
    "move_key",
    "name_en",
    "name_es",
    "type_key",
    "category_key",
    "power",
    "accuracy",
    "pp",
    "priority",
    "targeting_key",
    "makes_contact",
    "is_sound",
    "is_pulse",
    "is_punch",
    "is_bite",
    "is_slashing",
    "is_status",
    "effect_short_en",
    "effect_short_es",
    "effect_long_en",
    "effect_long_es",
    "source_key",
]

ABILITY_FIELDNAMES = [
    "ability_key",
    "name_en",
    "name_es",
    "description_en",
    "description_es",
    "is_signature",
    "source_key",
]


def request_text(url: str, session: requests.Session) -> str:
    response = session.get(
        url,
        timeout=60,
        headers={"User-Agent": "Mozilla/5.0 (compatible; pokemon-champions-db/1.0)"},
    )
    response.raise_for_status()
    return response.text


def request_json(url: str, session: requests.Session) -> dict:
    response = session.get(url, timeout=60, headers={"User-Agent": "pokemon-champions-db/1.0"})
    response.raise_for_status()
    return response.json()


def try_request_json(url: str, session: requests.Session) -> dict | None:
    response = session.get(url, timeout=60, headers={"User-Agent": "pokemon-champions-db/1.0"})
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("♀", "female").replace("♂", "male")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def normalize_resource_key(value: str) -> str:
    value = value.strip().lower().replace("’", "'")
    value = value.replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_compare_name(value: str) -> str:
    value = value.strip().lower().replace("’", "'")
    replacements = {
        "alolan ": "alola ",
        "galarian ": "galar ",
        "hisuian ": "hisui ",
        "paldean ": "paldea ",
        "wash rotom": "rotom wash",
        "heat rotom": "rotom heat",
        "frost rotom": "rotom frost",
        "fan rotom": "rotom fan",
        "mow rotom": "rotom mow",
        "(blaze) paldean tauros": "paldea tauros blaze",
        "(aqua) paldean tauros": "paldea tauros aqua",
        "(combat) paldean tauros": "paldea tauros combat",
        "paldean tauros blaze": "paldea tauros blaze",
        "paldean tauros aqua": "paldea tauros aqua",
        "paldean tauros combat": "paldea tauros combat",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = value.replace("-", " ")
    value = value.replace("(", " ").replace(")", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_human_date(value: str) -> str:
    return datetime.strptime(value, "%B %d, %Y").date().isoformat()


def parse_season_rules(seasons_dataset: list[dict]) -> dict[str, str | int]:
    active_season = next((season for season in seasons_dataset if season.get("isActive")), seasons_dataset[0] if seasons_dataset else {})
    rules = active_season.get("rules", []) or []

    def find_rule(fragment: str, default: str = "") -> str:
        return next((rule for rule in rules if fragment.lower() in rule.lower()), default)

    timer_rule = find_rule("timer")
    timer_match = re.search(r"(\d+)", timer_rule)

    return {
        "bring_pick_rule": find_rule("Bring", "Ranked Battles current regulation"),
        "level_rule": find_rule("Level", "50"),
        "mega_allowed": 1 if any("Mega" in rule for rule in rules) else 0,
        "duplicate_pokemon_allowed": 0 if any("No duplicate Pokémon" in rule or "No duplicate Pokemon" in rule for rule in rules) else "",
        "duplicate_items_allowed": 0 if any("No duplicate held items" in rule for rule in rules) else "",
        "timer_minutes": int(timer_match.group(1)) if timer_match else 10,
        "rules_source_text": " | ".join(rules),
    }


def fetch_championslab_home(session: requests.Session) -> tuple[list[dict], dict]:
    html = request_text(CHAMPIONS_LAB_HOME, session)
    season_match = re.search(
        r"(Season [^<]+?-\s+Regulation [^<]+)</h3><p[^>]*>([A-Za-z]+ \d{1,2}, \d{4})</p>.*?Season Ends</p><p[^>]*>([A-Za-z]+ \d{1,2}, \d{4})</p>.*?Regulation Until</p><p[^>]*>([A-Za-z]+ \d{1,2}, \d{4})</p>.*?>(\d+)<!-- --> in roster",
        html,
        re.S,
    )
    if not season_match:
        raise RuntimeError("No se pudo extraer la temporada activa de Champions Lab")

    season_info = {
        "season_name": season_match.group(1).replace("  ", " ").strip(),
        "start_date_human": season_match.group(2),
        "end_date_human": season_match.group(3),
        "regulation_until_human": season_match.group(4),
        "roster_count": int(season_match.group(5)),
    }

    card_pattern = re.compile(
        r'<div class="group relative cursor-pointer".*?'
        r'<span[^>]*>([SABCD])</span>.*?'
        r'src="/sprites/(\d+)\.png".*?'
        r'<h3[^>]*>([^<]+)</h3><span[^>]*>#<!-- -->(\d+)</span>.*?'
        r'<div class="flex gap-1\.5">(.*?)</div>',
        re.S,
    )
    roster = []
    for tier, sprite_id, display_name, dex_number, type_block in card_pattern.findall(html):
        types = re.findall(r">([a-z-]+)</span>", type_block)
        types = [type_name for type_name in types if type_name in TYPE_COLORS]
        roster.append(
            {
                "pokemon_id": int(sprite_id),
                "display_name": display_name.strip(),
                "dex_number": int(dex_number),
                "tier_value": tier,
                "type1_key": types[0] if types else "",
                "type2_key": types[1] if len(types) > 1 else "",
            }
        )

    if len(roster) != season_info["roster_count"]:
        raise RuntimeError(
            f"Champions Lab indica {season_info['roster_count']} Pokemon, pero se extrajeron {len(roster)}"
        )
    return roster, season_info


def fetch_bulbapedia_tables(session: requests.Session) -> tuple[pd.DataFrame, pd.DataFrame, str, str]:
    html = request_text(BULBAPEDIA_ROSTER_URL, session)
    tables = pd.read_html(StringIO(html))
    roster_table = tables[0]
    mega_table = tables[1]
    parse_method = "pandas_read_html"
    if roster_table.empty or "Ndex" not in roster_table.columns or mega_table.empty or "Ndex" not in mega_table.columns:
        roster_table, mega_table = parse_bulbapedia_text_tables(html)
        parse_method = "html_text_blocks"
    current_roster_match = re.search(
        r"Until ([A-Za-z]+ \d{1,2}, \d{4}), the current roster is ([^.]+)\.",
        html,
    )
    current_roster_until = current_roster_match.group(1) if current_roster_match else ""
    return roster_table, mega_table, current_roster_until, parse_method


def parse_bulbapedia_text_tables(html: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if re.fullmatch(r"#\d{4}", line):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    roster_rows: list[dict[str, str]] = []
    mega_rows: list[dict[str, str]] = []

    for block in blocks:
        dex = block[0]
        tokens = block[1:]
        i = 0
        while i < len(tokens):
            name = tokens[i]
            i += 1
            qualifiers: list[str] = []
            while i < len(tokens) and tokens[i] not in BULBAPEDIA_TYPES:
                qualifiers.append(tokens[i])
                i += 1

            if i >= len(tokens):
                break

            type_values: list[str] = []
            while i < len(tokens) and tokens[i] in BULBAPEDIA_TYPES:
                type_values.append(tokens[i].strip().lower())
                i += 1

            if i >= len(tokens):
                break

            availability = tokens[i]
            i += 1
            if i < len(tokens) and re.fullmatch(r"\d+\.\d+(?:\.\d+)?", tokens[i]):
                version_added = tokens[i]
                i += 1
            else:
                version_added = ""

            pokemon_label = " ".join([name, *qualifiers]).strip()
            row = {
                "Ndex": dex,
                "Pokémon": pokemon_label,
                "Type": type_values[0] if type_values else "",
                "Type.1": type_values[1] if len(type_values) > 1 else "",
                "Normally available?": availability,
                "Version added": version_added,
            }
            if any(part.startswith("Mega ") for part in qualifiers):
                mega_rows.append(row)
            else:
                roster_rows.append(row)

    if not roster_rows or not mega_rows:
        raise RuntimeError("No se pudo reconstruir la tabla de Bulbapedia desde el HTML actual")

    return pd.DataFrame(roster_rows), pd.DataFrame(mega_rows)


def build_bulbapedia_availability(roster_table: pd.DataFrame) -> dict[tuple[int, str], str]:
    availability = {}
    for _, row in roster_table.iterrows():
        dex = int(str(row["Ndex"]).replace("#", ""))
        pokemon_label = str(row["Pokémon"]).strip()
        availability_value = str(row["Normally available?"]).strip()
        availability[(dex, pokemon_label)] = availability_value
    return availability


def build_seed_lookup(rows: list[dict[str, str]]) -> dict[tuple[int, str, str], dict[str, str]]:
    lookup = {}
    for row in rows:
        key = (
            int(row["dex_number"]),
            row["name_en"].strip(),
            (row.get("form_name_en") or "").strip(),
        )
        lookup[key] = row
    return lookup


def load_seed_megas() -> dict[str, dict[str, str]]:
    rows = load_csv(RAW / "mega_forms.csv")
    return {row["mega_key"]: row for row in rows}


def normalize_availability(display_name: str, dex_number: int, availability_lookup: dict[tuple[int, str], str]) -> str:
    if "Floette" in display_name and "Eternal" in display_name:
        return "transfer_only"
    candidates = [
        availability_lookup.get((dex_number, display_name)),
        availability_lookup.get((dex_number, display_name.replace("Alolan ", "") + " Alolan Form")),
        availability_lookup.get((dex_number, display_name.replace("Hisuian ", "") + " Hisuian Form")),
        availability_lookup.get((dex_number, display_name.replace("Galarian ", "") + " Galarian Form")),
        availability_lookup.get((dex_number, display_name.replace("(Blaze) Paldean Tauros", "Paldean Tauros (Blaze)"))),
        availability_lookup.get((dex_number, display_name.replace("(Aqua) Paldean Tauros", "Paldean Tauros (Aqua)"))),
    ]
    availability = next((value for value in candidates if value), "Yes")
    if availability.lower().startswith("transfer"):
        return "transfer_only"
    if availability.lower().startswith("event"):
        return "event_only"
    return "standard"


def accurate_level_50_speeds(base_speed: int) -> dict[str, int | str]:
    def stat(iv: int, ev: int, nature: float) -> int:
        raw = ((2 * base_speed + iv + (ev // 4)) * 50) // 100 + 5
        return int(raw * nature)

    speed_min_negative = stat(0, 0, 0.9)
    speed_min_neutral = stat(0, 0, 1.0)
    speed_max_neutral = stat(31, 252, 1.0)
    speed_max_positive = stat(31, 252, 1.1)
    speed_max_positive_boosted_1 = int(speed_max_positive * 1.5)
    speed_max_positive_boosted_2 = speed_max_positive * 2

    if base_speed <= 55:
        trick_room_rating = "high"
    elif base_speed <= 80:
        trick_room_rating = "medium"
    else:
        trick_room_rating = "low"

    return {
        "speed_min_negative": speed_min_negative,
        "speed_min_neutral": speed_min_neutral,
        "speed_max_neutral": speed_max_neutral,
        "speed_max_positive": speed_max_positive,
        "speed_max_positive_boosted_1": speed_max_positive_boosted_1,
        "speed_max_positive_boosted_2": speed_max_positive_boosted_2,
        "trick_room_rating": trick_room_rating,
    }


def extract_js_literal(text: str, anchor: str, open_char: str, close_char: str, search_start: int = 0) -> str:
    idx = text.find(anchor, search_start)
    if idx == -1:
        raise RuntimeError(f"No se encontro el ancla JS: {anchor}")
    start = idx + len(anchor)
    depth = 1
    in_string = False
    escaping = False
    quote_char = ""
    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if in_string:
            if escaping:
                escaping = False
            elif char == "\\":
                escaping = True
            elif char == quote_char:
                in_string = False
        else:
            if char in {'"', "'"}:
                in_string = True
                quote_char = char
            elif char == open_char:
                depth += 1
            elif char == close_char:
                depth -= 1
                if depth == 0:
                    return text[start - 1 : cursor + 1]
        cursor += 1
    raise RuntimeError(f"Literal JS no cerrado para el ancla: {anchor}")


def js_literal_to_python(literal: str) -> list | dict:
    normalized = re.sub(r"\\x([0-9A-Fa-f]{2})", lambda match: "\\u00" + match.group(1), literal)
    normalized = normalized.replace("!0", "true").replace("!1", "false")
    normalized = re.sub(r"(:)\.(\d+)", r"\g<1>0.\2", normalized)
    normalized = re.sub(r"([\{,])(\s*)([A-Za-z_][A-Za-z0-9_]*|\d+)(\s*):", r'\1\2"\3"\4:', normalized)
    return json.loads(normalized)


def extract_championslab_literals(bundle_text: str) -> tuple[list[dict], dict[str, list[dict]], list[dict]]:
    module_match = re.search(
        r'a\.d\(t,\{Ns:\(\)=>([a-z]),su:\(\)=>([a-z]),w1:\(\)=>([a-z]),wv:\(\)=>([a-z])\}\);let ([a-z])=\[',
        bundle_text,
    )
    if not module_match:
        raise RuntimeError("No se pudo localizar el bloque principal de datos de Champions Lab")

    season_var = module_match.group(1)
    pokemon_var = module_match.group(2)
    season_literal = extract_js_literal(bundle_text, f"let {season_var}=[", "[", "]", module_match.start())
    pokemon_literal = extract_js_literal(bundle_text, f",{pokemon_var}=[", "[", "]", module_match.start())

    setdex_literal = ""
    for match in re.finditer(r'a\.d\(t,\{z:\(\)=>([a-z])\}\);let ([a-z])=\{', bundle_text):
        candidate_var = match.group(1)
        candidate_literal = extract_js_literal(bundle_text, f"let {candidate_var}={{", "{", "}", match.start())
        if "moves" in candidate_literal and "nature" in candidate_literal:
            setdex_literal = candidate_literal
            break
    if not setdex_literal:
        raise RuntimeError("No se pudo localizar el bloque setdex de Champions Lab")

    seasons = js_literal_to_python(season_literal)
    pokemon_entries = js_literal_to_python(pokemon_literal)
    setdex_entries = js_literal_to_python(setdex_literal)
    if not seasons or not isinstance(seasons, list) or not isinstance(seasons[0], dict) or "startDate" not in seasons[0]:
        raise RuntimeError("El bloque de temporadas extraido no tiene estructura valida")
    if not pokemon_entries or not isinstance(pokemon_entries, list) or not isinstance(pokemon_entries[0], dict) or "dexNumber" not in pokemon_entries[0]:
        raise RuntimeError("El bloque de pokedex extraido no tiene estructura valida")
    if not isinstance(setdex_entries, dict):
        raise RuntimeError("El bloque setdex extraido no tiene estructura valida")
    return pokemon_entries, setdex_entries, seasons


def resolve_bundle_candidates(page_html: str) -> list[str]:
    candidates = []
    for relative_path in re.findall(r'(/_next/static/chunks/[^"]+\.js)', page_html):
        if relative_path not in candidates:
            candidates.append(relative_path)
    candidates.sort(key=lambda path: (0 if "/880-" in path else 1, path))
    return [f"https://championslab.xyz{path}" for path in candidates]


def fetch_championslab_datasets(session: requests.Session) -> tuple[list[dict], dict[str, list[dict]], list[dict], str]:
    html = request_text(CHAMPIONS_LAB_META, session)
    candidate_urls = resolve_bundle_candidates(html)
    if not candidate_urls:
        raise RuntimeError("No se pudo localizar ningun chunk JS de Champions Lab")

    errors = []
    for bundle_url in candidate_urls:
        bundle_text = request_text(bundle_url, session)
        try:
            pokemon_entries, setdex_entries, seasons = extract_championslab_literals(bundle_text)
            return pokemon_entries, setdex_entries, seasons, bundle_url
        except RuntimeError as exc:
            errors.append(f"{bundle_url}: {exc}")
            continue
    raise RuntimeError("No se pudo localizar un chunk util de Champions Lab:\n- " + "\n- ".join(errors[:5]))


def build_champions_entry_index(entries: list[dict]) -> tuple[dict[str, dict], dict[int, list[dict]], dict[str, dict]]:
    by_name = {normalize_compare_name(entry["name"]): entry for entry in entries}
    by_dex: dict[int, list[dict]] = {}
    mega_by_name: dict[str, dict] = {}
    for entry in entries:
        by_dex.setdefault(int(entry["dexNumber"]), []).append(entry)
        for form in entry.get("forms", []):
            if form.get("isMega"):
                mega_by_name[normalize_compare_name(form["name"])] = {
                    "base_entry": entry,
                    "form": form,
                }
    return by_name, by_dex, mega_by_name


def resolve_champions_entry(card: dict, by_name: dict[str, dict], by_dex: dict[int, list[dict]]) -> dict:
    target_key = normalize_compare_name(card["display_name"])
    direct = by_name.get(target_key)
    if direct:
        return direct

    dex_candidates = by_dex.get(int(card["dex_number"]), [])
    exact = next((entry for entry in dex_candidates if normalize_compare_name(entry["name"]) == target_key), None)
    if exact:
        return exact

    if len(dex_candidates) == 1:
        return dex_candidates[0]

    fallback = next(
        (
            entry
            for entry in dex_candidates
            if all(token in normalize_compare_name(entry["name"]) for token in target_key.split())
        ),
        None,
    )
    if fallback:
        return fallback

    raise RuntimeError(f"No se pudo resolver en Champions Lab: {card['display_name']} (dex {card['dex_number']})")


def build_observed_sets_by_name(setdex_entries: dict[str, list[dict]], pokemon_entries: list[dict]) -> dict[str, list[dict]]:
    names_by_chunk_id = {str(entry["id"]): entry["name"] for entry in pokemon_entries}
    observed = {}
    for chunk_id, sets in setdex_entries.items():
        name = names_by_chunk_id.get(str(chunk_id))
        if not name:
            continue
        observed[normalize_compare_name(name)] = sets
    return observed


def build_species_cache(session: requests.Session, dex_numbers: set[int]) -> dict[int, dict]:
    cache = {}
    for dex_number in sorted(dex_numbers):
        cache[dex_number] = request_json(f"{POKEAPI_BASE}/pokemon-species/{dex_number}", session)
    return cache


def upsert_ability_row(abilities: dict[str, dict], ability_name: str, description: str) -> str:
    ability_key = normalize_resource_key(ability_name)
    existing = abilities.get(ability_key, {})
    abilities[ability_key] = {
        "ability_key": ability_key,
        "name_en": ability_name,
        "name_es": existing.get("name_es") or ability_name,
        "description_en": description or existing.get("description_en", ""),
        "description_es": existing.get("description_es", ""),
        "is_signature": existing.get("is_signature") or "0",
        "source_key": "championslab",
    }
    return ability_key


def infer_move_flags(move_name: str, category_key: str) -> dict[str, str]:
    lower = move_name.lower()
    return {
        "priority": "",
        "targeting_key": "unknown",
        "makes_contact": "1" if lower in {"close combat", "fake out", "flare blitz", "u-turn", "knock off", "population bomb", "drain punch", "brave bird", "leaf blade"} else "0",
        "is_sound": "1" if lower in {"hyper voice", "clangorous soul", "clanging scales", "perish song", "boomburst", "disarming voice"} else "0",
        "is_pulse": "1" if lower in {"dragon pulse", "dark pulse", "water pulse", "aura sphere"} else "0",
        "is_punch": "1" if lower in {"thunder punch", "ice punch", "bullet punch", "drain punch", "focus punch"} else "0",
        "is_bite": "1" if lower in {"crunch", "ice fang", "fire fang", "thunder fang"} else "0",
        "is_slashing": "1" if lower in {"leaf blade", "night slash", "air slash", "psycho cut", "sacred sword"} else "0",
        "is_status": "1" if category_key == "status" else "0",
    }


def upsert_move_row(moves: dict[str, dict], move_entry: dict) -> str:
    move_key = normalize_resource_key(move_entry["name"])
    category_key = str(move_entry.get("category") or "").lower() or "unknown"
    flags = infer_move_flags(move_entry["name"], category_key)
    existing = moves.get(move_key, {})
    moves[move_key] = {
        "move_key": move_key,
        "name_en": move_entry["name"],
        "name_es": existing.get("name_es") or move_entry["name"],
        "type_key": str(move_entry.get("type") or existing.get("type_key") or "unknown").lower(),
        "category_key": category_key,
        "power": "" if move_entry.get("power") is None else str(move_entry["power"]),
        "accuracy": "" if move_entry.get("accuracy") is None else str(move_entry["accuracy"]),
        "pp": "" if move_entry.get("pp") is None else str(move_entry["pp"]),
        "priority": existing.get("priority") or flags["priority"],
        "targeting_key": existing.get("targeting_key") or flags["targeting_key"],
        "makes_contact": existing.get("makes_contact") or flags["makes_contact"],
        "is_sound": existing.get("is_sound") or flags["is_sound"],
        "is_pulse": existing.get("is_pulse") or flags["is_pulse"],
        "is_punch": existing.get("is_punch") or flags["is_punch"],
        "is_bite": existing.get("is_bite") or flags["is_bite"],
        "is_slashing": existing.get("is_slashing") or flags["is_slashing"],
        "is_status": existing.get("is_status") or flags["is_status"],
        "effect_short_en": move_entry.get("description") or existing.get("effect_short_en", ""),
        "effect_short_es": existing.get("effect_short_es", ""),
        "effect_long_en": move_entry.get("description") or existing.get("effect_long_en", ""),
        "effect_long_es": existing.get("effect_long_es", ""),
        "source_key": "championslab",
    }
    return move_key


def item_name_to_api_slug(item_name: str) -> str:
    value = item_name.strip().lower().replace("’", "'")
    value = value.replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def infer_mega_stone_name(mega_name: str) -> str:
    base_name = mega_name.replace("Mega ", "").strip()
    if base_name.endswith(" X"):
        return f"{base_name[:-2]}ite X"
    if base_name.endswith(" Y"):
        return f"{base_name[:-2]}ite Y"
    return f"{base_name}ite"


def ensure_item_row(items: dict[str, dict], item_name: str, session: requests.Session, force_mega_stone: bool = False) -> str:
    item_key = normalize_resource_key(item_name)
    if item_key in items:
        return item_key

    api_payload = try_request_json(f"{POKEAPI_BASE}/item/{item_name_to_api_slug(item_name)}", session)
    if api_payload:
        name_es = next(
            (entry["name"] for entry in api_payload.get("names", []) if entry["language"]["name"] == "es"),
            item_name,
        )
        effect_en = next(
            (entry["short_effect"] for entry in api_payload.get("effect_entries", []) if entry["language"]["name"] == "en"),
            "",
        )
        items[item_key] = {
            "item_key": item_key,
            "name_en": item_name,
            "name_es": name_es,
            "category_key": normalize_resource_key(api_payload.get("category", {}).get("name", "held_items")),
            "effect_short_en": effect_en,
            "effect_short_es": "",
            "effect_long_en": effect_en,
            "effect_long_es": "",
            "is_mega_stone": "1" if force_mega_stone else "0",
            "source_key": "pokeapi",
        }
        return item_key

    category_key = "mega_stones" if force_mega_stone or item_name.lower().endswith(("ite", "ite x", "ite y", "ite z")) else "held_items"
    effect_short_en = f"Used in current Champions set data: {item_name}."
    items[item_key] = {
        "item_key": item_key,
        "name_en": item_name,
        "name_es": item_name,
        "category_key": category_key,
        "effect_short_en": effect_short_en,
        "effect_short_es": "",
        "effect_long_en": effect_short_en,
        "effect_long_es": "",
        "is_mega_stone": "1" if category_key == "mega_stones" else "0",
        "source_key": "championslab",
    }
    return item_key


def build_current_sources() -> list[dict]:
    return [
        {
            "source_key": "pokemon_champions_official",
            "source_name": "Pokemon Champions Official",
            "source_type": "official",
            "url": "https://champions.pokemon.com/es-es/gameplay/",
            "trust_level": "high",
            "last_checked_at": TODAY,
            "license_notes": "",
            "notes": "Gameplay overview confirming Ranked Battles, Mega Evolution in the first regulation and rotating regulations.",
        },
        {
            "source_key": "championslab",
            "source_name": "Champions Lab",
            "source_type": "meta_site",
            "url": CHAMPIONS_LAB_HOME,
            "trust_level": "medium",
            "last_checked_at": TODAY,
            "license_notes": "",
            "notes": "Used for current season, visible roster tiers, current Pokedex move pools, current ability pools and observed set data.",
        },
        {
            "source_key": "bulbapedia",
            "source_name": "Bulbapedia",
            "source_type": "fan_db",
            "url": BULBAPEDIA_ROSTER_URL,
            "trust_level": "medium",
            "last_checked_at": TODAY,
            "license_notes": "CC BY-NC-SA 2.5",
            "notes": "Used for current roster availability notes and current legal Mega Evolution list.",
        },
        {
            "source_key": "pokeapi",
            "source_name": "PokeAPI",
            "source_type": "fan_db",
            "url": "https://pokeapi.co/docs",
            "trust_level": "medium",
            "last_checked_at": TODAY,
            "license_notes": "CC BY-SA 4.0",
            "notes": "Used for species flags, generation data, localized names and standard item fallbacks.",
        },
        {
            "source_key": "manual_curation",
            "source_name": "Manual Curation",
            "source_type": "manual_curation",
            "url": "",
            "trust_level": "low",
            "last_checked_at": TODAY,
            "license_notes": "",
            "notes": "Used only for fallback mega stone naming when no cleaner structured source is available.",
        },
    ]


def build_sync_summary(
    season_info: dict,
    seasons_dataset: list[dict],
    bundle_url: str,
    bulba_parse_method: str,
    roster_table: pd.DataFrame,
    mega_table: pd.DataFrame,
    pokedex_entries: list[dict],
    setdex_entries: dict[str, list[dict]],
    pokemon_rows: list[dict],
    tiers_rows: list[dict],
    mega_rows: list[dict],
    abilities_catalog: dict[str, dict],
    moves_catalog: dict[str, dict],
    items_catalog: dict[str, dict],
    pokemon_abilities_rows: list[dict],
    pokemon_moves_rows: list[dict],
    speed_rows: list[dict],
) -> dict:
    observed_set_rows = sum(1 for row in pokemon_moves_rows if row.get("availability_status") == "observed_set")
    move_pool_rows = sum(1 for row in pokemon_moves_rows if row.get("availability_status") == "champions_move_pool")
    fallback_mega_rows = sum(1 for row in mega_rows if row.get("source_key") == "manual_curation")
    items_by_source: dict[str, int] = {}
    for row in items_catalog.values():
        items_by_source[row.get("source_key", "unknown")] = items_by_source.get(row.get("source_key", "unknown"), 0) + 1
    active_season = next((season for season in seasons_dataset if season.get("isActive")), {})

    return {
        "generated_at": TODAY,
        "season_key": SEASON_KEY,
        "season_name": season_info["season_name"],
        "season_dates": {
            "start_date": parse_human_date(season_info["start_date_human"]),
            "end_date": parse_human_date(season_info["end_date_human"]),
            "regulation_until": parse_human_date(season_info["regulation_until_human"]),
        },
        "source_health": {
            "championslab_bundle_url": bundle_url,
            "championslab_home_expected_roster_count": season_info["roster_count"],
            "championslab_home_extracted_roster_count": len(pokemon_rows),
            "championslab_pokedex_entries": len(pokedex_entries),
            "championslab_setdex_groups": len(setdex_entries),
            "championslab_active_seasons_in_bundle": len(seasons_dataset),
            "championslab_active_season_match": active_season.get("name", ""),
            "bulbapedia_parse_method": bulba_parse_method,
            "bulbapedia_roster_rows": int(len(roster_table)),
            "bulbapedia_mega_rows": int(len(mega_table)),
        },
        "dataset_metrics": {
            "pokemon_rows": len(pokemon_rows),
            "tiers_rows": len(tiers_rows),
            "mega_rows": len(mega_rows),
            "abilities_catalog_rows": len(abilities_catalog),
            "moves_catalog_rows": len(moves_catalog),
            "items_catalog_rows": len(items_catalog),
            "pokemon_abilities_rows": len(pokemon_abilities_rows),
            "pokemon_moves_rows": len(pokemon_moves_rows),
            "pokemon_move_pool_rows": move_pool_rows,
            "pokemon_observed_set_rows": observed_set_rows,
            "speed_profiles_rows": len(speed_rows),
            "manual_curation_mega_rows": fallback_mega_rows,
        },
        "automation_signals": {
            "items_by_source": items_by_source,
            "has_bulbapedia_fallback_parser": bulba_parse_method != "pandas_read_html",
            "manual_curation_mega_ratio": round(fallback_mega_rows / len(mega_rows), 4) if mega_rows else 0,
            "observed_set_move_ratio": round(observed_set_rows / move_pool_rows, 4) if move_pool_rows else 0,
        },
    }


def main() -> None:
    session = requests.Session()
    roster_cards, season_info = fetch_championslab_home(session)
    roster_table, mega_table, bulba_roster_until, bulba_parse_method = fetch_bulbapedia_tables(session)
    pokedex_entries, setdex_entries, seasons_dataset, bundle_url = fetch_championslab_datasets(session)
    entry_by_name, entries_by_dex, mega_lookup = build_champions_entry_index(pokedex_entries)
    observed_sets_by_name = build_observed_sets_by_name(setdex_entries, pokedex_entries)
    availability_lookup = build_bulbapedia_availability(roster_table)
    seed_lookup = build_seed_lookup(load_csv(RAW / "pokemon.csv"))
    seed_mega_lookup = load_seed_megas()
    species_cache = build_species_cache(session, {card["dex_number"] for card in roster_cards})

    pokemon_rows = []
    stats_rows = []
    tiers_rows = []
    pokemon_abilities_rows = []
    pokemon_moves_rows = []
    speed_rows = []
    abilities_catalog: dict[str, dict] = {}
    moves_catalog: dict[str, dict] = {}
    items_catalog: dict[str, dict] = {}
    seen_pokemon_moves = set()

    mega_names_by_species: dict[int, list[str]] = {}
    for _, row in mega_table.iterrows():
        dex = int(str(row["Ndex"]).replace("#", ""))
        label = str(row["Pokémon"]).strip()
        mega_name = label[label.find("Mega ") :] if "Mega " in label else label
        mega_names_by_species.setdefault(dex, []).append(mega_name)

    for card in roster_cards:
        pokemon_id = card["pokemon_id"]
        entry = resolve_champions_entry(card, entry_by_name, entries_by_dex)
        species_data = species_cache[card["dex_number"]]

        species_name_en = next(
            (entry_name["name"] for entry_name in species_data["names"] if entry_name["language"]["name"] == "en"),
            entry["name"],
        )
        species_name_es = next(
            (entry_name["name"] for entry_name in species_data["names"] if entry_name["language"]["name"] == "es"),
            species_name_en,
        )
        form_name_en = "" if normalize_compare_name(entry["name"]) == normalize_compare_name(species_name_en) else entry["name"]
        seed_row = seed_lookup.get((card["dex_number"], species_name_en, form_name_en))
        form_name_es = (seed_row or {}).get("form_name_es") or (form_name_en if form_name_en else "")

        available_mega_names = mega_names_by_species.get(card["dex_number"], [])
        primary_mega_key = slugify(available_mega_names[0]) if available_mega_names else ""

        pokemon_rows.append(
            {
                "pokemon_id": pokemon_id,
                "dex_number": card["dex_number"],
                "species_key": species_data["name"],
                "form_key": slugify(form_name_en) if form_name_en else "",
                "name_en": species_name_en,
                "name_es": (seed_row or {}).get("name_es") or species_name_es,
                "form_name_en": form_name_en,
                "form_name_es": form_name_es,
                "type1_key": entry["types"][0],
                "type2_key": entry["types"][1] if len(entry["types"]) > 1 else "",
                "generation": GENERATION_MAP.get(species_data["generation"]["name"], ""),
                "is_legendary": 1 if species_data["is_legendary"] else 0,
                "is_mythical": 1 if species_data["is_mythical"] else 0,
                "has_mega": 1 if available_mega_names else 0,
                "mega_key": primary_mega_key,
                "is_currently_legal": 1,
                "season_key": SEASON_KEY,
                "tier_current": card["tier_value"],
                "tier_source_key": "championslab",
                "roster_source_key": "championslab",
                "format_availability": normalize_availability(card["display_name"], card["dex_number"], availability_lookup),
                "notes": "Roster legal in current Champions Lab active regulation.",
            }
        )

        base_stats = entry["baseStats"]
        stats_rows.append(
            {
                "pokemon_id": pokemon_id,
                "hp": base_stats["hp"],
                "attack": base_stats["attack"],
                "defense": base_stats["defense"],
                "sp_attack": base_stats["spAtk"],
                "sp_defense": base_stats["spDef"],
                "speed": base_stats["speed"],
                "bst": sum(base_stats.values()),
                "source_key": "championslab",
            }
        )

        tiers_rows.append(
            {
                "pokemon_id": pokemon_id,
                "season_key": SEASON_KEY,
                "format": "doubles",
                "tier_value": card["tier_value"],
                "tier_source_key": "championslab",
                "last_checked_at": TODAY,
                "notes": f"Visible current tier on Champions Lab active roster card as of {TODAY}.",
            }
        )

        for ability_index, ability in enumerate(entry.get("abilities", []), start=1):
            ability_key = upsert_ability_row(abilities_catalog, ability["name"], ability.get("description", ""))
            slot_type = "hidden" if ability.get("isHidden") else f"ability-{ability_index}"
            pokemon_abilities_rows.append(
                {
                    "pokemon_id": pokemon_id,
                    "ability_key": ability_key,
                    "slot_type": slot_type,
                    "is_currently_available": 1,
                    "source_key": "championslab",
                }
            )

        observed_sets = observed_sets_by_name.get(normalize_compare_name(entry["name"]), [])
        observed_move_keys = set()
        observed_item_names = set()
        for set_row in observed_sets:
            observed_item_names.add(set_row["item"])
            for move_name in set_row.get("moves", []):
                observed_move_keys.add(normalize_resource_key(move_name))

        for move in entry.get("moves", []):
            move_key = upsert_move_row(moves_catalog, move)
            base_row_key = (pokemon_id, move_key, "champions_roster")
            if base_row_key not in seen_pokemon_moves:
                seen_pokemon_moves.add(base_row_key)
                pokemon_moves_rows.append(
                    {
                        "pokemon_id": pokemon_id,
                        "move_key": move_key,
                        "availability_status": "champions_move_pool",
                        "learn_method": "champions_roster",
                        "learn_method_es": "champions_roster",
                        "is_confirmed_in_champions": 1,
                        "source_key": "championslab",
                        "notes": f"Listed in Champions Lab current Pokedex move pool as of {TODAY}.",
                    }
                )
            if move_key in observed_move_keys:
                observed_row_key = (pokemon_id, move_key, "observed_set")
                if observed_row_key not in seen_pokemon_moves:
                    seen_pokemon_moves.add(observed_row_key)
                    pokemon_moves_rows.append(
                        {
                            "pokemon_id": pokemon_id,
                            "move_key": move_key,
                            "availability_status": "observed_set",
                            "learn_method": "observed_set",
                            "learn_method_es": "observed_set",
                            "is_confirmed_in_champions": 1,
                            "source_key": "championslab",
                            "notes": f"Observed in Champions Lab current set data as of {TODAY}.",
                        }
                    )

        for observed_item in observed_item_names:
            ensure_item_row(items_catalog, observed_item, session)

        speed_profile = accurate_level_50_speeds(base_stats["speed"])
        speed_rows.append(
            {
                "pokemon_id": pokemon_id,
                "season_key": SEASON_KEY,
                "format": "doubles",
                "base_speed": base_stats["speed"],
                "speed_min_negative": speed_profile["speed_min_negative"],
                "speed_min_neutral": speed_profile["speed_min_neutral"],
                "speed_max_neutral": speed_profile["speed_max_neutral"],
                "speed_max_positive": speed_profile["speed_max_positive"],
                "speed_max_positive_boosted_1": speed_profile["speed_max_positive_boosted_1"],
                "speed_max_positive_boosted_2": speed_profile["speed_max_positive_boosted_2"],
                "trick_room_rating": speed_profile["trick_room_rating"],
                "notes": "Calculated at level 50 with 0 IV/EV min and 31 IV/252 EV max assumptions.",
            }
        )

    pokemon_id_by_dex = {row["dex_number"]: row["pokemon_id"] for row in pokemon_rows}
    mega_rows = []
    for _, row in mega_table.iterrows():
        dex = int(str(row["Ndex"]).replace("#", ""))
        label = str(row["Pokémon"]).strip()
        mega_name = label[label.find("Mega ") :] if "Mega " in label else label
        mega_key = slugify(mega_name)
        seed = seed_mega_lookup.get(mega_key, {})
        mega_entry = mega_lookup.get(normalize_compare_name(mega_name), {})
        form = mega_entry.get("form", {})

        inferred_stone_name = seed.get("mega_stone_name_en") or infer_mega_stone_name(mega_name)
        mega_stone_name_en = seed.get("mega_stone_name_en") or inferred_stone_name
        mega_stone_name_es = seed.get("mega_stone_name_es") or mega_stone_name_en
        mega_stone_key = ensure_item_row(items_catalog, mega_stone_name_en, session, force_mega_stone=True)

        ability_key = ""
        if form.get("abilities"):
            ability_key = upsert_ability_row(
                abilities_catalog,
                form["abilities"][0]["name"],
                form["abilities"][0].get("description", ""),
            )

        stats = form.get("baseStats", {})
        mega_rows.append(
            {
                "mega_key": mega_key,
                "pokemon_id": pokemon_id_by_dex.get(dex, ""),
                "mega_name_en": mega_name,
                "mega_name_es": seed.get("mega_name_es") or mega_name,
                "mega_stone_key": mega_stone_key,
                "mega_stone_name_en": mega_stone_name_en,
                "mega_stone_name_es": mega_stone_name_es,
                "type1_key": form.get("types", [str(row["Type"]).strip().lower()])[0],
                "type2_key": form.get("types", ["", ""])[1] if len(form.get("types", [])) > 1 else "",
                "ability_key": ability_key,
                "hp": stats.get("hp", ""),
                "attack": stats.get("attack", ""),
                "defense": stats.get("defense", ""),
                "sp_attack": stats.get("spAtk", ""),
                "sp_defense": stats.get("spDef", ""),
                "speed": stats.get("speed", ""),
                "bst": sum(stats.values()) if stats else "",
                "is_currently_available": 1,
                "source_key": "championslab" if form else "manual_curation",
            }
        )

    season_rule_data = parse_season_rules(seasons_dataset)
    seasons_rows = [
        {
            "season_key": SEASON_KEY,
            "season_name": season_info["season_name"],
            "start_date": parse_human_date(season_info["start_date_human"]),
            "end_date": parse_human_date(season_info["end_date_human"]),
            "battle_format": "Doubles",
            "bring_pick_rule": season_rule_data["bring_pick_rule"],
            "level_rule": season_rule_data["level_rule"],
            "mega_allowed": season_rule_data["mega_allowed"],
            "duplicate_pokemon_allowed": season_rule_data["duplicate_pokemon_allowed"],
            "duplicate_items_allowed": season_rule_data["duplicate_items_allowed"],
            "timer_minutes": season_rule_data["timer_minutes"],
            "notes": f"Champions Lab rules: {season_rule_data['rules_source_text']}. Regulation until {season_info['regulation_until_human']}. Bulbapedia current roster text states current roster until {bulba_roster_until}.",
            "source_key": "championslab",
        }
    ]

    empty_relation_headers = {
        "pokemon_roles.csv": ["pokemon_id", "role_key", "confidence", "season_key", "format", "curation_source_key", "notes"],
        "pokemon_archetypes.csv": ["pokemon_id", "archetype_key", "fit_score", "season_key", "format", "notes"],
        "matchups.csv": ["matchup_id", "season_key", "format", "threat_pokemon_id", "answer_pokemon_id", "answer_type", "confidence", "notes"],
    }

    write_csv(RAW / "sources.csv", list(build_current_sources()[0].keys()), build_current_sources())
    write_csv(RAW / "seasons_rules.csv", list(seasons_rows[0].keys()), seasons_rows)
    write_csv(RAW / "pokemon.csv", list(pokemon_rows[0].keys()), sorted(pokemon_rows, key=lambda row: int(row["pokemon_id"])))
    write_csv(RAW / "stats_base.csv", list(stats_rows[0].keys()), sorted(stats_rows, key=lambda row: int(row["pokemon_id"])))
    write_csv(RAW / "abilities.csv", ABILITY_FIELDNAMES, sorted(abilities_catalog.values(), key=lambda row: row["ability_key"]))
    write_csv(RAW / "tiers.csv", list(tiers_rows[0].keys()), sorted(tiers_rows, key=lambda row: int(row["pokemon_id"])))
    write_csv(RAW / "pokemon_abilities.csv", list(pokemon_abilities_rows[0].keys()), sorted(pokemon_abilities_rows, key=lambda row: (int(row["pokemon_id"]), row["slot_type"], row["ability_key"])))
    write_csv(RAW / "moves.csv", MOVE_FIELDNAMES, sorted(moves_catalog.values(), key=lambda row: row["move_key"]))
    write_csv(RAW / "pokemon_moves.csv", list(pokemon_moves_rows[0].keys()), sorted(pokemon_moves_rows, key=lambda row: (int(row["pokemon_id"]), row["move_key"], row["learn_method"])))
    write_csv(RAW / "speed_profiles.csv", list(speed_rows[0].keys()), sorted(speed_rows, key=lambda row: int(row["pokemon_id"])))
    write_csv(RAW / "roles.csv", list(ROLE_ROWS[0].keys()), ROLE_ROWS)
    write_csv(RAW / "archetypes.csv", list(ARCHETYPE_ROWS[0].keys()), ARCHETYPE_ROWS)
    write_csv(RAW / "cores.csv", ["core_id", "season_key", "format", "core_name_en", "core_name_es", "archetype_key", "pokemon_1_id", "pokemon_2_id", "pokemon_3_id", "description_en", "description_es", "confidence", "source_key", "notes"], [])
    write_csv(RAW / "mega_forms.csv", list(mega_rows[0].keys()), sorted(mega_rows, key=lambda row: (int(row["pokemon_id"]) if row["pokemon_id"] else 0, row["mega_key"])))
    write_csv(RAW / "items.csv", ITEM_FIELDNAMES, sorted(items_catalog.values(), key=lambda row: row["item_key"]))
    for filename, fieldnames in empty_relation_headers.items():
        write_csv(RAW / filename, fieldnames, [])

    sync_summary = build_sync_summary(
        season_info=season_info,
        seasons_dataset=seasons_dataset,
        bundle_url=bundle_url,
        bulba_parse_method=bulba_parse_method,
        roster_table=roster_table,
        mega_table=mega_table,
        pokedex_entries=pokedex_entries,
        setdex_entries=setdex_entries,
        pokemon_rows=pokemon_rows,
        tiers_rows=tiers_rows,
        mega_rows=mega_rows,
        abilities_catalog=abilities_catalog,
        moves_catalog=moves_catalog,
        items_catalog=items_catalog,
        pokemon_abilities_rows=pokemon_abilities_rows,
        pokemon_moves_rows=pokemon_moves_rows,
        speed_rows=speed_rows,
    )
    write_json(BUILD / "sync_summary.json", sync_summary)

    print(f"[OK] Roster actual sincronizado: {len(pokemon_rows)} Pokemon legales")
    print(f"[OK] Tiers actuales sincronizados: {len(tiers_rows)} filas")
    print(f"[OK] Stats base sincronizados: {len(stats_rows)} filas")
    print(f"[OK] Catalogo de habilidades sincronizado: {len(abilities_catalog)} habilidades")
    print(f"[OK] Relaciones de habilidades sincronizadas: {len(pokemon_abilities_rows)} filas")
    print(f"[OK] Catalogo de movimientos sincronizado: {len(moves_catalog)} movimientos")
    print(f"[OK] Relaciones de movimientos sincronizadas: {len(pokemon_moves_rows)} filas")
    print(f"[OK] Catalogo de objetos sincronizado: {len(items_catalog)} objetos")
    print(f"[OK] Megas legales sincronizadas: {len(mega_rows)} filas")
    print(f"[OK] Resumen de sincronizacion generado: {BUILD / 'sync_summary.json'}")
    print("[INFO] Tablas curadas por Pokemon reiniciadas; la capa competitiva se deriva en el siguiente paso")


if __name__ == "__main__":
    main()
