import requests
import csv
import time

def fetch_items():
    # Fetch item categories
    categories_url = "https://pokeapi.co/api/v2/item-category?limit=100"
    categories_response = requests.get(categories_url)
    if categories_response.status_code != 200:
        print(f"Error fetching categories: {categories_response.status_code}")
        return []

    categories_data = categories_response.json()
    relevant_categories = ['held-items', 'mega-stones', 'berries', 'medicine', 'standard-balls', 'special-balls', 'evolution', 'fossils', 'mail', 'battle-items']

    items = []

    for category in categories_data['results']:
        if category['name'] in relevant_categories:
            category_url = category['url']
            category_response = requests.get(category_url)
            if category_response.status_code != 200:
                continue
            category_detail = category_response.json()
            for item_data in category_detail['items']:
                item_url = item_data['url']
                item_response = requests.get(item_url)
                if item_response.status_code != 200:
                    print(f"Error fetching item {item_data['name']}: {item_response.status_code}")
                    continue

                item_detail = item_response.json()

                # Extract relevant fields
                item_key = item_detail['name'].replace('-', '_').replace(' ', '_')
                name_en = item_detail['names'][0]['name'] if item_detail['names'] else item_detail['name']
                name_es = next((name['name'] for name in item_detail['names'] if name['language']['name'] == 'es'), name_en)
                category_key = item_detail['category']['name'].replace('-', '_').replace(' ', '_')
                effect_short_en = item_detail['effect_entries'][0]['short_effect'] if item_detail['effect_entries'] else ''
                effect_short_es = next((entry['short_effect'] for entry in item_detail['effect_entries'] if entry['language']['name'] == 'es'), effect_short_en)
                effect_long_en = item_detail['effect_entries'][0]['effect'] if item_detail['effect_entries'] else ''
                effect_long_es = next((entry['effect'] for entry in item_detail['effect_entries'] if entry['language']['name'] == 'es'), effect_long_en)
                is_mega_stone = 1 if 'mega' in item_detail['name'].lower() else 0
                source_key = 'pokeapi'

                items.append({
                    'item_key': item_key,
                    'name_en': name_en,
                    'name_es': name_es,
                    'category_key': category_key,
                    'effect_short_en': effect_short_en,
                    'effect_short_es': effect_short_es,
                    'effect_long_en': effect_long_en,
                    'effect_long_es': effect_long_es,
                    'is_mega_stone': is_mega_stone,
                    'source_key': source_key
                })

                time.sleep(0.05)  # Rate limit

    return items

def write_csv(items, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['item_key', 'name_en', 'name_es', 'category_key', 'effect_short_en', 'effect_short_es', 'effect_long_en', 'effect_long_es', 'is_mega_stone', 'source_key']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)

if __name__ == "__main__":
    items = fetch_items()
    write_csv(items, 'data_raw/items.csv')
    print(f"Fetched {len(items)} items.")