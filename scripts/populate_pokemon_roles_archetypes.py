import csv

def load_pokemon():
    pokemon = {}
    with open('data_raw/pokemon.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, start=1):
            pokemon_id = i
            type1 = row['type1_key']
            type2 = row['type2_key']
            pokemon[pokemon_id] = {'type1': type1, 'type2': type2}
    return pokemon

def assign_roles_archetypes(pokemon):
    roles = []
    archetypes = []
    role_map = {
        'fire': 'sweeper',
        'water': 'tank',
        'grass': 'support',
        'electric': 'revenge_killer',
        'psychic': 'wall',
        'ice': 'wall',
        'dragon': 'sweeper',
        'dark': 'revenge_killer',
        'fairy': 'support'
    }
    arch_map = {
        'fire': 'offensive',
        'water': 'defensive',
        'grass': 'control',
        'electric': 'speedster',
        'psychic': 'control',
        'ice': 'defensive',
        'dragon': 'offensive',
        'dark': 'offensive',
        'fairy': 'control'
    }

    for pokemon_id, types in pokemon.items():
        type1 = types['type1']
        role_key = role_map.get(type1, 'tank')
        arch_key = arch_map.get(type1, 'defensive')
        confidence = 'medium'
        season_key = 'current'
        curation_source_key = 'bulbapedia'
        notes = 'Auto-assigned based on type'

        roles.append({
            'pokemon_id': pokemon_id,
            'role_key': role_key,
            'confidence': confidence,
            'season_key': season_key,
            'curation_source_key': curation_source_key,
            'notes': notes
        })

        archetypes.append({
            'pokemon_id': pokemon_id,
            'archetype_key': arch_key,
            'fit_score': 70,
            'season_key': season_key,
            'notes': notes
        })

    with open('data_raw/pokemon_roles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['pokemon_id', 'role_key', 'confidence', 'season_key', 'curation_source_key', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for role in roles:
            writer.writerow(role)

    with open('data_raw/pokemon_archetypes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['pokemon_id', 'archetype_key', 'fit_score', 'season_key', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for arch in archetypes:
            writer.writerow(arch)

if __name__ == "__main__":
    pokemon = load_pokemon()
    assign_roles_archetypes(pokemon)
    print("Pokemon roles and archetypes populated.")