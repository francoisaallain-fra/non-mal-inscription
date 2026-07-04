import csv
import html
import json
from pathlib import Path

import nuage_points_mal_inscrits_nupes_2022 as nupes
from cartes_departements_mal_inscrits_nupes_2022 import map_html
from construire_tableau_top25_mal_inscrits_nupes_2022 import (
    LEGACY_RATE_18_34,
    format_int,
    format_pct,
    localized_young_estimate,
)
from nuages_points_mal_inscrits_bulles_sans_outliers_2022 import (
    build_html as build_bubble_html,
    normalize_rows,
)
from nuages_points_mal_inscrits_sans_outliers_2022 import (
    add_outlier_note,
    format_excluded,
    split_outliers,
)


ROOT = Path(__file__).resolve().parents[3]
GEOJSON_T1 = (
    ROOT / "data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson"
)
DEMOGRAPHY_CSV = (
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-nupes-t1-top25.csv"
)
DEMOGRAPHY_FALLBACKS = [
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-top25.csv",
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-nupes-t2-top25.csv",
    ROOT / "data/04_analysis/insee/2022-age-scolarisation-departements-melenchon-top25.csv",
]

OUTPUT_SCATTER = (
    ROOT / "maps/2022-nuage-points-mal-inscrits-nupes-t1-departements.html"
)
OUTPUT_SCATTER_FILTERED = (
    ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-t1-departements-sans-outliers.html"
)
OUTPUT_SCATTER_BUBBLES = (
    ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-t1-departements-bulles-sans-outliers.html"
)
OUTPUT_MAP = ROOT / "maps/2022-croisement-mal-inscrits-nupes-departements-t1.html"
OUTPUT_MD = ROOT / "top-25-departements-mal-inscrits-nupes-t1-2022.md"
OUTPUT_TABLE_HTML = ROOT / "maps/2022-tableau-top25-mal-inscrits-nupes-t1.html"


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


def load_rows():
    original = nupes.INPUT_GEOJSON
    nupes.INPUT_GEOJSON = GEOJSON_T1
    try:
        return nupes.load_rows()
    finally:
        nupes.INPUT_GEOJSON = original


def t1_labels(content):
    return (
        content.replace(
            "Nuage de points mal-inscription x vote NUPES au second tour des législatives de 2022",
            "Nuage de points mal-inscription x vote NUPES au premier tour des législatives de 2022",
        )
        .replace(
            "Mal-inscription et vote NUPES au second tour des législatives de 2022",
            "Mal-inscription et vote NUPES au premier tour des législatives de 2022",
        )
        .replace("législatives 2022 T2", "législatives 2022 T1")
    )


def write_scatter(rows):
    content = t1_labels(nupes.build_html(rows))
    OUTPUT_SCATTER.write_text(content, encoding="utf-8")
    xs = [row["nupes"] for row in rows]
    ys = [row["mal"] for row in rows]
    print(f"NUPES T1 complet : {len(rows)} départements")
    print(f"NUPES T1 complet : Pearson {nupes.correlation(xs, ys):.6f}")
    print(
        "NUPES T1 complet : Spearman "
        f"{nupes.correlation(nupes.average_ranks(xs), nupes.average_ranks(ys)):.6f}"
    )
    print(f"NUPES T1 complet : {OUTPUT_SCATTER}")


def write_filtered_scatter(rows):
    kept, excluded = split_outliers(rows, "nupes")
    content = t1_labels(nupes.build_html(kept))
    content = add_outlier_note(content, excluded, "nupes")
    content = content.replace(
        "premier tour des législatives de 2022",
        "premier tour des législatives de 2022 - sans outliers",
    )
    OUTPUT_SCATTER_FILTERED.write_text(content, encoding="utf-8")
    xs = [row["nupes"] for row in kept]
    ys = [row["mal"] for row in kept]
    print(f"NUPES T1 sans outliers : {len(kept)} conservés, {len(excluded)} exclus")
    print(f"NUPES T1 sans outliers : Pearson {nupes.correlation(xs, ys):.6f}")
    print(
        "NUPES T1 sans outliers : Spearman "
        f"{nupes.correlation(nupes.average_ranks(xs), nupes.average_ranks(ys)):.6f}"
    )
    print(f"NUPES T1 sans outliers : exclus - {format_excluded(excluded, 'nupes')}")
    print(f"NUPES T1 sans outliers : {OUTPUT_SCATTER_FILTERED}")
    return kept, excluded


