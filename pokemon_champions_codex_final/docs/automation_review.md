# Revisión de automatización y carga

## Fecha de revisión
2026-04-13

## Resumen ejecutivo
La BD ya puede reconstruirse con datos actuales del formato usando un flujo reproducible:

1. `scripts/sync_current_champions.py`
2. `scripts/derive_competitive_layer.py`
3. `scripts/validate_data.py`
4. `scripts/build_db.py`
5. `scripts/export_views.py`

La parte estable del modelo ya está automatizada o semiautomatizada. La parte cambiante del metajuego se ha separado:

- `pokemon`, `tiers` y `seasons_rules` se sincronizan contra fuentes actuales.
- `stats_base`, `pokemon_abilities`, `moves`, `items` y `speed_profiles` se generan automáticamente para el roster legal actual.
- `pokemon_moves` ya no depende del learnset bruto de Scarlet/Violet: se sincroniza desde la Pokédex actual de Champions Lab y se complementa con sets observados.
- La capa competitiva derivada (`pokemon_roles`, `pokemon_archetypes`, `cores`, `matchups`) se genera en un segundo paso separado y queda trazada como curación derivada, no como dato oficial de juego.

## Cómo está montada la BD

### Clave principal
- La clave canónica es `pokemon_id`.
- Para el roster actual se mantiene el identificador visible en las cards del roster activo y se resuelve contra la Pokédex de Champions Lab por nombre y forma, evitando depender de ids de PokeAPI para formas especiales.

### Separación funcional
- Catálogo estable: `types`, `abilities`, `moves`, `items`, `sources`
- Roster y regulación actual: `pokemon`, `seasons_rules`, `tiers`, `mega_forms`
- Relaciones derivadas: `stats_base`, `pokemon_abilities`, `pokemon_moves`, `speed_profiles`
- Curación competitiva: `roles`, `pokemon_roles`, `archetypes`, `pokemon_archetypes`, `cores`, `matchups`

## Cómo se pueblan ahora las tablas

### Tablas totalmente automatizables

#### `sources`
- Método actual: generación directa en `sync_current_champions.py`
- Fuente: oficial, Champions Lab, Bulbapedia, PokeAPI
- Estado: correcto

#### `seasons_rules`
- Método actual: scraping ligero de Champions Lab para temporada activa y fechas visibles
- Fuente: Champions Lab
- Estado: correcto
- Nota: el campo `notes` conserva la discrepancia observada entre `Regulation Until` en Champions Lab y `current roster until` en Bulbapedia

#### `pokemon`
- Método actual: scraping del roster actual en Champions Lab y enriquecimiento de especies con PokeAPI
- Fuente: Champions Lab + PokeAPI
- Estado: correcto
- Cobertura actual: 208/208 Pokémon legales

#### `stats_base`
- Método actual: Pokédex actual de Champions Lab por cada Pokémon legal del roster actual
- Fuente: Champions Lab
- Estado: correcto
- Cobertura actual: 208/208

#### `tiers`
- Método actual: scraping de la tier visible en cada card del roster activo en Champions Lab
- Fuente: Champions Lab
- Estado: correcto
- Cobertura actual: 208/208

#### `pokemon_abilities`
- Método actual: extracción de habilidades desde la Pokédex actual de Champions Lab por cada Pokémon legal
- Fuente: Champions Lab
- Estado: correcto
- Cobertura actual: 504 relaciones

#### `moves`
- Método actual: catálogo generado desde la Pokédex actual de Champions Lab para el roster legal
- Fuente: Champions Lab
- Estado: correcto
- Cobertura actual: 518 movimientos relevantes del roster actual

#### `abilities`
- Método actual: catálogo generado desde la Pokédex actual de Champions Lab para el roster legal y sus megas
- Fuente: Champions Lab
- Estado: correcto
- Cobertura actual: 190 habilidades

#### `items`
- Método actual: catálogo generado desde ítems observados en sets actuales y piedras mega legales, con fallback a PokeAPI para objetos estándar
- Fuente: Champions Lab + PokeAPI
- Estado: correcto
- Cobertura actual: 161 objetos relevantes del roster actual y megas legales

#### `speed_profiles`
- Método actual: cálculo determinista a nivel 50 desde `stats_base`
- Fuente: derivado interno
- Estado: correcto
- Cobertura actual: 208/208

#### `mega_forms`
- Método actual: lista legal actual desde Bulbapedia, enriquecida con stats y habilidades desde la Pokédex actual de Champions Lab
- Fuente: Bulbapedia + Champions Lab
- Estado: correcto
- Cobertura actual: 59 megas legales
- Riesgo: el nombre de algunas piedras mega personalizadas sigue usando fallback manual si el bundle cambia el etiquetado

