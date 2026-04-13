from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv
import re

import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data_raw"
TODAY = "2026-04-13"
SEASON_KEY = "season_m1_reg_ma"
META_URL = "https://championslab.xyz/meta"

ROLE_ROWS = [
    {"role_key": "speed_control", "name_en": "Speed Control", "name_es": "Control de Velocidad", "description_en": "Provides proactive or reverse speed control.", "description_es": "Aporta control de velocidad directo o inverso."},
    {"role_key": "pivot", "name_en": "Pivot", "name_es": "Pivot", "description_en": "Creates positioning or tempo through switching and utility.", "description_es": "Genera posicin o tempo mediante cambios y utilidad."},
    {"role_key": "wallbreaker", "name_en": "Wallbreaker", "name_es": "Muroperforador", "description_en": "Breaks through bulky cores using strong offensive pressure.", "description_es": "Rompe ncleos defensivos con presin ofensiva alta."},
    {"role_key": "bulky_support", "name_en": "Bulky Support", "name_es": "Soporte Resistente", "description_en": "Supports allies while maintaining defensive presence.", "description_es": "Apoya al equipo manteniendo presencia defensiva."},
    {"role_key": "weather_setter", "name_en": "Weather Setter", "name_es": "Setter de Clima", "description_en": "Sets weather that defines the game plan.", "description_es": "Activa el clima que define el plan de partida."},
    {"role_key": "trick_room_setter", "name_en": "Trick Room Setter", "name_es": "Setter de Espacio Raro", "description_en": "Can reliably set Trick Room.", "description_es": "Puede activar Espacio Raro de forma fiable."},
]

ARCHETYPE_ROWS = [
    {"archetype_key": "sun", "name_en": "Sun", "name_es": "Sol", "description_en": "Structures built around sun.", "description_es": "Estructuras basadas en sol."},
    {"archetype_key": "rain", "name_en": "Rain", "name_es": "Lluvia", "description_en": "Structures built around rain.", "description_es": "Estructuras basadas en lluvia."},
    {"archetype_key": "sand", "name_en": "Sand", "name_es": "Arena", "description_en": "Structures built around sand.", "description_es": "Estructuras basadas en arena."},
    {"archetype_key": "trick_room", "name_en": "Trick Room", "name_es": "Espacio Raro", "description_en": "Structures built around reverse speed control.", "description_es": "Estructuras basadas en control inverso de velocidad."},
    {"archetype_key": "tailwind", "name_en": "Tailwind", "name_es": "Viento Afn", "description_en": "Structures built around Tailwind speed control.", "description_es": "Estructuras basadas en Viento Afn."},
    {"archetype_key": "hyper_offense", "name_en": "Hyper Offense", "name_es": "Hiperofensiva", "description_en": "High-pressure offensive structures.", "description_es": "Estructuras ofensivas de alta presin."},
    {"archetype_key": "balance", "name_en": "Balance", "name_es": "Balance", "description_en": "Flexible structures with both defensive and offensive pieces.", "description_es": "Estructuras flexibles con piezas ofensivas y defensivas."},
    {"archetype_key": "commander", "name_en": "Commander", "name_es": "Commander", "description_en": "Structures built around Dondozo + Tatsugiri style commander interactions.", "description_es": "Estructuras basadas en sinergias tipo Commander."},
    {"archetype_key": "offense", "name_en": "Offense", "name_es": "Ofensiva", "description_en": "Proactive offensive structures.", "description_es": "Estructuras ofensivas proactivas."},
]

