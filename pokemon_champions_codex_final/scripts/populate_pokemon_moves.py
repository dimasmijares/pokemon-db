import csv

# Sample pokemon_moves data for some Pokémon
pokemon_moves_data = [
    # (pokemon_id, move_key, availability_status, learn_method, learn_method_es, is_confirmed_in_champions, source_key, notes)
    (1, "vine-whip", "available", "level-up", "subida de nivel", 1, "bulbapedia", ""),
    (1, "razor-leaf", "available", "level-up", "subida de nivel", 1, "bulbapedia", ""),
    (2, "ember", "available", "level-up", "subida de nivel", 1, "bulbapedia", ""),
    (2, "flamethrower", "available", "level-up", "subida de nivel", 1, "bulbapedia", ""),
    (3, "water-gun", "available", "level-up", "subida de nivel", 1, "bulbapedia", ""),
    (3, "hydro-pump", "available", "level-up", "subida de nivel", 1, "bulbapedia", ""),
    # Add more as needed
]

# Write to CSV
with open('data_raw/pokemon_moves.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['pokemon_id', 'move_key', 'availability_status', 'learn_method', 'learn_method_es', 'is_confirmed_in_champions', 'source_key', 'notes'])
    writer.writerows(pokemon_moves_data)

print(f"Generated pokemon_moves.csv with {len(pokemon_moves_data)} entries.")