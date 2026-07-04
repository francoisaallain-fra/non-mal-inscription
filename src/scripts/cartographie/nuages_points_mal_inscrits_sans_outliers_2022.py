import html
import math
from pathlib import Path

import nuage_points_mal_inscrits_melenchon_2022 as melenchon
import nuage_points_mal_inscrits_nupes_2022 as nupes


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_NUPES = (
    ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-departements-sans-outliers.html"
)
OUTPUT_MELENCHON = (
    ROOT
    / "maps/2022-nuage-points-mal-inscrits-melenchon-departements-sans-outliers.html"
)


def quantile(values, q):
    values = sorted(values)
    position = (len(values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def split_outliers(rows, x_key):
    xs = [row[x_key] for row in rows]
    ys = [row["mal"] for row in rows]
    x_q1, x_q3 = quantile(xs, 0.25), quantile(xs, 0.75)
    y_q1, y_q3 = quantile(ys, 0.25), quantile(ys, 0.75)
    x_iqr = x_q3 - x_q1
    y_iqr = y_q3 - y_q1
    x_min, x_max = x_q1 - 1.5 * x_iqr, x_q3 + 1.5 * x_iqr
    y_min, y_max = y_q1 - 1.5 * y_iqr, y_q3 + 1.5 * y_iqr

    kept = []
    excluded = []
    for row in rows:
        if row[x_key] < x_min or row[x_key] > x_max or row["mal"] < y_min or row["mal"] > y_max:
            excluded.append(row)
        else:
            kept.append(row)
    return kept, excluded


def format_excluded(excluded, x_key):
    return ", ".join(
        f"{row['nom']} ({row['code']}, vote {row[x_key]:.1f} %, mal-inscrits {row['mal']:.1f} %)"
        for row in sorted(excluded, key=lambda row: row["code"])
    )


def add_outlier_note(content, excluded, x_key):
    note = (
        '<p class="note">'
        "Version sans outliers : exclusion par règle IQR 1,5 sur les deux axes "
        "(vote et part de mal-inscrits). "
        f"Départements exclus : {html.escape(format_excluded(excluded, x_key))}."
        "</p>"
    )
    return content.replace("</aside>", f"      {note}\n    </aside>")


def write_filtered(label, module, output_path, x_key):
    rows = module.load_rows()
    kept, excluded = split_outliers(rows, x_key)
    content = module.build_html(kept)
    content = add_outlier_note(content, excluded, x_key)
    if label == "NUPES":
        content = content.replace(
            "Nuage de points mal-inscription x vote NUPES en 2022",
            "Nuage de points mal-inscription x vote NUPES en 2022 - sans outliers",
        ).replace(
            "Mal-inscription et vote NUPES au premier tour des législatives de 2022",
            "Mal-inscription et vote NUPES au premier tour des législatives de 2022 - sans outliers",
        )
    else:
        content = content.replace(
            "Nuage de points mal-inscription x vote Mélenchon en 2022",
            "Nuage de points mal-inscription x vote Mélenchon en 2022 - sans outliers",
        ).replace(
            "Mal-inscription et vote Mélenchon au premier tour de la présidentielle de 2022",
            "Mal-inscription et vote Mélenchon au premier tour de la présidentielle de 2022 - sans outliers",
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    xs = [row[x_key] for row in kept]
    ys = [row["mal"] for row in kept]
    pearson = module.correlation(xs, ys)
    spearman = module.correlation(module.average_ranks(xs), module.average_ranks(ys))
    print(f"{label}: {len(kept)} départements conservés, {len(excluded)} exclus")
    print(f"{label}: Pearson {pearson:.6f}, Spearman {spearman:.6f}")
    print(f"{label}: exclus - {format_excluded(excluded, x_key)}")
    print(f"{label}: {output_path}")


def main():
    write_filtered("NUPES", nupes, OUTPUT_NUPES, "nupes")
    write_filtered("Mélenchon", melenchon, OUTPUT_MELENCHON, "melenchon")


if __name__ == "__main__":
    main()
