import csv
import json
import math
from pathlib import Path

from cartes_departements_mal_inscrits_nupes_2022 import (
    JOINED_GEOJSON,
    JOINED_T2_GEOJSON,
    MAPS,
    NUPES_CSV,
    NUPES_T2_CSV,
    QA_TOTALS,
    QA_TOTALS_T2,
    WIKIPEDIA_OVERRIDES_CSV,
    add_colors,
    map_html,
)


ROOT = Path(__file__).resolve().parents[3]
QA_OVERRIDES = (
    ROOT / "data/04_analysis/qa/2022-nupes-wikipedia-overrides-appliques.csv"
)


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def to_int(value):
    value = str(value or "").strip()
    return int(value) if value else None


def to_rate(value):
    value = str(value or "").strip().replace(",", ".")
    return float(value) / 100 if value else None


def format_rate(value):
    return f"{value:.6f}" if value is not None else ""


def load_overrides():
    overrides = {}
    for row in read_csv(WIKIPEDIA_OVERRIDES_CSV):
        overrides[row["code_departement"]] = {
            "source": row["source"],
            "voix_t1": to_int(row.get("voix_nupes_wikipedia_t1")),
            "part_t1": to_rate(row.get("pourcentage_nupes_wikipedia_t1")),
            "voix_t2": to_int(row.get("voix_nupes_wikipedia_t2")),
            "part_t2": to_rate(row.get("pourcentage_nupes_wikipedia_t2")),
        }
    return overrides


def apply_overrides(rows, overrides, turn):
    updated = []
    audit = []
    voix_key = f"voix_t{turn}"
    part_key = f"part_t{turn}"
    method = f"total_coalition_wikipedia_t{turn}"

    for row in rows:
        override = overrides.get(row["code_departement"])
        voix = override.get(voix_key) if override else None
        part = override.get(part_key) if override else None
        if voix is None or part is None:
            updated.append(row)
            continue

        before_voix = row["voix_nupes"]
        before_part = row["part_nupes_exprimes"]
        row = {
            **row,
            "voix_nupes": str(voix),
            "part_nupes_exprimes": format_rate(part),
            "methode_nupes": method,
            "source_nupes": override["source"],
            "methode_part_nupes_exprimes": "pourcentage_source_coalition",
        }
        if row.get("inscrits"):
            row["part_nupes_inscrits"] = format_rate(voix / int(row["inscrits"]))
        audit.append(
            {
                "tour": f"T{turn}",
                "code_departement": row["code_departement"],
                "libelle_departement": row["libelle_departement"],
                "voix_avant": before_voix,
                "part_avant": before_part,
                "voix_apres": row["voix_nupes"],
                "part_apres": row["part_nupes_exprimes"],
                "source": row["source_nupes"],
            }
        )
        updated.append(row)
    return updated, audit


def write_totals(rows, path, scope, method):
    totals = {
        "bureaux": sum(int(row["bureaux"]) for row in rows),
        "inscrits": sum(int(row["inscrits"]) for row in rows),
        "exprimes": sum(int(row["exprimes"]) for row in rows),
        "voix_nupes": sum(int(row["voix_nupes"]) for row in rows),
    }
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "scope",
                "bureaux",
                "inscrits",
                "exprimes",
                "voix_nupes",
                "part_nupes_exprimes",
                "methode",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "scope": scope,
                **totals,
                "part_nupes_exprimes": "",
                "methode": method,
            }
        )


def percentile_scores(features, key):
    values = sorted(
        (feature["properties"].get(key), index)
        for index, feature in enumerate(features)
        if isinstance(feature["properties"].get(key), (int, float))
    )
    if len(values) == 1:
        return {values[0][1]: 1.0}
    return {index: rank / (len(values) - 1) for rank, (_, index) in enumerate(values)}


