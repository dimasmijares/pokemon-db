# Upstream Requests

Estado simple para requests entre workspaces.

## Carpetas

- `open/`: petición pendiente
- `done/`: petición resuelta o implementada
- `rejected/`: petición descartada

## Regla

- no borrar requests antiguas
- moverlas entre carpetas según estado
- si una petición cambia mucho, crear una nueva en lugar de reescribir historia

## Cabecera mínima recomendada

```md
Status: open
Owner: pokemon-db
Related downstream: pokemon-app
Created: 2026-04-16
Resolved:
Superseded by:
```
