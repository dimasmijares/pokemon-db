# Handoff para Agente Web

## Qué archivo debes consumir primero

1. `manifest.json`
2. `docs/handoff.md`

Con esos dos archivos ya deberías poder empezar a trabajar sin inspección manual larga.

## Qué SQLite debes usar

- Archivo principal: `db/pokemon_champions.sqlite`

No uses CSV sueltos como fuente primaria en el repo web. El contrato operativo de consumo es la SQLite y, cuando convenga, los JSON de `exports/`.

## Qué vistas usar en frontend

### Listado principal

- `v_team_builder_pool`

Usa esta vista para:

- listados de Pokemon legales
- búsqueda por nombre
- filtros por tier
- filtros por rol o arquetipo ya derivados
- nombres localizados desde el propio export de listado

### Detalle de Pokemon

- `v_pokemon_summary`

Usa esta vista para:

- ficha base
- tipos
- stats base
- habilidades actuales
- roles y arquetipos derivados
- tier actual

Y usa estos exports estructurados para evitar joins locales:

- `exports/pokemon_detail_index.json`
- `exports/pokemon_abilities_summary.json`
- `exports/pokemon_moves_summary.json`

### Búsqueda y filtros de velocidad

- `v_speed_table`

Usa esta vista para:

- speed tiers
- filtros por velocidad base
- candidatos de Espacio Raro

### Búsqueda y filtros de movimientos

- `v_move_users`

Campos relevantes:

- `move_key`
- `name_en`
- `move_pool_user_count`
- `observed_set_user_count`
- `observed_set_coverage_pct`
- `users`
- `name_es`

Interpretación:

- `move_pool_user_count`: cuantos Pokemon tienen ese movimiento en el move pool actual de Champions
- `observed_set_user_count`: cuantos Pokemon lo llevan en sets observados
- `observed_set_coverage_pct`: proporcion observada respecto al move pool
- en el export JSON, `users` sale estructurado y enlazable por `pokemon_id`

### Filtros temáticos rápidos

- `v_rain_candidates`
- `v_sun_candidates`
- `v_trick_room_candidates`
- `v_charizard_answers`

## Qué campos son estables

Trátalos como identificadores estables para integración:

- `pokemon_id`
- `species_key`
- `form_key`
- `move_key`
- `ability_key`
- `item_key`
- `season_key`

Notas:

- `species_key` no es único por sí solo
- la clave funcional de especie+forma es `species_key + form_key`
- para detalle y joins, prioriza `pokemon_id`

## Qué partes son derivadas y no debes presentar como oficiales

Estas tablas no son dato oficial del juego:

- `pokemon_roles`
- `pokemon_archetypes`
- `cores`
- `matchups`

Regla de presentación:

- pueden mostrarse como análisis, sugerencia o clasificación táctica
- no deben mostrarse como si fueran reglas oficiales, tier oficial o dato interno del juego

## Qué partes sí son dato confirmado o estructural

Base estructural confirmada para el estado actual del bundle:

- `pokemon`
- `stats_base`
- `pokemon_abilities`
- `moves`
- `pokemon_moves`
- `items`
- `mega_forms`
- `tiers`
- `speed_profiles`
- `seasons_rules`
- `types`
- `sources`

Importante sobre `pokemon_moves`:

- ya no sale de un learnset genérico de Scarlet/Violet
- sale del move pool actual visible en Champions Lab
- además puede incluir capa `observed_set` para movimientos vistos en sets

## Recomendación de consumo web

Si quieres minimizar complejidad:

1. usa `v_team_builder_pool` para listados
2. usa `v_pokemon_summary` para detalle
3. usa `v_speed_table` para speed logic
4. usa `v_move_users` para búsquedas por movimiento
5. usa los exports `pokemon_abilities_summary.json`, `pokemon_moves_summary.json`, `pokemon_roles_summary.json` y `pokemon_archetypes_summary.json` para detalle y localización sin joins locales

Si necesitas páginas estáticas o caché:

- puedes consumir directamente los JSON de `exports/`
- cada JSON está exportado desde una vista o query documentada en `manifest.json`
