import requests
import csv
import time

def load_pokemon_mapping():
    mapping = {}
    with open('data_raw/pokemon.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, start=1):
            species_key = row['species_key']
            form_key = row['form_key']
            # Assign pokemon_id as sequential
            pokemon_id = i
            key = f"{species_key}_{form_key}" if form_key else species_key
            mapping[key] = pokemon_id
    return mapping

def fetch_mega_forms(pokemon_mapping):
    mega_forms = []
    # List of known mega Pokémon
    mega_pokemon = [
        'venusaur', 'charizard', 'blastoise', 'beedrill', 'pidgeot', 'alakazam', 'slowbro', 'gengar',
        'kangaskhan', 'pinsir', 'gyarados', 'aerodactyl', 'mewtwo', 'ampharos', 'scizor', 'heracross',
        'houndoom', 'tyranitar', 'sceptile', 'blaziken', 'swampert', 'gardevoir', 'sableye', 'mawile',
        'aggron', 'medicham', 'manectric', 'sharpedo', 'camerupt', 'altaria', 'banette', 'absol',
        'glalie', 'salamence', 'metagross', 'latias', 'latios', 'lopunny', 'garchomp', 'lucario',
        'abomasnow', 'gallade', 'audino', 'diancie'
    ]

    for poke_name in mega_pokemon:
        url = f"https://pokeapi.co/api/v2/pokemon-species/{poke_name}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching {poke_name}: {response.status_code}")
            continue

        data = response.json()
        for variety in data.get('varieties', []):
            variety_name = variety['pokemon']['name']
            if 'mega' in variety_name:
                # Fetch the variety data
                variety_url = variety['pokemon']['url']
                variety_response = requests.get(variety_url)
                if variety_response.status_code != 200:
                    continue
                variety_data = variety_response.json()

                # Get stats, types, etc.
                stats = {stat['stat']['name']: stat['base_stat'] for stat in variety_data['stats']}
                types = [t['type']['name'] for t in variety_data['types']]
                abilities = [a['ability']['name'] for a in variety_data['abilities'] if a['is_hidden'] == False]

                mega_key = variety_name.replace('-', '_')
                pokemon_key = poke_name
                pokemon_id = pokemon_mapping.get(pokemon_key)
                if not pokemon_id:
                    continue

                mega_name_en = variety_data.get('names', [{}])[0].get('name', variety_name.replace('-', ' ').title())
                mega_name_es = next((name['name'] for name in variety_data.get('names', []) if name['language']['name'] == 'es'), mega_name_en)

                # Mega stone: infer from name
                mega_stone_key = f"{poke_name}_mega_stone" if 'mega' in variety_name else ''
                mega_stone_name_en = mega_stone_key.replace('_', ' ').title()
                mega_stone_name_es = mega_stone_name_en  # Placeholder

                type1_key = types[0] if types else ''
                type2_key = types[1] if len(types) > 1 else ''
                ability_key = abilities[0] if abilities else ''
                hp = stats.get('hp', 0)
                attack = stats.get('attack', 0)
                defense = stats.get('defense', 0)
                sp_attack = stats.get('special-attack', 0)
                sp_defense = stats.get('special-defense', 0)
                speed = stats.get('speed', 0)
                bst = hp + attack + defense + sp_attack + sp_defense + speed
                is_currently_available = 1
                source_key = 'pokeapi'

                mega_forms.append({
                    'mega_key': mega_key,
                    'pokemon_id': pokemon_id,
                    'mega_name_en': mega_name_en,
                    'mega_name_es': mega_name_es,
                    'mega_stone_key': mega_stone_key,
                    'mega_stone_name_en': mega_stone_name_en,
                    'mega_stone_name_es': mega_stone_name_es,
                    'type1_key': type1_key,
                    'type2_key': type2_key,
                    'ability_key': ability_key,
                    'hp': hp,
                    'attack': attack,
                    'defense': defense,
                    'sp_attack': sp_attack,
                    'sp_defense': sp_defense,
                    'speed': speed,
                    'bst': bst,
                    'is_currently_available': is_currently_available,
                    'source_key': source_key
                })

        time.sleep(0.1)

    return mega_forms

def write_csv(mega_forms, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['mega_key', 'pokemon_id', 'mega_name_en', 'mega_name_es', 'mega_stone_key', 'mega_stone_name_en', 'mega_stone_name_es', 'type1_key', 'type2_key', 'ability_key', 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'bst', 'is_currently_available', 'source_key']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for form in mega_forms:
            writer.writerow(form)

if __name__ == "__main__":
    pokemon_mapping = load_pokemon_mapping()
    mega_forms = fetch_mega_forms(pokemon_mapping)
    write_csv(mega_forms, 'data_raw/mega_forms.csv')
    print(f"Fetched {len(mega_forms)} mega forms.")