# Pokémon Champions DB

Base de trabajo para construir una base de datos competitiva de **Pokémon Champions**, con foco en:
- formato **Dobles**
- análisis del metajuego
- construcción de equipos
- traducciones al castellano siempre que sea posible
- versionado y mantenimiento desde Codex

## Objetivo
Montar una BD que permita responder preguntas como:
- qué Pokémon son legales en la temporada actual
- qué tier tienen
- qué estadísticas base tienen
- qué habilidades y movimientos tienen
- qué velocidades alcanzan a nivel 50
- qué candidatos encajan en lluvia, sol, Espacio Raro, balance, etc.
- qué respuestas existen contra amenazas como Mega Charizard Y

## Estructura del proyecto
- `data_raw/`: fuentes editables en CSV
- `data_build/pokemon_champions.sqlite`: base SQLite generada
- `data_build/exports/`: exportaciones útiles
- `scripts/`: scripts de construcción, validación y exportación
- `docs/`: documentación funcional y de diseño

## Estado inicial
Este paquete incluye:
- una **base SQLite semilla** (`data_build/pokemon_champions.sqlite`) si estaba disponible al generar el paquete
- un conjunto de **CSV vacíos con encabezados útiles**
- documentación detallada para seguir en Codex
- scripts esqueleto para construir la BD correctamente

## Flujo recomendado en Codex
1. Revisar `docs/schema.md`
2. Revisar `docs/source_policy.md`
3. Revisar `docs/roadmap.md`
4. Completar y ajustar los CSV de `data_raw/`
5. Implementar `scripts/build_db.py`
6. Implementar `scripts/validate_data.py`
7. Generar la SQLite final
8. Publicarlo en GitHub y continuar iterando

## Vistas objetivo
La BD final debería incluir, como mínimo:
- `v_pokemon_summary`
- `v_speed_table`
- `v_move_users`
- `v_team_builder_pool`
- `v_rain_candidates`
- `v_sun_candidates`
- `v_trick_room_candidates`
- `v_charizard_answers`

## Convención de idioma
Siempre que sea posible:
- guardar campo técnico estable en inglés (`*_key`)
- guardar nombre visible en inglés (`*_en`)
- guardar nombre visible en castellano (`*_es`)

## Siguiente paso recomendado
En Codex:
- crear el esquema completo
- cargar la temporada actual
- poblar roster, tiers, estadísticas, habilidades y movimientos clave
- construir la capa competitiva encima
