import csv

# Sample pokemon_abilities data for some Pokémon
pokemon_abilities_data = [
    # (pokemon_id, ability_key, slot_type, is_currently_available, source_key)
    (1, "overgrow", "ability-1", 1, "bulbapedia"),
    (1, "chlorophyll", "ability-2", 1, "bulbapedia"),
    (2, "blaze", "ability-1", 1, "bulbapedia"),
    (2, "solar-power", "ability-2", 1, "bulbapedia"),
    (3, "torrent", "ability-1", 1, "bulbapedia"),
    (3, "rain-dish", "ability-2", 1, "bulbapedia"),
    # Add more as needed
]

# Write to CSV
with open('data_raw/pokemon_abilities.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['pokemon_id', 'ability_key', 'slot_type', 'is_currently_available', 'source_key'])
    writer.writerows(pokemon_abilities_data)

print(f"Generated pokemon_abilities.csv with {len(pokemon_abilities_data)} entries.")