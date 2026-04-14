# Especificaciones consolidadas

## Propósito
Esta base de datos debe servir como repositorio estructurado para analizar el formato competitivo de **Pokémon Champions**, con foco inicial en **Dobles**, y permitir consultas de:

- legalidad de Pokémon por temporada
- tiers por temporada y formato
- estadísticas base y formas mega
- habilidades, movimientos e ítems
- perfiles de velocidad a nivel 50
- roles, arquetipos, cores y matchups
- candidatos para construcción de equipos por clima o estilo
- respuestas a amenazas concretas del meta

## Alcance funcional

### 1. Capa de dato base
La BD debe almacenar, como mínimo:

- roster de Pokémon y formas relevantes
- tipados
- estadísticas base
- habilidades disponibles
- movimientos disponibles y su disponibilidad en Champions
- formas mega y sus piedras
- ítems relevantes
- reglas de temporada

Esta capa representa el dato más cercano a fuente primaria o secundaria verificable.

### 2. Capa de metajuego
La BD debe permitir modelar:

- tiers por temporada
- legalidad por temporada
- disponibilidad por formato
- snapshots del pool jugable en dobles

Esta capa depende de una combinación de fuente oficial, fuente fan especializada y curación documentada.

### 3. Capa de curación competitiva
La BD debe almacenar inferencias y curación no oficiales, separadas del dato base:

- roles
- arquetipos
- relaciones Pokémon-arquetipo
- cores recomendados
- matchups, checks, counters y respuestas
- notas de team-building

Todo dato curado debe conservar trazabilidad mediante `source_key`, `notes` y, cuando aplique, `confidence`.

### 4. Capa de consulta
La BD debe exponer vistas preparadas para análisis y uso práctico.

Vistas mínimas objetivo:

- `v_pokemon_summary`
- `v_speed_table`
- `v_move_users`
- `v_team_builder_pool`
- `v_rain_candidates`
- `v_sun_candidates`
- `v_trick_room_candidates`
- `v_charizard_answers`

## Requisitos funcionales

### RF-01. Consultar legalidad
Debe ser posible saber qué Pokémon son legales en una temporada concreta.

Entradas mínimas:

- `pokemon`
- `seasons_rules`
- `tiers`

### RF-02. Consultar tier actual e histórico
Debe ser posible consultar el tier de un Pokémon por temporada y formato.

Entradas mínimas:

- `pokemon`
- `tiers`

### RF-03. Consultar ficha base de un Pokémon
Debe ser posible recuperar una ficha resumida con:

- nombre
- forma
- tipos
- tier
- estadísticas base
- habilidades principales
- disponibilidad por formato

Salida principal:

- `v_pokemon_summary`

### RF-04. Consultar movimientos por Pokémon y usuarios por movimiento
Debe ser posible:

- listar movimientos de un Pokémon
- listar qué Pokémon usan un movimiento concreto
- distinguir entre movimientos confirmados y no confirmados en Champions

Entradas mínimas:

- `moves`
- `pokemon_moves`

Salida principal:

- `v_move_users`

### RF-05. Consultar velocidad competitiva a nivel 50
Debe ser posible calcular o almacenar perfiles de velocidad comparables para dobles:

- mínima naturaleza negativa
- mínima neutra
- máxima neutra
- máxima positiva
- máximos con boosts
- rating aproximado para Espacio Raro

Entradas mínimas:

- `stats_base`
- `speed_profiles`

Salida principal:

- `v_speed_table`

### RF-06. Consultar pool para team-building
Debe ser posible obtener un pool filtrable para construcción de equipos usando:

- tier
- roles
- habilidades
- arquetipos
- legalidad

Salida principal:

- `v_team_builder_pool`

### RF-07. Consultar candidatos por arquetipo o clima
Debe ser posible listar candidatos útiles para:

- lluvia
- sol
- Espacio Raro
- balance y otros arquetipos posteriores

Salidas objetivo:

- `v_rain_candidates`
- `v_sun_candidates`
- `v_trick_room_candidates`

### RF-08. Consultar respuestas a amenazas del meta
Debe ser posible almacenar y consultar qué respuestas existen contra amenazas concretas.

Caso inicial explícito:

- respuestas a Mega Charizard Y

Entradas mínimas:

- `matchups`
- `cores`
- `pokemon_roles`

Salida objetivo:

- `v_charizard_answers`

### RF-09. Mantener bilingüismo parcial
Siempre que sea posible, la BD debe almacenar:

- clave técnica estable en inglés
- nombre visible en inglés
- nombre visible en castellano

Convención base:

