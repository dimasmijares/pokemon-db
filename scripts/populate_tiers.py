import csv

def populate_tiers():
    tiers = [
        {
            'pokemon_id': 1,
            'season_key': 'champions_v1',
            'tier_value': 'S',
            'tier_source_key': 'smogon',
            'last_checked_at': '2026-04-09',
            'notes': 'Top tier'
        },
        {
            'pokemon_id': 3,
            'season_key': 'champions_v1',
            'tier_value': 'A',
            'tier_source_key': 'smogon',
            'last_checked_at': '2026-04-09',
            'notes': 'High tier'
        },
        {
            'pokemon_id': 6,
            'season_key': 'champions_v1',
            'tier_value': 'S',
            'tier_source_key': 'smogon',
            'last_checked_at': '2026-04-09',
            'notes': 'Top tier'
        }
    ]

    with open('data_raw/tiers.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['pokemon_id', 'season_key', 'tier_value', 'tier_source_key', 'last_checked_at', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tier in tiers:
            writer.writerow(tier)

if __name__ == "__main__":
    populate_tiers()
    print("Tiers populated.")