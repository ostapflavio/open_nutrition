# build_foods_v2.py
# Usage:
#   python build_foods_v2.py /path/to/opennutrition_foods.tsv /path/to/foods_v2.sqlite
#
# Table: ingredients
#   id INTEGER PRIMARY KEY, name VARCHAR(64) NOT NULL,
#   kcal_per_100g REAL NOT NULL CHECK(kcal_per_100g >= 0),
#   carbs_per_100g REAL NOT NULL CHECK(carbs_per_100g >= 0),
#   fats_per_100g REAL NOT NULL CHECK(fats_per_100g >= 0),
#   proteins_per_100g REAL NOT NULL CHECK(proteins_per_100g >= 0)

import sqlite3, json, pandas as pd, os, math, re, csv, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "opennutrition_foods.tsv"
DB  = sys.argv[2] if len(sys.argv) > 2 else "foods_v2.sqlite"
CSV = os.path.splitext(DB)[0].replace(".sqlite","") + ".csv"

COMMIT_EVERY = 5000  # commit periodic

# ---- helpers ----
def to_float(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        if isinstance(x, str):
            x = x.strip()
            x = re.sub(r"[a-zA-Z]+", "", x)  # drop units like g, kcal
            x = x.replace(",", ".")
        return float(x)
    except Exception:
        return None

def energy_kcal_per_100(n):
    if "energy_kcal" in n and n["energy_kcal"] not in (None, ""):
        return to_float(n["energy_kcal"])
    if "calories" in n and n["calories"] not in (None, ""):
        return to_float(n["calories"])
    if "energy" in n and n["energy"] not in (None, ""):  # kJ
        kj = to_float(n["energy"])
        if kj is not None:
            return kj / 4.184
    return None

def first_number(n, keys):
    for k in keys:
        if k in n and n[k] not in (None, ""):
            return to_float(n[k])
    return None

def create_db(conn):
    conn.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    PRAGMA temp_store=MEMORY;

    CREATE TABLE IF NOT EXISTS ingredients (
      id INTEGER PRIMARY KEY,                                 -- auto-assigned
      name TEXT NOT NULL
        CHECK (length(name) <= 64),                           -- enforce VARCHAR(64)
      kcal_per_100g REAL NOT NULL
        CONSTRAINT KCAL_NOT_NEGATIVE CHECK (kcal_per_100g >= 0),
      carbs_per_100g REAL NOT NULL
        CONSTRAINT CARBS_NOT_NEGATIVE CHECK (carbs_per_100g >= 0),
      fats_per_100g REAL NOT NULL
        CONSTRAINT FATS_NOT_NEGATIVE CHECK (fats_per_100g >= 0),
      proteins_per_100g REAL NOT NULL
        CONSTRAINT PROTEINS_NOT_NEGATIVE CHECK (proteins_per_100g >= 0)
    );
    """)
    conn.commit()

def main():
    if os.path.exists(DB):
        os.remove(DB)

    conn = sqlite3.connect(DB)
    create_db(conn)
    cur = conn.cursor()

    inserted = 0
    rows_for_csv = []

    for chunk in pd.read_csv(
        SRC,
        sep="\t",          # REAL tab, keeps fast C engine
        engine="c",
        chunksize=20000,
        dtype=str,
        keep_default_na=False,
        on_bad_lines="skip",
    ):
        name_col = chunk.get("name")
        nutr_col = chunk.get("nutrition_100g")

        cur.execute("BEGIN")
        for name, nutr_json in zip(name_col, nutr_col):
            if not name or not nutr_json:
                continue
            try:
                n = json.loads(nutr_json)
            except Exception:
                continue

            kcal_100      = energy_kcal_per_100(n)
            carbs_100     = first_number(n, ["carbohydrates", "carbs"])
            fats_100      = first_number(n, ["total_fat", "fats", "fat"])
            proteins_100  = first_number(n, ["protein", "proteins"])

            # Enforce NOT NULL: skip rows that miss any required value
            if None in (kcal_100, carbs_100, fats_100, proteins_100):
                continue

            cur.execute("""
              INSERT INTO ingredients(
                name, kcal_per_100g, carbs_per_100g, fats_per_100g, proteins_per_100g
              ) VALUES (?, ?, ?, ?, ?)
            """, (name, kcal_100, carbs_100, fats_100, proteins_100))

            new_id = cur.lastrowid
            rows_for_csv.append((new_id, name, kcal_100, carbs_100, fats_100, proteins_100))
            inserted += 1

            if inserted % COMMIT_EVERY == 0:
                conn.commit()
                cur.execute("BEGIN")

        conn.commit()

    # Index (după încărcare)
    cur.executescript("""
    CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
    """)
    conn.commit()
    conn.close()

    # CSV
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id","name","kcal_per_100g","carbs_per_100g","fats_per_100g","proteins_per_100g"])
        w.writerows(rows_for_csv)

    print(f"Done. SQLite: {DB}\\nCSV: {CSV}\\nRows inserted: {inserted}")

if __name__ == "__main__":
    main()
