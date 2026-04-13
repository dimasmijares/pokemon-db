import csv

def populate_archetypes():
    archetypes = [
        {
            'archetype_key': 'offensive',
            'name_en': 'Offensive',
            'name_es': 'Ofensivo',
            'description_en': 'Focuses on dealing damage and breaking through defenses.',
            'description_es': 'Se enfoca en infligir daño y romper defensas.'
        },
        {
            'archetype_key': 'defensive',
            'name_en': 'Defensive',
            'name_es': 'Defensivo',
            'description_en': 'Focuses on surviving and countering threats.',
            'description_es': 'Se enfoca en sobrevivir y contrarrestar amenazas.'
        },
        {
            'archetype_key': 'control',
            'name_en': 'Control',
            'name_es': 'Control',
            'description_en': 'Uses status moves and abilities to control the battle.',
            'description_es': 'Usa movimientos de estado y habilidades para controlar la batalla.'
        },
        {
            'archetype_key': 'speedster',
            'name_en': 'Speedster',
            'name_es': 'Velocista',
            'description_en': 'Relies on speed to outpace and strike first.',
            'description_es': 'Depende de la velocidad para superar y golpear primero.'
        },
        {
            'archetype_key': 'bulky_attacker',
            'name_en': 'Bulky Attacker',
            'name_es': 'Atacante Robusto',
            'description_en': 'Combines bulk with offensive power.',
            'description_es': 'Combina robustez con poder ofensivo.'
        }
    ]

    with open('data_raw/archetypes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['archetype_key', 'name_en', 'name_es', 'description_en', 'description_es']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for arch in archetypes:
            writer.writerow(arch)

if __name__ == "__main__":
    populate_archetypes()
    print("Archetypes populated.")