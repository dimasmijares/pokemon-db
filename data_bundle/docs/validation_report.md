# Informe de validación

## Fecha
2026-04-15

## Resultado ejecutivo
La estructura de la BD ya está alineada con la especificación funcional base:

- la clave canónica es `pokemon_id`
- la SQLite se reconstruye desde cero sin arrastrar artefactos heredados
- las vistas objetivo ya existen
- la validación detecta integridad referencial y cobertura

El estado actual es **estructuralmente válido**, con avisos pendientes de **cobertura localizada parcial**.
Tras la sincronización del 15 de abril de 2026, la cobertura del roster legal actual ya es completa en `pokemon`, `stats_base`, `tiers` y `speed_profiles`.
Además, el flujo semiautomático deja ahora dos resúmenes operativos:

- `data_build/sync_summary.json`
- `data_build/validation_summary.json`

## Comandos ejecutados

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_bundle.ps1
```

## Estado de validación

### Errores críticos
- ninguno

### Avisos actuales
- `species_key` se repite en 16 especies con formas; debe interpretarse junto con `form_key`
- `pokemon_moves` mezcla dos capas confirmadas de Champions: `champions_move_pool` y `observed_set`; no deben interpretarse como la misma semántica
- `pokemon_roles`, `pokemon_archetypes`, `cores` y `matchups` ya se cargan, pero como capa derivada y no como dato oficial del juego
- la cobertura ES sigue incompleta en descripciones de habilidades, descripciones de movimientos y, especialmente, ítems

## Cobertura localizada observada

- `pokemon.name_es`: `208/208` (`100.0%`)
- `abilities.name_es`: `190/190` (`100.0%`)
- `abilities.description_es`: `174/190` (`91.6%`)
- `moves.name_es`: `518/518` (`100.0%`)
- `moves.effect_short_es`: `469/518` (`90.5%`)
- `moves.effect_long_es`: `469/518` (`90.5%`)
- `items.name_es`: `161/161` (`100.0%`)
- `items.effect_short_es`: `0/161` (`0.0%`)
- `items.effect_long_es`: `0/161` (`0.0%`)
- `roles.name_es`: `6/6` (`100.0%`)
- `roles.description_es`: `6/6` (`100.0%`)
- `archetypes.name_es`: `9/9` (`100.0%`)
- `archetypes.description_es`: `9/9` (`100.0%`)

## Comparativa antes / después de la carga ES

- `abilities.description_es`: de `0/190` a `174/190`
- `moves.effect_short_es`: de `0/518` a `469/518`
- `moves.effect_long_es`: de `0/518` a `469/518`
- `items.effect_short_es`: de `0/161` a `0/161`
- `items.effect_long_es`: de `0/161` a `0/161`

## Método de enriquecimiento ES

- `abilities`: nombre ES desde `PokeAPI.names`, descripción ES desde `PokeAPI.flavor_text_entries`
- `moves`: nombre ES desde `PokeAPI.names`, textos ES desde `PokeAPI.flavor_text_entries`
- `items`: nombre ES desde `PokeAPI.names`; los textos ES siguen vacíos porque `PokeAPI` no aporta una capa localizada equivalente y no se ha introducido traducción manual no verificable
- el pipeline deja ahora métricas localizadas explícitas en `data_build/validation_summary.json`

## Comprobaciones que ya pasan

### Integridad referencial
- `stats_base.csv` sin `pokemon_id` huérfanos
- `pokemon_abilities.csv` sin `pokemon_id` ni `ability_key` huérfanos
- `pokemon_moves.csv` sin `pokemon_id` ni `move_key` huérfanos
- `tiers.csv` sin `pokemon_id` ni `season_key` huérfanos
- `pokemon_roles.csv` sin `pokemon_id`, `role_key` ni `season_key` huérfanos
- `pokemon_archetypes.csv` sin `pokemon_id`, `archetype_key` ni `season_key` huérfanos
- `speed_profiles.csv` sin `pokemon_id` ni `season_key` huérfanos
- `mega_forms.csv` sin `pokemon_id` ni `mega_stone_key` huérfanos
- `matchups.csv` sin referencias huérfanas
- `cores.csv` sin referencias huérfanas

### Fuentes
- `roster_source_key`, `source_key`, `tier_source_key` y `curation_source_key` apuntan a fuentes registradas
- `championslab` ya cubre roster, tiers, stats, habilidades, move pool actual y parte del catálogo de megas
- `pokeapi` queda como soporte para especies, traducciones y fallback de ítems estándar

## Estructura observada en SQLite

### Tablas
- `abilities`
- `archetypes`
- `cores`
- `items`
- `matchups`
- `mega_forms`
- `moves`
- `pokemon`
- `pokemon_abilities`
- `pokemon_archetypes`
- `pokemon_moves`
- `pokemon_roles`
- `roles`
- `seasons_rules`
- `sources`
- `speed_profiles`
- `stats_base`
- `tiers`
- `types`

### Vistas
- `v_pokemon_summary`
- `v_speed_table`
- `v_move_users`
- `v_team_builder_pool`
- `v_rain_candidates`
- `v_sun_candidates`
- `v_trick_room_candidates`
- `v_charizard_answers`

## Recuento de vistas
- `v_pokemon_summary`: 208 filas
- `v_speed_table`: 208 filas
- `v_move_users`: 518 filas
- `v_team_builder_pool`: 208 filas
- `v_rain_candidates`: 27 filas
- `v_sun_candidates`: 29 filas
- `v_trick_room_candidates`: 62 filas
- `v_charizard_answers`: 3 filas

## Salvaguardas nuevas del pipeline
- validación explícita del método de extracción de Bulbapedia
- validación de coherencia entre el roster esperado en Champions Lab y el roster realmente extraído
- validación de existencia de `champions_move_pool` y `observed_set`
- comparación contra `data_build/validation_summary.json` previo para detectar regresiones fuertes en métricas clave
- métricas explícitas de cobertura localizada ES para `abilities`, `moves`, `items`, `roles` y `archetypes`
- separación entre errores críticos y warnings asumibles en un flujo semiautomático

## Correcciones aplicadas

1. Se unificó el modelo relacional en `pokemon_id`.
2. Se rellenó `pokemon_id` explícitamente en `pokemon.csv`.
3. Se normalizaron `season_key` y `format` en los CSV competitivos.
4. Se corrigieron `move_key` huérfanos en `pokemon_moves.csv`.
5. Se corrigieron `mega_key` y `mega_stone_key` en `mega_forms.csv`.
6. Se añadió `pokeapi` a `sources.csv`.
7. Se marcó correctamente `is_mega_stone` en `items.csv`.
8. Se reescribió `scripts/build_db.py` para:
   - reconstruir la BD desde cero
   - respetar foreign keys
   - convertir vacíos a `NULL` cuando procede
   - calcular `bst`
   - crear todas las vistas funcionales
9. Se reescribió `scripts/validate_data.py` para validar:
   - claves duplicadas
   - integridad referencial
   - consistencia de fuentes
   - cobertura funcional mínima
10. Se añadió `scripts/sync_current_champions.py` para refrescar el roster legal actual y las tablas volátiles con scraping + enriquecimiento automático.
11. Se añadió `scripts/derive_competitive_layer.py` para poblar `pokemon_roles`, `pokemon_archetypes`, `cores` y `matchups` como capa derivada reproducible.
12. Se ajustó `v_move_users` para separar cobertura estructural del move pool y presencia en sets observados.
13. Se reescribió `scripts/sync_current_champions.py` para usar la Pokédex actual de Champions Lab como fuente primaria de stats, habilidades, move pool y parte del catálogo de megas.
14. Se corrigió la resolución de formas del roster actual, incluyendo casos problemáticos como `Hisuian Avalugg` y `Paldean Tauros`.
15. Se regeneraron `abilities.csv`, `moves.csv` e `items.csv` para el roster y metajuego actual relevantes.
16. Se reajustó `v_move_users` para devolver una sola fila por movimiento, separando `move_pool_user_count` y `observed_set_user_count`.
17. Se endureció `scripts/build_db.py` para reconstruir el esquema incluso cuando Windows mantiene bloqueada la SQLite durante el borrado del archivo.
18. Se refinó la capa derivada para dar más peso a movimientos realmente observados en sets actuales al asignar ciertos roles competitivos.
19. Se desacopló la extracción del bundle de Champions Lab de ids de módulo fijos y se pasó a resolver chunks candidatos con validación estructural.
20. Se pasó `seasons_rules` a derivar también las reglas visibles del dataset activo de Champions Lab, reduciendo hardcodes en la tabla.
21. Se enriquecieron `abilities.csv` y `moves.csv` con nombres y descripciones ES desde `PokeAPI`.
22. Se añadieron métricas de cobertura localizada ES a `scripts/validate_data.py` y a `data_build/validation_summary.json`.
23. Se normalizaron algunos labels cortos bilingües visibles para frontend, como `learn_method_es` en `pokemon_moves`.
21. Se añadió `data_build/sync_summary.json` para dejar métricas y método de extracción por fuente en cada ejecución.
22. Se añadió `data_build/validation_summary.json` para comparar la ejecución actual con la anterior y detectar regresiones silenciosas.

## Trabajo pendiente

### Pendiente de datos
- reforzar con una fuente más directa la capa derivada de curación por Pokémon (`pokemon_roles`, `pokemon_archetypes`, `matchups`)
- consolidar una política estable para `cores` si Champions Lab cambia el marcado HTML o la terminología visible
- añadir, si la fuente lo permite, métricas de frecuencia o win rate por movimiento para complementar `observed_set`

### Pendiente de criterio funcional
- afinar la lógica de candidatos por clima con reglas competitivas más precisas
- enriquecer `matchups` y `cores`
- decidir si `format_availability` debe pasar de `standard` a un vocabulario más formal

## Conclusión
La BD ya cumple el cierre estructural y operativo esperado: todas las tablas están pobladas, la SQLite se reconstruye desde cero y el move pool actual ya sale de una fuente específica de Champions en lugar de un learnset genérico. El trabajo restante ya no es de arquitectura ni de cobertura base, sino de elevar la calidad probatoria de la capa competitiva derivada.
