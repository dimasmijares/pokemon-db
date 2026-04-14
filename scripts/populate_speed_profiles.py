import csv

def populate_speed_profiles():
    profiles = []
    with open('data_raw/stats_base.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pokemon_id = int(row['pokemon_id'])
            base_speed = int(row['speed'])
            speed_min_negative = int(base_speed * 0.75)
            speed_min_neutral = base_speed
            speed_max_neutral = base_speed
            speed_max_positive = int(base_speed * 1.25)
            speed_max_positive_boosted_1 = int(speed_max_positive * 1.5)
            speed_max_positive_boosted_2 = speed_max_positive * 2
            trick_room_rating = 'Slow' if base_speed < 50 else 'Medium' if base_speed < 100 else 'Fast'
            season_key = 'current'
            notes = ''

            profiles.append({
                'pokemon_id': pokemon_id,
                'season_key': season_key,
                'base_speed': base_speed,
                'speed_min_negative': speed_min_negative,
                'speed_min_neutral': speed_min_neutral,
                'speed_max_neutral': speed_max_neutral,
                'speed_max_positive': speed_max_positive,
                'speed_max_positive_boosted_1': speed_max_positive_boosted_1,
                'speed_max_positive_boosted_2': speed_max_positive_boosted_2,
                'trick_room_rating': trick_room_rating,
                'notes': notes
            })

    with open('data_raw/speed_profiles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['pokemon_id', 'season_key', 'base_speed', 'speed_min_negative', 'speed_min_neutral', 'speed_max_neutral', 'speed_max_positive', 'speed_max_positive_boosted_1', 'speed_max_positive_boosted_2', 'trick_room_rating', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)

if __name__ == "__main__":
    populate_speed_profiles()
    print("Speed profiles populated.")