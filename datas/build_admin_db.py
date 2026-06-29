#!/usr/bin/env python3
import argparse
import json
import sqlite3
from pathlib import Path


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        DROP TABLE IF EXISTS village;
        DROP TABLE IF EXISTS groupement_quartier;
        DROP TABLE IF EXISTS secteur_chefferie_commune;
        DROP TABLE IF EXISTS territoire_ville;
        DROP TABLE IF EXISTS province;

        CREATE TABLE province (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(source_id)
        );

        CREATE TABLE territoire_ville (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type_name TEXT NOT NULL,
            province_id INTEGER NOT NULL,
            FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE,
            UNIQUE(source_id, province_id)
        );

        CREATE TABLE secteur_chefferie_commune (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type_name TEXT NOT NULL,
            territoire_ville_id INTEGER NOT NULL,
            FOREIGN KEY (territoire_ville_id) REFERENCES territoire_ville(id) ON DELETE CASCADE,
            UNIQUE(source_id, territoire_ville_id)
        );

        CREATE TABLE groupement_quartier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type_name TEXT NOT NULL,
            secteur_chefferie_commune_id INTEGER NOT NULL,
            FOREIGN KEY (secteur_chefferie_commune_id) REFERENCES secteur_chefferie_commune(id) ON DELETE CASCADE,
            UNIQUE(source_id, secteur_chefferie_commune_id)
        );

        CREATE TABLE village (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            village_name TEXT NOT NULL,
            locality_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            objectid INTEGER NOT NULL,
            groupement_quartier_id INTEGER NOT NULL,
            FOREIGN KEY (groupement_quartier_id) REFERENCES groupement_quartier(id) ON DELETE CASCADE,
            UNIQUE(objectid)
        );

        CREATE INDEX idx_tv_province ON territoire_ville(province_id);
        CREATE INDEX idx_scc_tv ON secteur_chefferie_commune(territoire_ville_id);
        CREATE INDEX idx_gq_scc ON groupement_quartier(secteur_chefferie_commune_id);
        CREATE INDEX idx_village_gq ON village(groupement_quartier_id);
        """
    )


def load_geojson(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_database(json_path: Path, db_path: Path) -> None:
    data = load_geojson(json_path)
    features = data.get("features", [])

    conn = sqlite3.connect(db_path)
    try:
        create_schema(conn)
        cur = conn.cursor()

        province_cache: dict[int, int] = {}
        tv_cache: dict[tuple[int, int], int] = {}
        scc_cache: dict[tuple[int, int], int] = {}
        gq_cache: dict[tuple[int, int], int] = {}

        for feature in features:
            props = feature["properties"]

            province_key = props["PROVINCE_ID"]
            province_id = province_cache.get(province_key)
            if province_id is None:
                cur.execute(
                    "INSERT INTO province (source_id, name) VALUES (?, ?)",
                    (props["PROVINCE_ID"], props["PROVINCE"]),
                )
                province_id = cur.lastrowid
                province_cache[province_key] = province_id

            tv_key = (props["TERRITOIRE_VILLE_ID"], province_id)
            territoire_ville_id = tv_cache.get(tv_key)
            if territoire_ville_id is None:
                cur.execute(
                    """
                    INSERT INTO territoire_ville (source_id, name, type_name, province_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        props["TERRITOIRE_VILLE_ID"],
                        props["TERRITOIRE_VILLE"],
                        props["TYPE_TERRITOIRE_VILLE"],
                        province_id,
                    ),
                )
                territoire_ville_id = cur.lastrowid
                tv_cache[tv_key] = territoire_ville_id

            scc_key = (props["SECTEUR_CHEFFERIE_COMMUNE_ID"], territoire_ville_id)
            secteur_id = scc_cache.get(scc_key)
            if secteur_id is None:
                cur.execute(
                    """
                    INSERT INTO secteur_chefferie_commune (source_id, name, type_name, territoire_ville_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        props["SECTEUR_CHEFFERIE_COMMUNE_ID"],
                        props["SECTEUR_CHEFFERIE_COMMNE"],
                        props["TYPE_SECT_CHEF_COM"],
                        territoire_ville_id,
                    ),
                )
                secteur_id = cur.lastrowid
                scc_cache[scc_key] = secteur_id

            gq_key = (props["GROUPEMENT_QUARTIER_ID"], secteur_id)
            groupement_id = gq_cache.get(gq_key)
            if groupement_id is None:
                cur.execute(
                    """
                    INSERT INTO groupement_quartier (source_id, name, type_name, secteur_chefferie_commune_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        props["GROUPEMENT_QUARTIER_ID"],
                        props["GROUPEMENT_QUARTIER"],
                        props["TYPE_GROUPEMENT_QUARTIER"],
                        secteur_id,
                    ),
                )
                groupement_id = cur.lastrowid
                gq_cache[gq_key] = groupement_id

            cur.execute(
                """
                INSERT INTO village (
                    source_id, village_name, locality_name, latitude, longitude, objectid, groupement_quartier_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    props["VILLAGE_ID"],
                    props["VILLAGE"],
                    props["Nom"].strip(),
                    props["Latitude"],
                    props["Longitude"],
                    props["OBJECTID"],
                    groupement_id,
                ),
            )

        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a normalized SQLite database from Entites_admin GeoJSON."
    )
    parser.add_argument(
        "--input",
        default="Entites_admin.json",
        help="Path to input GeoJSON file (default: Entites_admin.json)",
    )
    parser.add_argument(
        "--output",
        default="entites_admin.sqlite",
        help="Path to output SQLite database (default: entites_admin.sqlite)",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    build_database(input_path, output_path)
    print(f"Database created: {output_path}")


if __name__ == "__main__":
    main()
