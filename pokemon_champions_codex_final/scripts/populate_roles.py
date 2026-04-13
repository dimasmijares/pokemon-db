import csv

def populate_roles():
    roles = [
        {
            'role_key': 'sweeper',
            'name_en': 'Sweeper',
            'name_es': 'Barrendero',
            'description_en': 'High damage dealer that can sweep through teams.',
            'description_es': 'Inflige alto daño y puede barrer equipos.'
        },
        {
            'role_key': 'tank',
            'name_en': 'Tank',
            'name_es': 'Tanque',
            'description_en': 'High defense, absorbs damage and supports team.',
            'description_es': 'Alta defensa, absorbe daño y apoya al equipo.'
        },
        {
            'role_key': 'support',
            'name_en': 'Support',
            'name_es': 'Apoyo',
            'description_en': 'Provides utility like healing, buffs, or debuffs.',
            'description_es': 'Proporciona utilidad como curación, buffs o debuffs.'
        },
        {
            'role_key': 'wall',
            'name_en': 'Wall',
            'name_es': 'Muro',
            'description_en': 'Special or physical wall that takes hits.',
            'description_es': 'Muro especial o físico que recibe golpes.'
        },
        {
            'role_key': 'revenge_killer',
            'name_en': 'Revenge Killer',
            'name_es': 'Asesino de Venganza',
            'description_en': 'Fast Pokémon that can KO weakened opponents.',
            'description_es': 'Pokémon rápido que puede KO a oponentes debilitados.'
        }
    ]

    with open('data_raw/roles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['role_key', 'name_en', 'name_es', 'description_en', 'description_es']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for role in roles:
            writer.writerow(role)

if __name__ == "__main__":
    populate_roles()
    print("Roles populated.")