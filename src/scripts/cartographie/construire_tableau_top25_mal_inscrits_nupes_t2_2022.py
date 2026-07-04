import csv
import html
import json
from pathlib import Path

from construire_tableau_top25_mal_inscrits_nupes_2022 import (
    LEGACY_RATE_18_34,
    localized_young_estimate,
    format_int,
    format_pct,
)


ROOT = Path(__file__).resolve().parents[3]
GEOJSON = (
    ROOT / "data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson"
)
DEMOGRAPHY_CSV = (
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-nupes-t2-top25.csv"
)
DEMOGRAPHY_FALLBACKS = [
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-top25.csv",
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-melenchon-top25.csv",
]
OUTPUT_MD = ROOT / "top-25-departements-mal-inscrits-nupes-t2-2022.md"
OUTPUT_HTML = ROOT / "maps/2022-tableau-top25-mal-inscrits-nupes-t2.html"


def read_csv(path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as stream:
        return {row["code_departement"]: row for row in csv.DictReader(stream)}


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_top25():
    data = json.loads(GEOJSON.read_text(encoding="utf-8"))
    rows = [
        feature["properties"]
        for feature in data["features"]
        if isinstance(feature["properties"].get("score_croise"), (int, float))
    ]
    return sorted(rows, key=lambda row: row["score_croise"], reverse=True)[:25]


def ensure_demography(top25):
    demography = read_csv(DEMOGRAPHY_CSV)
    for fallback in DEMOGRAPHY_FALLBACKS:
        for code, row in read_csv(fallback).items():
            demography.setdefault(code, row)
    missing = [row["code_departement"] for row in top25 if row["code_departement"] not in demography]
    if missing:
        raise SystemExit("Données démographiques manquantes pour : " + ", ".join(missing))
    ordered = [demography[row["code_departement"]] for row in top25]
    write_csv(DEMOGRAPHY_CSV, ordered)
    return {row["code_departement"]: row for row in ordered}


def build_rows(top25, demography):
    rows = []
    for rank, row in enumerate(top25, start=1):
        age = demography[row["code_departement"]]
        mal_estimated = row["part_mal_inscrits"] * row["inscrits"]
        localized = localized_young_estimate(age)
        school = int(age["population_scolarisee_18_24"]) + int(age["population_scolarisee_25_29"])
        population_18_29 = int(age["population_18_24"]) + int(age["population_25_29"])
        rows.append(
            {
                "rank": rank,
                "name": row["libelle_departement"],
                "mal_estimated": mal_estimated,
                "young_localized": localized,
                "young_legacy": mal_estimated * LEGACY_RATE_18_34,
                "school": school,
                "school_share": school / population_18_29,
                "mal_share": row["part_mal_inscrits"],
                "nupes_share": row["part_nupes_exprimes"],
                "score": row["score_croise"],
                "inscrits": row["inscrits"],
            }
        )
    return rows


def markdown_table(rows):
    total_mal = sum(row["mal_estimated"] for row in rows)
    total_inscrits = sum(row["inscrits"] for row in rows)
    total_school = sum(row["school"] for row in rows)
    total_population_18_29 = 0
    demography = read_csv(DEMOGRAPHY_CSV)
    for row in rows:
        age = next(item for item in demography.values() if item["libelle_departement"] == row["name"])
        total_population_18_29 += int(age["population_18_24"]) + int(age["population_25_29"])

    lines = [
        "# Top 25 des départements mal-inscription x vote NUPES au second tour des législatives 2022",
        "",
        "Classement selon la moyenne géométrique des rangs percentiles de mal-inscription et de vote NUPES au second tour :",
        "",
        "`score_croise = sqrt(score_mal_inscription * score_nupes)`",
        "",
        "Les voix et pourcentages NUPES T2 utilisent les totaux de coalition Wikipédia quand ils sont disponibles, avec les agrégats ministériels conservés comme contrôle.",
        "",
        "| Rang | Département | Mal-inscrits estimés | 18-34 ans estimés, méthode territorialisée | 18-34 ans estimés, ancienne méthode uniforme 52 % | Population scolarisée 18-29 ans | Part scolarisée des 18-29 ans | Mal-inscrits | Vote NUPES T2 | Score croisé |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        score = f"{row['score']:.3f}".replace(".", ",")
        lines.append(
            f"| {row['rank']} | {row['name']} | {format_int(row['mal_estimated'])} "
            f"| {format_int(row['young_localized'])} "
            f"| {format_int(row['young_legacy'])} "
            f"| {format_int(row['school'])} "
            f"| {format_pct(row['school_share'])} "
            f"| {format_pct(row['mal_share'])} "
            f"| {format_pct(row['nupes_share'], 2)} "
            f"| {score} |"
        )
    lines.extend(
        [
            f"| **Total top 25** | **25 départements** | **{format_int(total_mal)}** "
            f"| **{format_int(sum(row['young_localized'] for row in rows))}** "
            f"| **{format_int(sum(row['young_legacy'] for row in rows))}** "
            f"| **{format_int(total_school)}** "
            f"| **{format_pct(total_school / total_population_18_29)}** "
            f"| **{format_pct(total_mal / total_inscrits)}** | **n.d.** | **-** |",
            "",
            "## Méthodes et limites",
            "",
            "`part départementale Insee × inscrits électoraux aux législatives 2022 T2`.",
            "",
            "Sources : Insee Première n°1986, figures 3 et 4 ; Insee RP2022 ; Wikipédia, pages départementales des législatives 2022 ; ministère de l'Intérieur via Hexagonal, législatives 2022 T2.",
        ]
    )
    return "\n".join(lines)


def markdown_to_html(markdown):
    lines = markdown.splitlines()
    title = lines[0].lstrip("# ")
    paragraphs = []
    table_lines = []
    in_table = False
    for line in lines[2:]:
        if line.startswith("|"):
            in_table = True
            table_lines.append(line)
        elif in_table:
            in_table = False
            if table_lines:
                paragraphs.append(("table", table_lines))
                table_lines = []
            if line:
                paragraphs.append(("p", line))
        elif line.startswith("## "):
            paragraphs.append(("h2", line[3:]))
        elif line:
            paragraphs.append(("p", line))
    if table_lines:
        paragraphs.append(("table", table_lines))

    body = [f"<h1>{html.escape(title)}</h1>"]
    for kind, value in paragraphs:
        if kind == "h2":
            body.append(f"<h2>{html.escape(value)}</h2>")
        elif kind == "p":
            body.append(f"<p>{html.escape(value)}</p>")
        else:
            headers = [cell.strip() for cell in value[0].strip("|").split("|")]
            rows = value[2:]
            body.append('<div class="table-wrap"><table><thead><tr>')
            body.extend(f"<th>{html.escape(header)}</th>" for header in headers)
            body.append("</tr></thead><tbody>")
            for row in rows:
                cells = [cell.strip().replace("**", "") for cell in row.strip("|").split("|")]
                body.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>")
            body.append("</tbody></table></div>")

    return """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Top 25 mal-inscription x NUPES T2 2022</title><style>:root{color-scheme:light;--ink:#1f2529;--line:#d9dddf;--paper:#fff;--wash:#f5f6f3}*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1280px;margin:0 auto;padding:28px 22px 48px}h1{margin:0 0 16px;font-size:28px;line-height:1.15;letter-spacing:0}h2{margin:30px 0 12px;font-size:21px;letter-spacing:0}p{color:#374047;line-height:1.55}.table-wrap{overflow:auto;margin:18px 0 28px;border:1px solid var(--line);background:var(--paper)}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px 10px;border-bottom:1px solid #eceeef;text-align:right;vertical-align:top;white-space:nowrap}th{background:#eef3f5;color:#263138;font-weight:700;position:sticky;top:0;z-index:1}th:nth-child(2),td:nth-child(2){text-align:left;min-width:190px}tr:hover td{background:#fafafa}code{background:#eef1f2;padding:2px 5px;border-radius:4px}</style></head><body><main>""" + "".join(body) + "</main></body></html>"


def main():
    top25 = load_top25()
    demography = ensure_demography(top25)
    rows = build_rows(top25, demography)
    markdown = markdown_table(rows)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    OUTPUT_HTML.write_text(markdown_to_html(markdown), encoding="utf-8")
    print(f"Tableau Markdown : {OUTPUT_MD}")
    print(f"Tableau HTML : {OUTPUT_HTML}")
    print(f"Données Insee : {DEMOGRAPHY_CSV}")


if __name__ == "__main__":
    main()
