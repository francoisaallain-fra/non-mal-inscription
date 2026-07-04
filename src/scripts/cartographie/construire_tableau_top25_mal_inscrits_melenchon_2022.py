import argparse
import csv
import html
import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[3]
GEOJSON = (
    ROOT
    / "data/04_analysis/cartographie/2022-departements-mal-inscription-melenchon.geojson"
)
DEMOGRAPHY_CSV = (
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-melenchon-top25.csv"
)
OUTPUT_MD = ROOT / "top-25-departements-mal-inscrits-melenchon-2022.md"

INSEE_URL = "https://www.insee.fr/fr/statistiques/2011101?geo=DEP-{code}"
USER_AGENT = "non-mal-inscription/1.0 (recherche reproductible; contact via GitHub)"

RATE_18_25 = 0.387
RATE_26_29 = 0.343
RATE_30_34 = 0.309
LEGACY_RATE_18_34 = 0.52


def parse_args():
    parser = argparse.ArgumentParser(
        description="Construit le tableau Top 25 mal-inscription x Mélenchon 2022."
    )
    parser.add_argument(
        "--refresh-insee",
        action="store_true",
        help="Retélécharge les données Insee même si le CSV intermédiaire existe.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Délai en secondes entre deux pages Insee (défaut : 0,2).",
    )
    return parser.parse_args()


def clean_text(value):
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).replace("\xa0", " ").strip()


def parse_number(value):
    value = clean_text(value).replace(" ", "").replace(",", ".")
    return float(value)


def table_html(page, table_id):
    match = re.search(
        rf'<table[^>]+id="{re.escape(table_id)}"[^>]*>(.*?)</table>',
        page,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Table Insee introuvable : {table_id}")
    return match.group(1)


def row_values(table, label):
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, flags=re.DOTALL):
        header = re.search(r'<th[^>]*scope="row"[^>]*>(.*?)</th>', row, re.DOTALL)
        if not header or clean_text(header.group(1)) != label:
            continue
        return [
            parse_number(value)
            for value in re.findall(
                r'<td[^>]*class="[^"]*nombre[^"]*"[^>]*>(.*?)</td>',
                row,
                re.DOTALL,
            )
        ]
    raise ValueError(f"Ligne Insee introuvable : {label}")


def fetch_insee(code):
    url = INSEE_URL.format(code=code)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        page = response.read().decode("utf-8")

    population_table = table_html(page, "produit-tableau-POP_T0")
    education_table = table_html(page, "produit-tableau-FOR_T1")

    population_30_44 = row_values(population_table, "30 à 44 ans")[-2]
    school_18_24, population_18_24 = row_values(education_table, "De 18 à 24 ans")
    school_25_29, population_25_29 = row_values(education_table, "De 25 à 29 ans")

    return {
        "population_18_24": round(population_18_24),
        "population_25_29": round(population_25_29),
        "population_30_44": round(population_30_44),
        "population_scolarisee_18_24": round(school_18_24),
        "population_scolarisee_25_29": round(school_25_29),
        "source_insee": url,
    }


def load_top25():
    data = json.loads(GEOJSON.read_text(encoding="utf-8"))
    rows = [
        feature["properties"]
        for feature in data["features"]
        if isinstance(feature["properties"].get("score_croise"), (int, float))
    ]
    return sorted(rows, key=lambda row: row["score_croise"], reverse=True)[:25]


def write_demography(rows, delay):
    output = []
    for index, row in enumerate(rows):
        code = row["code_departement"]
        values = fetch_insee(code)
        output.append(
            {
                "code_departement": code,
                "libelle_departement": row["libelle_departement"],
                **values,
            }
        )
        if index + 1 < len(rows):
            time.sleep(delay)

    DEMOGRAPHY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with DEMOGRAPHY_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    return {row["code_departement"]: row for row in output}


def load_demography():
    with DEMOGRAPHY_CSV.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return {row["code_departement"]: row for row in rows}


def localized_young_estimate(row):
    population_18_24 = float(row["population_18_24"])
    population_25_29 = float(row["population_25_29"])
    population_30_34 = float(row["population_30_44"]) / 3

    rate_25_29 = (RATE_18_25 + 4 * RATE_26_29) / 5
    return (
        population_18_24 * RATE_18_25
        + population_25_29 * rate_25_29
        + population_30_34 * RATE_30_34
    )


def format_int(value):
    return f"{round(value):,}".replace(",", " ")


def format_pct(value, digits=1):
    return f"{value * 100:.{digits}f}".replace(".", ",") + " %"


