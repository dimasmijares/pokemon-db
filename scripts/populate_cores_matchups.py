import csv

def populate_cores():
    cores = [
        {
            'core_id': 1,
            'season_key': 'current',
            'core_name_en': 'Offensive Fire Core',
            'core_name_es': 'Núcleo Ofensivo de Fuego',
            'archetype_key': 'offensive',
            'pokemon_1_id': 3,  # Venusaur
            'pokemon_2_id': 6,  # Charizard
            'pokemon_3_id': 9,  # Blastoise
            'description_en': 'Balanced offensive team with fire type.',
            'description_es': 'Equipo ofensivo equilibrado con tipo fuego.',
            'confidence': 'high',
            'source_key': 'smogon',
            'notes': 'Example core'
        },
        {
            'core_id': 2,
            'season_key': 'current',
            'core_name_en': 'Defensive Water Core',
            'core_name_es': 'Núcleo Defensivo de Agua',
            'archetype_key': 'defensive',
            'pokemon_1_id': 9,
            'pokemon_2_id': 130,  # Gyarados
            'pokemon_3_id': 131,  # Lapras
            'description_en': 'Tanky water types for defense.',
            'description_es': 'Tipos agua robustos para defensa.',
            'confidence': 'medium',
            'source_key': 'smogon',
            'notes': 'Example core'
        }
    ]

    with open('data_raw/cores.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['core_id', 'season_key', 'core_name_en', 'core_name_es', 'archetype_key', 'pokemon_1_id', 'pokemon_2_id', 'pokemon_3_id', 'description_en', 'description_es', 'confidence', 'source_key', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for core in cores:
            writer.writerow(core)

def populate_matchups():
    matchups = [
        {
            'matchup_id': 1,
            'season_key': 'current',
            'threat_pokemon_id': 6,  # Charizard
            'answer_pokemon_id': 9,  # Blastoise
            'answer_type': 'counter',
            'confidence': 'high',
            'notes': 'Water beats Fire'
        },
        {
            'matchup_id': 2,
            'season_key': 'current',
            'threat_pokemon_id': 3,  # Venusaur
            'answer_pokemon_id': 6,  # Charizard
            'answer_type': 'counter',
            'confidence': 'high',
            'notes': 'Fire beats Grass'
        }
    ]

    with open('data_raw/matchups.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['matchup_id', 'season_key', 'threat_pokemon_id', 'answer_pokemon_id', 'answer_type', 'confidence', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for matchup in matchups:
            writer.writerow(matchup)

if __name__ == "__main__":
    populate_cores()
    populate_matchups()
    print("Cores and matchups populated.")