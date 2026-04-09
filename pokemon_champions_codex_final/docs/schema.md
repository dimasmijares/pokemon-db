# Esquema recomendado

## Principios
- Usar claves técnicas estables (`*_key`)
- Separar dato base, dato curado e inferencias
- Mantener castellano en paralelo a inglés cuando sea posible

## Tablas principales

### pokemon
- `pokemon_id` INTEGER PK
- `dex_number` INTEGER
- `species_key` TEXT
- `form_key` TEXT
- `name_en` TEXT
- `name_es` TEXT
- `form_name_en` TEXT
- `form_name_es` TEXT
- `type1_key` TEXT
- `type2_key` TEXT
- `generation` INTEGER
- `is_legendary` INTEGER
- `is_mythical` INTEGER
- `has_mega` INTEGER
- `mega_key` TEXT
- `is_currently_legal` INTEGER
- `season_key` TEXT
- `tier_current` TEXT
- `tier_source_key` TEXT
- `roster_source_key` TEXT
- `notes` TEXT

### stats_base
- `pokemon_id` INTEGER
- `hp` INTEGER
- `attack` INTEGER
- `defense` INTEGER
- `sp_attack` INTEGER
- `sp_defense` INTEGER
- `speed` INTEGER
- `bst` INTEGER
- `source_key` TEXT

### abilities
- `ability_key` TEXT PK
- `name_en` TEXT
- `name_es` TEXT
- `description_en` TEXT
- `description_es` TEXT
- `is_signature` INTEGER
- `source_key` TEXT

### pokemon_abilities
- `pokemon_id` INTEGER
- `ability_key` TEXT
- `slot_type` TEXT
- `is_currently_available` INTEGER
- `source_key` TEXT

### moves
- `move_key` TEXT PK
- `name_en` TEXT
- `name_es` TEXT
- `type_key` TEXT
- `category_key` TEXT
- `power` INTEGER
- `accuracy` REAL
- `pp` INTEGER
- `priority` INTEGER
- `targeting_key` TEXT
- `makes_contact` INTEGER
- `is_sound` INTEGER
- `is_pulse` INTEGER
- `is_punch` INTEGER
- `is_bite` INTEGER
- `is_slashing` INTEGER
- `is_status` INTEGER
- `effect_short_en` TEXT
- `effect_short_es` TEXT
- `effect_long_en` TEXT
- `effect_long_es` TEXT
- `source_key` TEXT

### pokemon_moves
- `pokemon_id` INTEGER
- `move_key` TEXT
- `availability_status` TEXT
- `learn_method` TEXT
- `learn_method_es` TEXT
- `is_confirmed_in_champions` INTEGER
- `source_key` TEXT
- `notes` TEXT

### mega_forms
- `mega_key` TEXT PK
- `pokemon_id` INTEGER
- `mega_name_en` TEXT
- `mega_name_es` TEXT
- `mega_stone_key` TEXT
- `mega_stone_name_en` TEXT
- `mega_stone_name_es` TEXT
- `type1_key` TEXT
- `type2_key` TEXT
- `ability_key` TEXT
- `hp` INTEGER
- `attack` INTEGER
- `defense` INTEGER
- `sp_attack` INTEGER
- `sp_defense` INTEGER
- `speed` INTEGER
- `bst` INTEGER
- `is_currently_available` INTEGER
- `source_key` TEXT

### items
- `item_key` TEXT PK
- `name_en` TEXT
- `name_es` TEXT
- `category_key` TEXT
- `effect_short_en` TEXT
- `effect_short_es` TEXT
- `effect_long_en` TEXT
- `effect_long_es` TEXT
- `is_mega_stone` INTEGER
- `source_key` TEXT

### seasons_rules
- `season_key` TEXT PK
- `season_name` TEXT
- `start_date` TEXT
- `end_date` TEXT
- `battle_format` TEXT
- `bring_pick_rule` TEXT
- `level_rule` TEXT
- `mega_allowed` INTEGER
- `duplicate_pokemon_allowed` INTEGER
- `duplicate_items_allowed` INTEGER
- `timer_minutes` INTEGER
- `notes` TEXT
- `source_key` TEXT

### tiers
- `pokemon_id` INTEGER
- `season_key` TEXT
- `tier_value` TEXT
- `tier_source_key` TEXT
- `last_checked_at` TEXT
- `notes` TEXT

### roles
- `role_key` TEXT PK
- `name_en` TEXT
- `name_es` TEXT
- `description_en` TEXT
- `description_es` TEXT

### pokemon_roles
- `pokemon_id` INTEGER
- `role_key` TEXT
- `confidence` TEXT
- `season_key` TEXT
- `curation_source_key` TEXT
- `notes` TEXT

### archetypes
- `archetype_key` TEXT PK
- `name_en` TEXT
- `name_es` TEXT
- `description_en` TEXT
- `description_es` TEXT

### pokemon_archetypes
- `pokemon_id` INTEGER
- `archetype_key` TEXT
- `fit_score` INTEGER
- `season_key` TEXT
- `notes` TEXT

### cores
- `core_id` INTEGER PK
- `season_key` TEXT
- `core_name_en` TEXT
- `core_name_es` TEXT
- `archetype_key` TEXT
- `pokemon_1_id` INTEGER
- `pokemon_2_id` INTEGER
- `pokemon_3_id` INTEGER
- `description_en` TEXT
- `description_es` TEXT
- `confidence` TEXT
- `source_key` TEXT
- `notes` TEXT

### matchups
- `matchup_id` INTEGER PK
- `season_key` TEXT
- `threat_pokemon_id` INTEGER
- `answer_pokemon_id` INTEGER
- `answer_type` TEXT
- `confidence` TEXT
- `notes` TEXT

### speed_profiles
- `pokemon_id` INTEGER
- `season_key` TEXT
- `base_speed` INTEGER
- `speed_min_negative` INTEGER
- `speed_min_neutral` INTEGER
- `speed_max_neutral` INTEGER
- `speed_max_positive` INTEGER
- `speed_max_positive_boosted_1` INTEGER
- `speed_max_positive_boosted_2` INTEGER
- `trick_room_rating` TEXT
- `notes` TEXT

### sources
- `source_key` TEXT PK
- `source_name` TEXT
- `source_type` TEXT
- `url` TEXT
- `trust_level` TEXT
- `last_checked_at` TEXT
- `license_notes` TEXT
- `notes` TEXT