def update_geojson(path, rows):
    by_dep = {row["code_departement"]: row for row in rows}
    geojson = json.loads(path.read_text(encoding="utf-8"))
    for index, feature in enumerate(geojson["features"]):
        props = feature["properties"]
        dep = props.get("code_departement") or props.get("code")
        row = by_dep.get(dep)
        for key in [
            "score_mal_inscription",
            "score_nupes",
            "score_croise",
            "methode_score_croise",
        ]:
            props.pop(key, None)
        if not row:
            continue
        for key in ["bureaux", "inscrits", "exprimes", "voix_nupes", "bureaux_avec_nupes"]:
            props[key] = int(row[key])
        props["methode_nupes"] = row["methode_nupes"]
        props["source_nupes"] = row["source_nupes"]
        props["source_exprimes"] = row["source_exprimes"]
        props["methode_part_nupes_exprimes"] = row["methode_part_nupes_exprimes"]
        for key in ["part_nupes_exprimes", "part_nupes_inscrits"]:
            if row.get(key):
                props[key] = float(row[key])
            else:
                props.pop(key, None)

    mal_scores = percentile_scores(geojson["features"], "part_mal_inscrits")
    nupes_scores = percentile_scores(geojson["features"], "part_nupes_exprimes")
    for index, feature in enumerate(geojson["features"]):
        props = feature["properties"]
        mal_score = mal_scores.get(index)
        nupes_score = nupes_scores.get(index)
        if mal_score is None or nupes_score is None:
            continue
        props["score_mal_inscription"] = round(mal_score, 6)
        props["score_nupes"] = round(nupes_score, 6)
        props["score_croise"] = round(math.sqrt(mal_score * nupes_score), 6)
        props["methode_score_croise"] = "moyenne_geometrique_des_rangs_percentiles"

    add_colors(geojson)
    path.write_text(
        json.dumps(geojson, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return geojson


def write_updated_maps(geojson_t1, geojson_t2):
    MAPS["cross_coalition"].write_text(
        map_html(
            geojson_t1,
            "cross",
            "Croisement mal-inscription x vote NUPES en 2022 - premier tour coalition contrôlée",
            "Vote NUPES au premier tour des législatives 2022, total de coalition Wikipédia quand disponible.",
            "Moyenne géométrique des rangs de mal-inscription et de vote NUPES au premier tour",
            "Mal-inscription : INSEE Première n°1986, Figure 4. Vote NUPES T1 : totaux de coalition Wikipédia quand disponibles ; agrégats ministériels conservés pour les contrôles.",
        ),
        encoding="utf-8",
    )
    MAPS["cross_coalition_web"].write_text(
        map_html(
            geojson_t1,
            "cross",
            "Croisement mal-inscription x vote NUPES en 2022 - premier tour coalition contrôlée",
            "Vote NUPES au premier tour des législatives 2022, total de coalition Wikipédia quand disponible.",
            "Moyenne géométrique des rangs de mal-inscription et de vote NUPES au premier tour",
            "Mal-inscription : INSEE Première n°1986, Figure 4. Vote NUPES T1 : totaux de coalition Wikipédia quand disponibles ; agrégats ministériels conservés pour les contrôles. Version web : contours géographiques simplifiés, données inchangées.",
        ),
        encoding="utf-8",
    )
    MAPS["cross_t2"].write_text(
        map_html(
            geojson_t2,
            "cross",
            "Croisement mal-inscription x vote NUPES en 2022 - second tour coalition contrôlée",
            "Vote NUPES au second tour des législatives 2022, total de coalition Wikipédia quand disponible.",
            "Moyenne géométrique des rangs de mal-inscription et de vote NUPES au second tour",
            "Mal-inscription : INSEE Première n°1986, Figure 4. Vote NUPES T2 : totaux de coalition Wikipédia quand disponibles ; agrégats ministériels conservés pour les contrôles. Les territoires sans donnée INSEE de mal-inscription restent neutres.",
        ),
        encoding="utf-8",
    )


def main():
    overrides = load_overrides()
    rows_t1, audit_t1 = apply_overrides(read_csv(NUPES_CSV), overrides, 1)
    rows_t2, audit_t2 = apply_overrides(read_csv(NUPES_T2_CSV), overrides, 2)
    write_csv(NUPES_CSV, rows_t1)
    write_csv(NUPES_T2_CSV, rows_t2)
    write_totals(
        rows_t1,
        QA_TOTALS,
        "France entière source ministère T1, coalition Wikipédia",
        "totaux de coalition Wikipédia quand disponibles ; exprimés ministère conservés en contrôle",
    )
    write_totals(
        rows_t2,
        QA_TOTALS_T2,
        "France entière source ministère T2, coalition Wikipédia",
        "totaux de coalition Wikipédia T2 quand disponibles ; exprimés ministère conservés en contrôle",
    )
    write_csv(QA_OVERRIDES, audit_t1 + audit_t2)
    geojson_t1 = update_geojson(JOINED_GEOJSON, rows_t1)
    geojson_t2 = update_geojson(JOINED_T2_GEOJSON, rows_t2)
    write_updated_maps(geojson_t1, geojson_t2)
    print(f"Overrides appliqués T1 : {len(audit_t1)}")
    print(f"Overrides appliqués T2 : {len(audit_t2)}")
    print(f"QA : {QA_OVERRIDES}")
    print(f"GeoJSON T1 : {JOINED_GEOJSON}")
    print(f"GeoJSON T2 : {JOINED_T2_GEOJSON}")
    print(f"Carte T2 : {MAPS['cross_t2']}")


if __name__ == "__main__":
    main()