- claves en `*_key`
- nombres visibles en `*_en` y `*_es`

### RF-10. Diferenciar dato confirmado y dato inferido
La BD no debe mezclar sin marcar:

- dato oficial o verificable
- dato fan especializado
- inferencia manual

Los registros curados deben incluir:

- `source_key`
- `notes`
- `confidence` cuando proceda

## Modelo de datos funcional

### Entidades base

- `pokemon`
- `stats_base`
- `abilities`
- `pokemon_abilities`
- `moves`
- `pokemon_moves`
- `mega_forms`
- `items`
- `seasons_rules`
- `tiers`
- `types`
- `sources`

### Entidades de curación

- `roles`
- `pokemon_roles`
- `archetypes`
- `pokemon_archetypes`
- `cores`
- `matchups`
- `speed_profiles`

## Política de fuentes

Prioridad esperada:

1. fuente oficial de Pokémon Champions
2. fuente fan especializada en Champions para roster, tiers y meta
3. fuente fan especializada para stats, habilidades y movimientos
4. curación manual documentada

Reglas operativas:

- si una fuente oficial contradice una fan, prevalece la oficial
- no presentar curación como dato oficial
- no mezclar dato confirmado e inferido sin marcarlo
- registrar `trust_level`, `source_type` y `last_checked_at` cuando sea posible

## Cómo se poblaría la BD

### Fase 1. Inicialización estructural
Se crea el esquema SQLite y las vistas base.

Acciones:

- definir tablas
- definir vistas
- preparar `data_raw/*.csv`
- preparar validaciones básicas

Script principal:

- `scripts/build_db.py`

### Fase 2. Carga de fuentes maestras
Se pueblan primero los catálogos y tablas maestras.

Orden recomendado:

1. `sources.csv`
2. `types.csv`
3. `seasons_rules.csv`
4. `pokemon.csv`
5. `stats_base.csv`
6. `abilities.csv`
7. `pokemon_abilities.csv`
8. `moves.csv`
9. `pokemon_moves.csv`
10. `items.csv`
11. `mega_forms.csv`
12. `tiers.csv`

Objetivo:

- tener una capa base consultable y consistente

### Fase 3. Carga competitiva
Se añaden tablas curadas y dependientes del formato.

Orden recomendado:

1. `roles.csv`
2. `pokemon_roles.csv`
3. `archetypes.csv`
4. `pokemon_archetypes.csv`
5. `cores.csv`
6. `matchups.csv`
7. `speed_profiles.csv`

Objetivo:

- habilitar consultas de team-building y meta

### Fase 4. Generación de vistas y exports
Una vez cargadas las tablas, se regeneran vistas y exportaciones útiles.

Resultados esperados:

- SQLite final lista para consulta
- CSV exportados para revisión rápida

### Fase 5. Validación continua
Cada actualización de CSV debe pasar validaciones mínimas.

Validaciones mínimas:

- duplicados de claves
- traducciones ausentes donde aplique
- referencias huérfanas
- Pokémon sin stats
- movimientos sin usuarios o usuarios con movimientos inexistentes
- tiers sin temporada
- megas sin piedra o sin especie base clara

## Fuente de verdad recomendada
La intención funcional del proyecto debe tomarse de esta prioridad:

1. `docs/specifications.md`
2. `docs/schema.md`
3. `docs/source_policy.md`
4. `docs/curation_policy.md`
5. `docs/roadmap.md`

## Gaps detectados en el repositorio actual

### Gap 1. La cobertura de datos sigue siendo parcial
Aunque la estructura ya está alineada, la cobertura actual sigue siendo incompleta en:

- `stats_base`
- `tiers`
- `speed_profiles`
- relaciones de habilidades y movimientos

### Gap 2. Algunas heurísticas de vistas son todavía básicas
Las vistas de clima y de respuestas existen, pero aún dependen de reglas simples de tipado, habilidades y matchups cargados.

### Gap 3. La especificación ya está consolidada, pero necesita mantenerse viva
La documentación base ya está centralizada, pero debe mantenerse sincronizada con cambios futuros en CSV, validaciones y vistas.

Referencia de estado:

- ver `docs/validation_report.md`

## Criterio de aceptación funcional
Se considerará que la BD cumple su objetivo mínimo cuando permita:

- consultar roster legal y tiers del formato de dobles actual
- recuperar ficha resumida por Pokémon
- consultar velocidades a nivel 50
- consultar movimientos y habilidades por Pokémon
- filtrar candidatos para team-building
- consultar al menos un conjunto inicial de roles, arquetipos y respuestas de matchup
- mantener trazabilidad de fuente y distinguir dato base de curación
