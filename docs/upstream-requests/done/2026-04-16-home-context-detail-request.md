Status: done
Owner: pokemon-db
Related downstream: pokemon-app
Created: 2026-04-16
Resolved: 2026-04-22
Superseded by:

# Home Context Detail Request

## Request

Soportar un futuro detalle contextual de Pokémon en home dentro de `pokemon-app`, cubriendo:

- 5 movimientos destacados con detalle corto localizado EN/ES
- habilidades del Pokémon
- megaevolución si existe, con resumen de stats y nueva habilidad

## Implementación aplicada

Se añadió un export ligero nuevo:

- `data_bundle/exports/pokemon_home_context_detail.json`

Fuente:

- `pokemon`
- `v_pokemon_abilities_summary`
- `v_pokemon_moves_summary`
- `moves`
- `mega_forms`
- `abilities`

## Shape entregado

Por cada `pokemon_id`, el export incluye:

- `abilities`
- `highlighted_moves`
  - máximo 5
  - con `effect_short_en` y `effect_short_es`
  - priorizando movimientos observados en sets y luego move pool actual
- `mega_evolution`
  - `null` si el Pokémon no tiene mega actual
  - resumen de stats
  - nueva habilidad con nombre y descripción EN/ES

## Motivo de la solución

Es el cambio mínimo y más limpio porque:

- no obliga a ampliar el esquema SQLite
- no introduce vistas artificiales para un payload anidado
- evita joins locales en `pokemon-app`
- no hincha `pokemon_detail_index.json` con contexto que solo interesa en home o previews

## Notas downstream

- el export está pensado para lookup por `pokemon_id`
- cuando falte texto ES, `pokemon-app` debe seguir usando fallback a EN según la política ya documentada del bundle
