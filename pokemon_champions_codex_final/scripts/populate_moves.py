import requests
import csv
import json

# PokéAPI base URL
BASE_URL = "https://pokeapi.co/api/v2"

# Type mappings
TYPE_MAP = {
    1: "normal", 2: "fighting", 3: "flying", 4: "poison", 5: "ground",
    6: "rock", 7: "bug", 8: "ghost", 9: "steel", 10: "fire", 11: "water",
    12: "grass", 13: "electric", 14: "psychic", 15: "ice", 16: "dragon",
    17: "dark", 18: "fairy", 10001: "unknown", 10002: "shadow"
}

# Damage class mappings
DAMAGE_CLASS_MAP = {
    1: "status",
    2: "physical", 
    3: "special"
}

# Target mappings
TARGET_MAP = {
    1: "specific-move", 2: "selected-pokemon-me-first", 3: "ally",
    4: "users-field", 5: "user-or-ally", 6: "opponents-field",
    7: "user", 8: "random-opponent", 9: "all-other-pokemon",
    10: "selected-pokemon", 11: "all-opponents", 12: "entire-field",
    13: "user-and-allies", 14: "all-pokemon", 15: "all-allies"
}

def get_move_data(move_id):
    """Fetch move data from PokéAPI"""
    try:
        response = requests.get(f"{BASE_URL}/move/{move_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_move_names(move_data):
    """Extract English and Spanish names"""
    names = move_data.get('names', [])
    name_en = ""
    name_es = ""
    for name_entry in names:
        if name_entry['language']['name'] == 'en':
            name_en = name_entry['name']
        elif name_entry['language']['name'] == 'es':
            name_es = name_entry['name']
    return name_en, name_es

def get_move_effect(move_data):
    """Extract effect descriptions"""
    effect_entries = move_data.get('effect_entries', [])
    effect_short_en = ""
    effect_long_en = ""
    effect_short_es = ""
    effect_long_es = ""
    
    for effect in effect_entries:
        if effect['language']['name'] == 'en':
            effect_short_en = effect.get('short_effect', '')
            effect_long_en = effect.get('effect', '')
        elif effect['language']['name'] == 'es':
            effect_short_es = effect.get('short_effect', '')
            effect_long_es = effect.get('effect', '')
    
    return effect_short_en, effect_long_en, effect_short_es, effect_long_es

def get_move_flags(move_data):
    """Extract move flags"""
    flags = move_data.get('flags', [])
    flag_names = [flag['name'] for flag in flags]
    
    return {
        'makes_contact': 1 if 'contact' in flag_names else 0,
        'is_sound': 1 if 'sound' in flag_names else 0,
        'is_pulse': 1 if 'pulse' in flag_names else 0,
        'is_punch': 1 if 'punch' in flag_names else 0,
        'is_bite': 1 if 'bite' in flag_names else 0,
        'is_slashing': 1 if 'slash' in flag_names else 0,
        'is_status': 1 if move_data.get('damage_class', {}).get('name') == 'status' else 0
    }

def main():
    moves = []
    
    # Get total count first
    response = requests.get(f"{BASE_URL}/move?limit=1")
    if response.status_code != 200:
        print("Failed to get move count")
        return
    
    total_moves = response.json()['count']
    print(f"Fetching {total_moves} moves...")
    
    for move_id in range(1, total_moves + 1):
        move_data = get_move_data(move_id)
        if not move_data:
            continue
            
        # Skip shadow moves for now (they have different IDs)
        if move_data['id'] >= 10000:
            continue
            
        name_en, name_es = get_move_names(move_data)
        effect_short_en, effect_long_en, effect_short_es, effect_long_es = get_move_effect(move_data)
        flags = get_move_flags(move_data)
        
        move = {
            'move_key': move_data['name'].replace('-', '_'),
            'name_en': name_en,
            'name_es': name_es,
            'type_key': TYPE_MAP.get(move_data['type']['url'].split('/')[-2], 'unknown'),
            'category_key': DAMAGE_CLASS_MAP.get(move_data['damage_class']['url'].split('/')[-2], 'unknown'),
            'power': move_data.get('power') or '',
            'accuracy': move_data.get('accuracy') or '',
            'pp': move_data.get('pp') or '',
            'priority': move_data.get('priority') or 0,
            'targeting_key': TARGET_MAP.get(move_data['target']['url'].split('/')[-2], 'unknown'),
            'makes_contact': flags['makes_contact'],
            'is_sound': flags['is_sound'],
            'is_pulse': flags['is_pulse'],
            'is_punch': flags['is_punch'],
            'is_bite': flags['is_bite'],
            'is_slashing': flags['is_slashing'],
            'is_status': flags['is_status'],
            'effect_short_en': effect_short_en,
            'effect_short_es': effect_short_es,
            'effect_long_en': effect_long_en,
            'effect_long_es': effect_long_es,
            'source_key': 'pokeapi'
        }
        
        moves.append(move)
        
        if len(moves) % 100 == 0:
            print(f"Processed {len(moves)} moves...")
    
    # Write to CSV
    fieldnames = [
        'move_key', 'name_en', 'name_es', 'type_key', 'category_key', 'power', 
        'accuracy', 'pp', 'priority', 'targeting_key', 'makes_contact', 'is_sound', 
        'is_pulse', 'is_punch', 'is_bite', 'is_slashing', 'is_status', 
        'effect_short_en', 'effect_short_es', 'effect_long_en', 'effect_long_es', 'source_key'
    ]
    
    with open('data_raw/moves.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(moves)
    
    print(f"Generated moves.csv with {len(moves)} moves.")

if __name__ == "__main__":
    main()