def write_bubble_scatter(rows):
    kept, excluded = split_outliers(rows, "nupes")
    normalized = normalize_rows(kept, "nupes", "voix_nupes")
    xs = [row["x"] for row in normalized]
    ys = [row["mal"] for row in normalized]
    pearson = nupes.correlation(xs, ys)
    spearman = nupes.correlation(nupes.average_ranks(xs), nupes.average_ranks(ys))
    OUTPUT_SCATTER_BUBBLES.write_text(
        build_bubble_html(
            normalized,
            excluded,
            "nupes",
            "NUPES",
            "Mal-inscription et vote NUPES au premier tour des législatives 2022 - bulles sans outliers",
            "Sources : Insee Première n°1986, figure 4 ; Wikipédia, pages départementales des législatives 2022, avec agrégats du ministère de l'Intérieur via Hexagonal conservés comme contrôle. Volume : part Insee de mal-inscrits × inscrits législatives 2022 T1.",
            pearson,
            spearman,
        ),
        encoding="utf-8",
    )
    print(f"NUPES T1 bulles : Pearson {pearson:.6f}, Spearman {spearman:.6f}")
    print(f"NUPES T1 bulles : {OUTPUT_SCATTER_BUBBLES}")


def write_map():
    geojson = json.loads(GEOJSON_T1.read_text(encoding="utf-8"))
    OUTPUT_MAP.write_text(
        map_html(
            geojson,
            "cross",
            "Croisement mal-inscription x vote NUPES en 2022 - premier tour coalition contrôlée",
            "Vote NUPES au premier tour des législatives 2022, total de coalition Wikipédia.",
            "Moyenne géométrique des rangs de mal-inscription et de vote NUPES au premier tour",
            "Mal-inscription : INSEE Première n°1986, Figure 4. Vote NUPES T1 : totaux de coalition Wikipédia ; agrégats du ministère de l'Intérieur via Hexagonal conservés comme contrôle.",
        ),
        encoding="utf-8",
    )
    print(f"Carte NUPES T1 : {OUTPUT_MAP}")


def load_top25():
    data = json.loads(GEOJSON_T1.read_text(encoding="utf-8"))
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