#### `pokemon_moves`
- Método actual: move pool confirmado desde la Pokédex actual de Champions Lab, con una segunda capa de movimientos observados en sets
- Fuente: Champions Lab
- Estado: correcto para Champions actual
- Cobertura actual: 14.172 relaciones
- Consecuencia: `v_move_users` ya devuelve una fila por movimiento y separa `move_pool_user_count` frente a `observed_set_user_count`

### Tablas derivadas con automatización controlada

#### `pokemon_roles`
- Método actual: heurísticas reproducibles sobre stats, habilidades, move pool de Champions y señales de metajuego
- Fuente: Champions Lab + reglas internas
- Estado: útil para team-building, no equivalente a dato oficial
- Cobertura actual: 512 relaciones

#### `pokemon_archetypes`
- Método actual: derivación desde equipos curados, core pairs y señales de clima/TR/Tailwind
- Fuente: Champions Lab Meta + reglas internas
- Estado: útil para clasificación funcional
- Cobertura actual: 226 relaciones

#### `matchups`
- Método actual: derivación de checks y soft checks para amenazas S/A usando tipado, bulk y cobertura
- Fuente: Champions Lab + tiers actuales + reglas internas
- Estado: orientativo, con confianza explícita
- Cobertura actual: 48 relaciones

### Tablas que pueden poblarse manualmente o con extracción controlada

#### `roles`
- Método actual: catálogo base mantenido manualmente
- Estado: correcto

#### `archetypes`
- Método actual: catálogo base mantenido manualmente
- Estado: correcto

#### `cores`
- Método actual: parseo de core pairs visibles en Champions Lab Meta
- Fuente: Champions Lab Meta
- Estado: correcto como capa derivada
- Cobertura actual: 6 cores

## Revisión de scripts existentes

### Scripts válidos o reutilizables
- `scripts/build_db.py`
- `scripts/validate_data.py`
- `scripts/export_views.py`
- `scripts/sync_current_champions.py`
- `scripts/derive_competitive_layer.py`
- `scripts/populate_items.py`
- `scripts/populate_moves.py`

### Scripts heredados o peligrosos para usar como fuente de verdad
- `scripts/populate_tiers.py`
  Motivo: tiers hardcodeadas de ejemplo
- `scripts/populate_speed_profiles.py`
  Motivo: cálculo simplificado y temporada antigua
- `scripts/populate_pokemon_roles_archetypes.py`
  Motivo: asignación heurística por tipo
- `scripts/populate_pokemon_abilities.py`
  Motivo: solo 6 filas de muestra
- `scripts/populate_pokemon_moves.py`
  Motivo: solo 6 filas de muestra
- `scripts/populate_block2.py`
  Motivo: seed grande embebido manualmente; útil como referencia, no como verdad actual
- `scripts/populate_block3.py`
  Motivo: seed embebido parcial; útil como referencia, no como verdad actual

## Qué es posible automatizar mejor

### Muy recomendable
1. Mantener `pokemon`, `tiers` y `seasons_rules` desde Champions Lab mientras siga renderizando HTML estático.
2. Mantener `stats_base`, `pokemon_abilities`, `moves` y `speed_profiles` desde la Pokédex actual de Champions Lab.
3. Mantener `mega_forms` comparando Bulbapedia con seed local hasta encontrar una fuente mejor para megas personalizadas.

### Posible, pero con más trabajo
1. Elevar de `observed_set` a métricas de uso reales por movimiento si Champions Lab expone una API más estable.
2. Sustituir parte de `pokemon_roles`, `pokemon_archetypes` y `matchups` por señales más directas desde equipos o usage reales.
3. Añadir una fuente adicional para resolver conflictos de vigencia entre Champions Lab y Bulbapedia.

### No recomendable sin nueva fuente
1. Tratar la capa derivada como si fuera dato oficial del cliente.
2. Volver a usar learnsets genéricos de PokeAPI como verdad primaria si ya existe una fuente más cercana al juego actual.
3. Inferir matchups complejos de alto nivel sin una fuente competitiva externa.

## Estado actual de carga

### Cobertura lograda
- `pokemon`: 208
- `stats_base`: 208
- `tiers`: 208
- `speed_profiles`: 208
- `pokemon_abilities`: 504
- `pokemon_moves`: 14172
- `mega_forms`: 59
- `pokemon_roles`: 512
- `pokemon_archetypes`: 224
- `cores`: 6
- `matchups`: 48

## Siguiente mejora recomendada
La siguiente mejora con mejor retorno es reforzar la trazabilidad de la capa derivada:

- elevar la confianza de `pokemon_roles`, `pokemon_archetypes` y `matchups` usando fuentes de equipos o usage más directas
- añadir indicadores de frecuencia real para los movimientos `observed_set` si la fuente se mantiene accesible

La arquitectura ya separa dato estructural confirmado de Champions y curación derivada. El trabajo pendiente ya no es cerrar el move pool, sino elevar la calidad probatoria de la capa competitiva.
