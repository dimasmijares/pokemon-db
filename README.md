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

## Responsabilidad del repo
- este repo produce el dato de dominio y el contrato de entrega para otros consumidores
- aquí se mantienen la SQLite, los scripts de sincronización, las validaciones y `data_bundle/`
- si la web necesita nuevos campos, vistas o exports, el cambio debe hacerse aquí primero
- `pokemon-app` debe consumir este contrato, no redefinirlo

## Estructura del proyecto
- raíz del repo: proyecto operativo y raíz Git real
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
1. Revisar `docs/specifications.md`
2. Revisar `docs/validation_report.md`
3. Revisar `docs/automation_review.md`
4. Revisar `docs/schema.md`
5. Ejecutar `python scripts/sync_current_champions.py`
6. Ejecutar `python scripts/derive_competitive_layer.py`
7. Ejecutar `python scripts/validate_data.py`
8. Ejecutar `python scripts/build_db.py`
9. Ejecutar `python scripts/export_views.py`
10. Revisar `docs/source_policy.md`
11. Revisar `docs/roadmap.md`

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
- usar `docs/specifications.md` como contrato funcional
- usar `docs/validation_report.md` como lista de gaps a corregir
- usar `docs/automation_review.md` para distinguir scripts vigentes de scripts legacy
- refrescar el roster actual con `scripts/sync_current_champions.py`
- derivar la capa competitiva actual con `scripts/derive_competitive_layer.py`
- validar, reconstruir y exportar la SQLite de forma secuencial