def build_table_rows(top25, demography):
    rows = []
    for rank, row in enumerate(top25, start=1):
        age = demography[row["code_departement"]]
        mal_estimated = row["part_mal_inscrits"] * row["inscrits"]
        school = int(age["population_scolarisee_18_24"]) + int(
            age["population_scolarisee_25_29"]
        )
        population_18_29 = int(age["population_18_24"]) + int(age["population_25_29"])
        rows.append(
            {
                "rank": rank,
                "code": row["code_departement"],
                "name": row["libelle_departement"],
                "mal_estimated": mal_estimated,
                "young_localized": localized_young_estimate(age),
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


def markdown_table(rows, demography):
    total_mal = sum(row["mal_estimated"] for row in rows)
    total_inscrits = sum(row["inscrits"] for row in rows)
    total_school = sum(row["school"] for row in rows)
    total_population_18_29 = sum(
        int(demography[row["code"]]["population_18_24"])
        + int(demography[row["code"]]["population_25_29"])
        for row in rows
    )
    lines = [
        "# Top 25 des départements mal-inscription x vote NUPES au premier tour des législatives 2022",
        "",
        "Classement selon la moyenne géométrique des rangs percentiles de mal-inscription et de vote NUPES au premier tour :",
        "",
        "`score_croise = sqrt(score_mal_inscription * score_nupes)`",
        "",
        "Les voix et pourcentages NUPES T1 utilisent les totaux de coalition Wikipédia, avec les agrégats ministériels conservés comme contrôle.",
        "",
        "| Rang | Département | Mal-inscrits estimés | 18-34 ans estimés, méthode territorialisée | 18-34 ans estimés, ancienne méthode uniforme 52 % | Population scolarisée 18-29 ans | Part scolarisée des 18-29 ans | Mal-inscrits | Vote NUPES T1 | Score croisé |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['rank']} | {row['name']} | {format_int(row['mal_estimated'])} "
            f"| {format_int(row['young_localized'])} "
            f"| {format_int(row['young_legacy'])} "
            f"| {format_int(row['school'])} "
            f"| {format_pct(row['school_share'])} "
            f"| {format_pct(row['mal_share'])} "
            f"| {format_pct(row['nupes_share'], 2)} "
            f"| {str(round(row['score'], 3)).replace('.', ',')} |"
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
            "`part départementale Insee × inscrits électoraux aux législatives 2022 T1`.",
            "",
            "Sources : Insee Première n°1986, figures 3 et 4 ; Insee RP2022 ; Wikipédia, pages départementales des législatives 2022 ; ministère de l'Intérieur via Hexagonal, législatives 2022 T1.",
        ]
    )
    return "\n".join(lines)


def markdown_to_html(markdown):
    lines = markdown.splitlines()
    title = lines[0].lstrip("# ")
    body = [f"<h1>{html.escape(title)}</h1>"]
    table_lines = []
    in_table = False
    for line in lines[2:]:
        if line.startswith("|"):
            in_table = True
            table_lines.append(line)
            continue
        if in_table:
            body.append(render_table(table_lines))
            table_lines = []
            in_table = False
        if line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line:
            body.append(f"<p>{html.escape(line)}</p>")
    if table_lines:
        body.append(render_table(table_lines))
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Top 25 mal-inscription x NUPES T1 2022</title>"
        "<style>:root{color-scheme:light;--ink:#1f2529;--line:#d9dddf;--paper:#fff;--wash:#f5f6f3}"
        "*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}"
        "main{max-width:1280px;margin:0 auto;padding:28px 22px 48px}h1{margin:0 0 16px;font-size:28px;line-height:1.15;letter-spacing:0}"
        "h2{margin:30px 0 12px;font-size:21px;letter-spacing:0}p{color:#374047;line-height:1.55}"
        ".table-wrap{overflow:auto;margin:18px 0 28px;border:1px solid var(--line);background:var(--paper)}"
        "table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px 10px;border-bottom:1px solid #eceeef;text-align:right;vertical-align:top;white-space:nowrap}"
        "th{background:#eef3f5;color:#263138;font-weight:700;position:sticky;top:0;z-index:1}th:nth-child(2),td:nth-child(2){text-align:left;min-width:190px}"
        "tr:hover td{background:#fafafa}code{background:#eef1f2;padding:2px 5px;border-radius:4px}</style></head><body><main>"
        + "".join(body)
        + "</main></body></html>"
    )


def render_table(lines):
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = lines[2:]
    html_rows = ['<div class="table-wrap"><table><thead><tr>']
    html_rows.extend(f"<th>{html.escape(header)}</th>" for header in headers)
    html_rows.append("</tr></thead><tbody>")
    for row in rows:
        cells = [cell.strip().replace("**", "") for cell in row.strip("|").split("|")]
        html_rows.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>")
    html_rows.append("</tbody></table></div>")
    return "".join(html_rows)


def write_table():
    top25 = load_top25()
    demography = ensure_demography(top25)
    rows = build_table_rows(top25, demography)
    markdown = markdown_table(rows, demography)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    OUTPUT_TABLE_HTML.write_text(markdown_to_html(markdown), encoding="utf-8")
    print(f"Tableau NUPES T1 Markdown : {OUTPUT_MD}")
    print(f"Tableau NUPES T1 HTML : {OUTPUT_TABLE_HTML}")


def main():
    rows = load_rows()
    write_scatter(rows)
    write_filtered_scatter(rows)
    write_bubble_scatter(rows)
    write_map()
    write_table()


if __name__ == "__main__":
    main()