def build_markdown(top25, demography):
    enriched = []
    for rank, row in enumerate(top25, start=1):
        age = demography[row["code_departement"]]
        mal_estimated = row["part_mal_inscrits"] * row["inscrits"]
        localized = localized_young_estimate(age)
        school = int(age["population_scolarisee_18_24"]) + int(
            age["population_scolarisee_25_29"]
        )
        population_18_29 = int(age["population_18_24"]) + int(age["population_25_29"])
        enriched.append(
            {
                "rank": rank,
                "name": row["libelle_departement"],
                "mal_estimated": mal_estimated,
                "young_localized": localized,
                "young_legacy": mal_estimated * LEGACY_RATE_18_34,
                "school": school,
                "school_share": school / population_18_29,
                "mal_share": row["part_mal_inscrits"],
                "melenchon_share": row["part_melenchon_exprimes"],
                "score": row["score_croise"],
                "inscrits": row["inscrits"],
            }
        )

    total_mal = sum(row["mal_estimated"] for row in enriched)
    total_inscrits = sum(row["inscrits"] for row in enriched)
    total_school = sum(row["school"] for row in enriched)
    total_population_18_29 = sum(
        int(demography[row["code_departement"]]["population_18_24"])
        + int(demography[row["code_departement"]]["population_25_29"])
        for row in top25
    )

    lines = [
        "# Top 25 des départements mal-inscription x vote Mélenchon en 2022",
        "",
        "Classement selon la moyenne géométrique des rangs percentiles de "
        "mal-inscription et de vote Mélenchon au premier tour de la présidentielle :",
        "",
        "`score_croise = sqrt(score_mal_inscription * score_melenchon)`",
        "",
        "La nouvelle estimation territorialisée des 18-34 ans applique les taux "
        "nationaux de mal-inscription par âge de la figure 3 de l'Insee aux "
        "populations d'âge départementales RP2022. L'ancienne méthode uniforme "
        "est conservée dans une colonne explicitement marquée « 52 % ».",
        "",
        "| Rang | Département | Mal-inscrits estimés | 18-34 ans estimés, méthode territorialisée | 18-34 ans estimés, ancienne méthode uniforme 52 % | Population scolarisée 18-29 ans | Part scolarisée des 18-29 ans | Mal-inscrits | Vote Mélenchon | Score croisé |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in enriched:
        score = f"{row['score']:.3f}".replace(".", ",")
        lines.append(
            f"| {row['rank']} | {row['name']} | {format_int(row['mal_estimated'])} "
            f"| {format_int(row['young_localized'])} "
            f"| {format_int(row['young_legacy'])} "
            f"| {format_int(row['school'])} "
            f"| {format_pct(row['school_share'])} "
            f"| {format_pct(row['mal_share'])} "
            f"| {format_pct(row['melenchon_share'], 2)} "
            f"| {score} |"
        )

    lines.extend(
        [
            f"| **Total top 25** | **25 départements** | **{format_int(total_mal)}** "
            f"| **{format_int(sum(row['young_localized'] for row in enriched))}** "
            f"| **{format_int(sum(row['young_legacy'] for row in enriched))}** "
            f"| **{format_int(total_school)}** "
            f"| **{format_pct(total_school / total_population_18_29)}** "
            f"| **{format_pct(total_mal / total_inscrits)}** | **n.d.** | **-** |",
            "",
            "## Méthodes et limites",
            "",
            "### Mal-inscrits estimés",
            "",
            "`part départementale Insee × inscrits électoraux à la présidentielle 2022`.",
            "",
            "### 18-34 ans, méthode territorialisée",
            "",
            "```text",
            "population 18-24 ans × 38,7 %",
            "+ population 25-29 ans × 35,18 %",
            "+ (population 30-44 ans / 3) × 30,9 %",
            "```",
            "",
            "Cette méthode territorialise les volumes, mais les données publiques "
            "utilisées portent sur toute la population résidente et non uniquement "
            "sur les personnes de nationalité française. Elle reste donc une "
            "approximation exploratoire.",
            "",
            "Sources : Insee Première n°1986, figures 3 et 4 ; Insee RP2022, "
            "dossiers complets départementaux, tableaux POP T0 et FOR T1 ; "
            "ministère de l'Intérieur via Hexagonal, présidentielle 2022 T1.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = parse_args()
    top25 = load_top25()
    if args.refresh_insee or not DEMOGRAPHY_CSV.exists():
        demography = write_demography(top25, args.delay)
    else:
        demography = load_demography()

    missing = [
        row["code_departement"]
        for row in top25
        if row["code_departement"] not in demography
    ]
    if missing:
        raise SystemExit(
            "Données démographiques manquantes pour : " + ", ".join(missing)
        )

    build_markdown(top25, demography)
    print(f"Tableau écrit : {OUTPUT_MD}")
    print(f"Données Insee : {DEMOGRAPHY_CSV}")


if __name__ == "__main__":
    main()