TYPE_CHART = {
    "normal": {"weak_to": {"fighting"}, "resists": set(), "immune_to": {"ghost"}},
    "fire": {"weak_to": {"water", "ground", "rock"}, "resists": {"fire", "grass", "ice", "bug", "steel", "fairy"}, "immune_to": set()},
    "water": {"weak_to": {"electric", "grass"}, "resists": {"fire", "water", "ice", "steel"}, "immune_to": set()},
    "electric": {"weak_to": {"ground"}, "resists": {"electric", "flying", "steel"}, "immune_to": set()},
    "grass": {"weak_to": {"fire", "ice", "poison", "flying", "bug"}, "resists": {"water", "electric", "grass", "ground"}, "immune_to": set()},
    "ice": {"weak_to": {"fire", "fighting", "rock", "steel"}, "resists": {"ice"}, "immune_to": set()},
    "fighting": {"weak_to": {"flying", "psychic", "fairy"}, "resists": {"bug", "rock", "dark"}, "immune_to": set()},
    "poison": {"weak_to": {"ground", "psychic"}, "resists": {"grass", "fighting", "poison", "bug", "fairy"}, "immune_to": set()},
    "ground": {"weak_to": {"water", "grass", "ice"}, "resists": {"poison", "rock"}, "immune_to": {"electric"}},
    "flying": {"weak_to": {"electric", "ice", "rock"}, "resists": {"grass", "fighting", "bug"}, "immune_to": {"ground"}},
    "psychic": {"weak_to": {"bug", "ghost", "dark"}, "resists": {"fighting", "psychic"}, "immune_to": set()},
    "bug": {"weak_to": {"fire", "flying", "rock"}, "resists": {"grass", "fighting", "ground"}, "immune_to": set()},
    "rock": {"weak_to": {"water", "grass", "fighting", "ground", "steel"}, "resists": {"normal", "fire", "poison", "flying"}, "immune_to": set()},
    "ghost": {"weak_to": {"ghost", "dark"}, "resists": {"poison", "bug"}, "immune_to": {"normal", "fighting"}},
    "dragon": {"weak_to": {"ice", "dragon", "fairy"}, "resists": {"fire", "water", "electric", "grass"}, "immune_to": set()},
    "dark": {"weak_to": {"fighting", "bug", "fairy"}, "resists": {"ghost", "dark"}, "immune_to": {"psychic"}},
    "steel": {"weak_to": {"fire", "fighting", "ground"}, "resists": {"normal", "grass", "ice", "flying", "psychic", "bug", "rock", "dragon", "steel", "fairy"}, "immune_to": {"poison"}},
    "fairy": {"weak_to": {"poison", "steel"}, "resists": {"fighting", "bug", "dark"}, "immune_to": {"dragon"}},
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def archetype_key_from_label(label: str) -> str:
    value = label.strip().lower()
    mapping = {
        "sand": "sand",
        "rain": "rain",
        "trick room": "trick_room",
        "sun": "sun",
        "offense": "offense",
        "hyper offense": "hyper_offense",
        "tailwind": "tailwind",
        "commander": "commander",
    }
    return mapping.get(value, "balance")


def parse_meta_sections() -> tuple[list[dict], list[dict], list[dict]]:
    html = requests.get(META_URL, timeout=60, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    core_pairs = []
    for heading in soup.find_all("h3"):
        if heading.get_text(" ", strip=True) == "Tournament Core Pairs":
            container = heading.parent.find("div", class_="space-y-2")
            if not container:
                break
            for child in container.find_all("div", recursive=False):
                imgs = child.find_all("img")
                if len(imgs) < 2:
                    continue
                sprite_ids = [
                    int(match.group(1))
                    for img in imgs[:2]
                    if (match := re.search(r"/sprites/(\d+)\.png", img.get("src", "")))
                ]
                if len(sprite_ids) < 2:
                    continue
                spans = child.find_all("span")
                title = next((span.get_text(" ", strip=True) for span in spans if " + " in span.get_text(" ", strip=True)), "")
                winrate = next((span.get_text(" ", strip=True).replace("%", "") for span in spans if "%" in span.get_text(" ", strip=True) or span.get("class") and "text-green-600" in " ".join(span.get("class", []))), "")
                paragraph = child.find("p")
                usage_match = re.search(r"([0-9.]+)", paragraph.get_text(" ", strip=True) if paragraph else "")
                desc = ""
                if paragraph:
                    ptxt = paragraph.get_text(" ", strip=True)
                    desc = re.sub(r"^[0-9.]+.*?usage\s*[·]?\s*", "", ptxt).strip()
                core_pairs.append(
                    {
                        "pokemon_1_id": sprite_ids[0],
                        "pokemon_2_id": sprite_ids[1],
                        "title": title,
                        "winrate": winrate,
                        "usage": usage_match.group(1) if usage_match else "",
                        "description": desc,
                    }
                )
            break

    team_pattern = re.compile(
        r'<span class="px-1\.5 py-0\.5 text-\[9px\] font-bold rounded uppercase [^"]+">([SA])</span>'
        r'<span class="text-xs font-semibold truncate flex-1">([^<]+)</span>'
        r'<span class="text-\[9px\] text-muted-foreground capitalize">([^<]+)</span>'
        r'(.*?)</div></div>',
        re.S,
    )
    curated_teams = []
    team_block = html[html.find("Curated Teams") : html.find("Key Counter Matchups")]
    for grade, team_name, archetype_label, body in team_pattern.findall(team_block):
        sprite_ids = [int(value) for value in re.findall(r'/sprites/(\d+)\.png', body)]
        if len(sprite_ids) >= 2:
            curated_teams.append(
                {
                    "grade": grade,
                    "team_name": team_name.strip(),
                    "archetype_label": archetype_label.strip(),
                    "pokemon_ids": sprite_ids[:6],
                }
            )

    matchup_pattern = re.compile(
        r'<span class="text-xs font-bold text-green-600">([^<]+)</span>.*?'
        r'<span class="text-xs font-bold text-red-600">([^<]+)</span>.*?'
        r'<span class="text-xs font-bold text-green-600">([0-9]+).*?</span>',
        re.S,
    )
    key_matchups = []
    matchup_block = html[html.find("Key Counter Matchups") : html.find("Highest Win-Rate Moves")]
    for winner, loser, pct in matchup_pattern.findall(matchup_block):
        key_matchups.append(
            {"winner": winner.strip(), "loser": loser.strip(), "pct": pct.strip()}
        )

    return core_pairs, curated_teams, key_matchups


def get_pokemon_type_list(row: dict[str, str]) -> list[str]:
    return [value for value in [row.get("type1_key", ""), row.get("type2_key", "")] if value]


def move_lookup_by_pokemon(
    pokemon_moves: list[dict[str, str]],
    moves: dict[str, dict[str, str]],
    availability_statuses: set[str] | None = None,
) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in pokemon_moves:
        if availability_statuses and row.get("availability_status") not in availability_statuses:
            continue
        move = moves.get(row["move_key"])
        if move:
            output[row["pokemon_id"]].add(move["move_key"])
    return output


def offensive_type_lookup_by_pokemon(
    pokemon_moves: list[dict[str, str]],
    moves: dict[str, dict[str, str]],
    availability_statuses: set[str] | None = None,
) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in pokemon_moves:
        if availability_statuses and row.get("availability_status") not in availability_statuses:
            continue
        move = moves.get(row["move_key"])
        if move and move.get("type_key"):
            output[row["pokemon_id"]].add(move["type_key"])
    return output


def score_archetype_fit(existing: dict[tuple[str, str], int], pokemon_id: str, archetype_key: str, fit_score: int) -> None:
    key = (pokemon_id, archetype_key)
    existing[key] = max(existing.get(key, 0), fit_score)


def add_role(rows: dict[tuple[str, str], dict], pokemon_id: str, role_key: str, confidence: str, notes: str) -> None:
    key = (pokemon_id, role_key)
    current = rows.get(key)
    rank = {"low": 1, "medium": 2, "high": 3}
    if current is None or rank[confidence] > rank[current["confidence"]]:
        rows[key] = {
            "pokemon_id": pokemon_id,
            "role_key": role_key,
            "confidence": confidence,
            "season_key": SEASON_KEY,
            "format": "doubles",
            "curation_source_key": "manual_curation",
            "notes": notes,
        }


def effectiveness(move_type: str, defender_types: list[str]) -> float:
    multiplier = 1.0
    for defender_type in defender_types:
        data = TYPE_CHART[defender_type]
        if move_type in data["immune_to"]:
            return 0.0
        if move_type in data["weak_to"]:
            multiplier *= 2.0
        elif move_type in data["resists"]:
            multiplier *= 0.5
    return multiplier


def defensive_response_score(answer_types: list[str], threat_types: list[str]) -> tuple[int, int]:
    resist_count = 0
    immune_count = 0
    for threat_type in threat_types:
        mult = effectiveness(threat_type, answer_types)
        if mult == 0:
            immune_count += 1
        elif mult < 1:
            resist_count += 1
    return resist_count, immune_count


def derive_matchups(
    pokemon_rows: list[dict[str, str]],
    tier_rows: list[dict[str, str]],
    move_types_by_pokemon: dict[str, set[str]],
) -> list[dict]:
    pokemon_by_id = {row["pokemon_id"]: row for row in pokemon_rows}
    tier_rank = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
    top_threats = [
        row for row in tier_rows if row["tier_value"] in {"S", "A"} and row["format"] == "doubles"
    ]
    matchup_rows = []
    matchup_id = 1

    for threat_row in top_threats:
        threat = pokemon_by_id[threat_row["pokemon_id"]]
        threat_types = get_pokemon_type_list(threat)
        candidates = []
        for answer in pokemon_rows:
            if answer["pokemon_id"] == threat["pokemon_id"]:
                continue
            answer_types = get_pokemon_type_list(answer)
            resist_count, immune_count = defensive_response_score(answer_types, threat_types)
            offensive_types = move_types_by_pokemon.get(answer["pokemon_id"], set())
            offensive_pressure = max((effectiveness(move_type, threat_types) for move_type in offensive_types), default=0.0)
            if offensive_pressure < 2 and resist_count + immune_count == 0:
                continue
            score = (
                offensive_pressure * 100
                + immune_count * 30
                + resist_count * 15
                + tier_rank.get(answer.get("tier_current", ""), 0) * 5
            )
            candidates.append((score, offensive_pressure, immune_count, resist_count, answer))

        candidates.sort(reverse=True, key=lambda item: item[0])
        for _, offensive_pressure, immune_count, resist_count, answer in candidates[:3]:
            if offensive_pressure >= 2 and (immune_count > 0 or resist_count >= 1):
                answer_type = "counter"
                confidence = "medium"
            elif offensive_pressure >= 2:
                answer_type = "check"
                confidence = "low"
            else:
                answer_type = "soft_check"
                confidence = "low"
            matchup_rows.append(
                {
                    "matchup_id": matchup_id,
                    "season_key": SEASON_KEY,
                    "format": "doubles",
                    "threat_pokemon_id": threat["pokemon_id"],
                    "answer_pokemon_id": answer["pokemon_id"],
                    "answer_type": answer_type,
                    "confidence": confidence,
                    "notes": "Derived from current roster types, Champions move pool coverage and current tier snapshot.",
                }
            )
            matchup_id += 1
    return matchup_rows


def main() -> None:
    pokemon_rows = load_csv(RAW / "pokemon.csv")
    stats_rows = {row["pokemon_id"]: row for row in load_csv(RAW / "stats_base.csv")}
    abilities_rows = load_csv(RAW / "pokemon_abilities.csv")
    moves_rows = {row["move_key"]: row for row in load_csv(RAW / "moves.csv")}
    pokemon_moves_rows = load_csv(RAW / "pokemon_moves.csv")
    tiers_rows = load_csv(RAW / "tiers.csv")

    core_pairs, curated_teams, key_matchups = parse_meta_sections()
    pokemon_by_id = {row["pokemon_id"]: row for row in pokemon_rows}
    moves_by_pokemon = move_lookup_by_pokemon(pokemon_moves_rows, moves_rows)
    observed_moves_by_pokemon = move_lookup_by_pokemon(
        pokemon_moves_rows,
        moves_rows,
        {"observed_set"},
    )
    move_types_by_pokemon = offensive_type_lookup_by_pokemon(pokemon_moves_rows, moves_rows)
    ability_keys_by_pokemon: dict[str, set[str]] = defaultdict(set)
    for row in abilities_rows:
        ability_keys_by_pokemon[row["pokemon_id"]].add(row["ability_key"])

    write_csv(RAW / "roles.csv", list(ROLE_ROWS[0].keys()), ROLE_ROWS)
    write_csv(RAW / "archetypes.csv", list(ARCHETYPE_ROWS[0].keys()), ARCHETYPE_ROWS)

    cores = []
    for index, core in enumerate(core_pairs, start=1):
        desc = core["description"].lower()
        title = core["title"].lower()
        if "sun" in desc or "drought" in desc:
            archetype_key = "sun"
        elif "rain" in desc or "drizzle" in desc:
            archetype_key = "rain"
        elif "sand" in desc:
            archetype_key = "sand"
        elif "trick room" in desc or "tr " in desc:
            archetype_key = "trick_room"
        else:
            archetype_key = "balance"

        cores.append(
            {
                "core_id": index,
                "season_key": SEASON_KEY,
                "format": "doubles",
                "core_name_en": core["title"],
                "core_name_es": core["title"],
                "archetype_key": archetype_key,
                "pokemon_1_id": core["pokemon_1_id"],
                "pokemon_2_id": core["pokemon_2_id"],
                "pokemon_3_id": "",
                "description_en": f"{core['description']} ({core['usage']}% usage, {core['winrate']}% WR)",
                "description_es": core["description"],
                "confidence": "high",
                "source_key": "championslab",
                "notes": "Parsed from Champions Lab Meta core pairs.",
            }
        )

    fit_scores: dict[tuple[str, str], int] = {}
    for team in curated_teams:
        archetype_key = archetype_key_from_label(team["archetype_label"])
        base_score = 90 if team["grade"] == "S" else 75
        for pokemon_id in team["pokemon_ids"]:
            score_archetype_fit(fit_scores, str(pokemon_id), archetype_key, base_score)

    for core in core_pairs:
        desc = core["description"].lower()
        if "sun" in desc or "drought" in desc:
            archetype_key = "sun"
        elif "rain" in desc or "drizzle" in desc:
            archetype_key = "rain"
        elif "sand" in desc:
            archetype_key = "sand"
        elif "trick room" in desc or "tr " in desc:
            archetype_key = "trick_room"
        else:
            archetype_key = "balance"
        score_archetype_fit(fit_scores, str(core["pokemon_1_id"]), archetype_key, 82)
        score_archetype_fit(fit_scores, str(core["pokemon_2_id"]), archetype_key, 82)

    for pokemon in pokemon_rows:
        pokemon_id = pokemon["pokemon_id"]
        abilities = ability_keys_by_pokemon.get(pokemon_id, set())
        moves = moves_by_pokemon.get(pokemon_id, set())
        observed_moves = observed_moves_by_pokemon.get(pokemon_id, set())
        types = set(get_pokemon_type_list(pokemon))
        speed = int(stats_rows[pokemon_id]["speed"])

        if {"drought", "chlorophyll", "solar-power"} & abilities:
            score_archetype_fit(fit_scores, pokemon_id, "sun", 85 if observed_moves else 80)
        if {"drizzle", "swift-swim", "rain-dish"} & abilities:
            score_archetype_fit(fit_scores, pokemon_id, "rain", 85 if observed_moves else 80)
        if {"sand-stream", "sand-rush", "sand-force"} & abilities:
            score_archetype_fit(fit_scores, pokemon_id, "sand", 85 if observed_moves else 80)
        if "trick_room" in moves or speed <= 55:
            tr_score = 78 if "trick_room" in observed_moves else 70 if "trick_room" in moves else 55
            score_archetype_fit(fit_scores, pokemon_id, "trick_room", tr_score)
        if "tailwind" in moves:
            tailwind_score = 82 if "tailwind" in observed_moves else 75
            score_archetype_fit(fit_scores, pokemon_id, "tailwind", tailwind_score)
        if not any(key[0] == pokemon_id for key in fit_scores):
            fallback = "offense" if speed >= 95 else "balance"
            score_archetype_fit(fit_scores, pokemon_id, fallback, 50)

    pokemon_archetypes = [
        {
            "pokemon_id": pokemon_id,
            "archetype_key": archetype_key,
            "fit_score": fit_score,
            "season_key": SEASON_KEY,
            "format": "doubles",
            "notes": "Derived from Champions Lab curated teams/core pairs and current roster heuristics."
            if fit_score >= 75
            else "Derived from current roster heuristics.",
        }
        for (pokemon_id, archetype_key), fit_score in sorted(fit_scores.items())
    ]

    role_rows: dict[tuple[str, str], dict] = {}
    for pokemon in pokemon_rows:
        pokemon_id = pokemon["pokemon_id"]
        abilities = ability_keys_by_pokemon.get(pokemon_id, set())
        moves = moves_by_pokemon.get(pokemon_id, set())
        observed_moves = observed_moves_by_pokemon.get(pokemon_id, set())
        stats = stats_rows[pokemon_id]
        attack = int(stats["attack"])
        sp_attack = int(stats["sp_attack"])
        hp = int(stats["hp"])
        defense = int(stats["defense"])
        sp_defense = int(stats["sp_defense"])
        speed = int(stats["speed"])

        speed_control_observed = {"trick_room", "tailwind", "icy_wind", "electroweb", "thunder_wave"} & observed_moves
        speed_control_pool = {"trick_room", "tailwind", "icy_wind", "electroweb", "thunder_wave"} & moves
        if speed_control_pool:
            add_role(
                role_rows,
                pokemon_id,
                "speed_control",
                "high" if speed_control_observed else "medium",
                "Derived from observed Champions sets." if speed_control_observed else "Derived from current Champions move pool access.",
            )
        if "trick_room" in moves:
            add_role(
                role_rows,
                pokemon_id,
                "trick_room_setter",
                "high" if "trick_room" in observed_moves else "medium",
                "Derived from observed Champions sets." if "trick_room" in observed_moves else "Derived from current Champions move pool access.",
            )
        if {"drought", "drizzle", "sand-stream", "snow-warning"} & abilities:
            add_role(role_rows, pokemon_id, "weather_setter", "high", "Directly derived from weather-setting ability.")
        pivot_observed = {"fake_out", "parting_shot", "u_turn", "volt_switch"} & observed_moves
        if {"fake_out", "parting_shot", "u_turn", "volt_switch"} & moves or {"intimidate", "regenerator"} & abilities:
            add_role(
                role_rows,
                pokemon_id,
                "pivot",
                "high" if pivot_observed else "medium",
                "Derived from observed Champions sets." if pivot_observed else "Derived from utility move or pivot ability access.",
            )
        if attack >= 120 or sp_attack >= 120 or int(stats["bst"]) >= 560:
            add_role(role_rows, pokemon_id, "wallbreaker", "medium", "Derived from offensive stats and current roster context.")
        support_observed = {"follow_me", "rage_powder", "helping_hand", "recover", "will_o_wisp"} & observed_moves
        if hp + defense + sp_defense >= 260 or {"follow_me", "rage_powder", "helping_hand", "recover", "will_o_wisp"} & moves:
            add_role(
                role_rows,
                pokemon_id,
                "bulky_support",
                "high" if support_observed else ("low" if speed >= 100 else "medium"),
                "Derived from observed Champions sets." if support_observed else "Derived from bulk profile and support move access.",
            )

        if not any(key[0] == pokemon_id for key in role_rows):
            fallback_role = "wallbreaker" if max(attack, sp_attack) >= 100 else "bulky_support"
            add_role(role_rows, pokemon_id, fallback_role, "low", "Fallback derived role for full table coverage.")

    pokemon_roles = sorted(role_rows.values(), key=lambda row: (int(row["pokemon_id"]), row["role_key"]))
    matchup_rows = derive_matchups(pokemon_rows, tiers_rows, move_types_by_pokemon)

    write_csv(RAW / "cores.csv", list(cores[0].keys()) if cores else ["core_id", "season_key", "format", "core_name_en", "core_name_es", "archetype_key", "pokemon_1_id", "pokemon_2_id", "pokemon_3_id", "description_en", "description_es", "confidence", "source_key", "notes"], cores)
    write_csv(RAW / "pokemon_archetypes.csv", list(pokemon_archetypes[0].keys()), pokemon_archetypes)
    write_csv(RAW / "pokemon_roles.csv", list(pokemon_roles[0].keys()), pokemon_roles)
    write_csv(RAW / "matchups.csv", list(matchup_rows[0].keys()), matchup_rows)

    print(f"[OK] Core pairs cargados: {len(cores)}")
    print(f"[OK] Asignaciones de arquetipo: {len(pokemon_archetypes)}")
    print(f"[OK] Asignaciones de rol: {len(pokemon_roles)}")
    print(f"[OK] Matchups derivados: {len(matchup_rows)}")
    print(f"[INFO] Matchups de arquetipo observados en Champions Lab: {len(key_matchups)}")


if __name__ == "__main__":
    main()
