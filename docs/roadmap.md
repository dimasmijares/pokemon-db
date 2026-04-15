# Hoja de ruta

## Estado actual

Completado y operativo:

- sincronización del roster legal actual
- sincronización de reglas de temporada y tiers actuales
- carga de stats, habilidades, movimientos, ítems y megas legales
- generación de `speed_profiles`
- reconstrucción reproducible de SQLite
- exports frontend-ready y `data_bundle/`
- validación estructural, comparativa y de cobertura localizada
- capa competitiva derivada (`roles`, `archetypes`, `cores`, `matchups`)

## Pendientes de datos

### Prioridad alta

- completar una fuente fiable para `items.effect_short_es` y `items.effect_long_es`
- mejorar la cobertura restante de `abilities.description_es`
- mejorar la cobertura restante de `moves.effect_short_es` y `moves.effect_long_es`

### Prioridad media

- reforzar con una fuente más directa la capa derivada de curación por Pokémon:
  - `pokemon_roles`
  - `pokemon_archetypes`
  - `matchups`
- consolidar una política estable para `cores` si Champions Lab cambia el HTML o la terminología visible
- añadir, si la fuente lo permite, métricas de frecuencia o win rate por movimiento para complementar `observed_set`

## Pendientes de producto / contrato

- revisar si el bundle debe exponer más texto corto bilingüe útil para `pokemon-app`
- mantener documentado qué partes son oficiales, confirmadas o derivadas
- seguir respondiendo a peticiones upstream concretas desde `pokemon-app` cuando el contrato no cubra una necesidad real de UX

## Pendientes de criterio funcional

- afinar la lógica de candidatos por clima con reglas competitivas más precisas
- enriquecer `matchups` y `cores`
- decidir si `format_availability` debe pasar de `standard` a un vocabulario más formal

## Mejora futura de handoff

- desacoplar la importación del `data_bundle` de rutas locales fijas entre repos
- permitir origen configurable del bundle o distribución como artefacto remoto versionado

## Mejora futura de automatización

- mantener primero un flujo semiautomático local robusto con `scripts/release_bundle.ps1`
- evaluar después automatización gratuita con GitHub Actions para regeneración periódica del bundle
- añadir validaciones de regresión y diff contra la ejecución anterior antes de publicar cambios
- publicar solo si el pipeline pasa y la calidad mínima del dato se mantiene
- estudiar sincronización posterior hacia `pokemon-app` mediante importación controlada, preferiblemente sin push ciego a producción
