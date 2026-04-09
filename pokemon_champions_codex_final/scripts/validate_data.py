from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data_raw"

def count_rows(csv_name: str) -> int:
    path = RAW / csv_name
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return max(0, len(rows) - 1)

def validate_duplicates(csv_name: str, key_column: str) -> list:
    """Detecta claves duplicadas en una columna."""
    path = RAW / csv_name
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        keys = [row[key_column] for row in reader if row[key_column]]
    seen = set()
    duplicates = []
    for key in keys:
        if key in seen:
            duplicates.append(key)
        else:
            seen.add(key)
    return duplicates

def validate_missing_translations(csv_name: str, en_col: str, es_col: str) -> int:
    """Cuenta filas con traducciones faltantes."""
    path = RAW / csv_name
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = sum(1 for row in reader if not row.get(es_col) and row.get(en_col))
    return missing

def main():
    files = sorted(p.name for p in RAW.glob("*.csv"))
    print("Validación básica:")
    for name in files:
        print(f"- {name}: {count_rows(name)} filas de datos")
    
    print("\nValidaciones adicionales:")
    # Duplicados en pokemon.csv
    dups = validate_duplicates("pokemon.csv", "species_key")
    if dups:
        print(f"- Duplicados en species_key (pokemon.csv): {dups}")
    else:
        print("- No duplicados en species_key (pokemon.csv)")
    
    # Traducciones faltantes
    missing_es = validate_missing_translations("pokemon.csv", "name_en", "name_es")
    if missing_es:
        print(f"- Traducciones faltantes en pokemon.csv: {missing_es} filas")
    else:
        print("- Todas las traducciones presentes en pokemon.csv")
    
    print("\nPendiente de ampliar:")
    print("- detectar Pokémon sin estadísticas")
    print("- detectar movimientos huérfanos")
    print("- detectar megas sin piedra")
    print("- detectar tiers sin temporada")

if __name__ == "__main__":
    main()
