#!/usr/bin/env python3
"""Build first-pass participation loss tables for presidential/legislative cycles."""

from __future__ import annotations

import csv
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_DATA = ROOT / "data/04_analysis/participation"
OUT_ANALYSIS = ROOT / "analyses/deperdition-jeunes-2002-2022"


GLOBAL_TURNOUT = [
    {
        "annee": 2002,
        "couple_scrutin": "pres. 2002 / leg. 2002",
        "presidentielle_t1": 71.60,
        "presidentielle_t2": 79.71,
        "legislatives_t1": 64.42,
        "legislatives_t2": 60.32,
        "source": "Ministere de l'Interieur, resultats nationaux; synthese controlee via https://fr.wikipedia.org/wiki/Abstention_de_vote_en_France",
    },
    {
        "annee": 2007,
        "couple_scrutin": "pres. 2007 / leg. 2007",
        "presidentielle_t1": 83.77,
        "presidentielle_t2": 83.97,
        "legislatives_t1": 60.44,
        "legislatives_t2": 59.99,
        "source": "Ministere de l'Interieur, resultats nationaux; synthese controlee via https://fr.wikipedia.org/wiki/Abstention_de_vote_en_France",
    },
    {
        "annee": 2012,
        "couple_scrutin": "pres. 2012 / leg. 2012",
        "presidentielle_t1": 79.48,
        "presidentielle_t2": 80.35,
        "legislatives_t1": 57.22,
        "legislatives_t2": 55.40,
        "source": "Ministere de l'Interieur, resultats nationaux; synthese controlee via https://fr.wikipedia.org/wiki/Abstention_de_vote_en_France",
    },
    {
        "annee": 2017,
        "couple_scrutin": "pres. 2017 / leg. 2017",
        "presidentielle_t1": 77.77,
        "presidentielle_t2": 74.56,
        "legislatives_t1": 48.70,
        "legislatives_t2": 42.64,
        "source": "Ministere de l'Interieur, resultats nationaux; Insee Premiere 1670 pour l'intermittence",
    },
    {
        "annee": 2022,
        "couple_scrutin": "pres. 2022 / leg. 2022",
        "presidentielle_t1": 73.69,
        "presidentielle_t2": 71.99,
        "legislatives_t1": 47.51,
        "legislatives_t2": 46.23,
        "source": "Ministere de l'Interieur, resultats nationaux; Insee Premiere 1928 pour l'intermittence",
    },
    {
        "annee": 2024,
        "couple_scrutin": "pres. 2022 / leg. 2024",
        "presidentielle_t1": 73.69,
        "presidentielle_t2": 71.99,
        "legislatives_t1": 66.71,
        "legislatives_t2": 66.63,
        "source": "Ministere de l'Interieur, resultats nationaux; legislatives 2024 decouplees de la presidentielle",
    },
]


# Published Insee 2017 age table, figure 2 and figure 3.
# Values are percentages of registered voters in each age band.
INSEE_2017_AGE = [
    {
        "annee": 2017,
        "classe_age": "18-24",
        "vote_systematique": 17.7,
        "vote_intermitent": 62.1,
        "abstention_systematique": 20.2,
        "deux_votes_uniquement_presidentielle": 31.1,
        "tout_sauf_legislatives_t2": 8.9,
        "tout_sauf_legislatives_t1": 4.8,
        "seul_t1_presidentielle": 8.1,
        "seul_t2_presidentielle": 5.1,
        "vote_intermitent_autre": 4.1,
        "source": "Insee Premiere 1670, figures 2 et 3, https://www.insee.fr/fr/statistiques/3138704",
    },
    {
        "annee": 2017,
        "classe_age": "25-29",
        "vote_systematique": 16.5,
        "vote_intermitent": 59.3,
        "abstention_systematique": 24.2,
        "deux_votes_uniquement_presidentielle": 28.1,
        "tout_sauf_legislatives_t2": 9.5,
        "tout_sauf_legislatives_t1": 3.8,
        "seul_t1_presidentielle": 7.5,
        "seul_t2_presidentielle": 4.7,
        "vote_intermitent_autre": 5.6,
        "source": "Insee Premiere 1670, figures 2 et 3, https://www.insee.fr/fr/statistiques/3138704",
    },
    {
        "annee": 2017,
        "classe_age": "30-34",
        "vote_systematique": 23.0,
        "vote_intermitent": 58.7,
        "abstention_systematique": 18.3,
        "deux_votes_uniquement_presidentielle": 28.8,
        "tout_sauf_legislatives_t2": 11.0,
        "tout_sauf_legislatives_t1": 4.4,
        "seul_t1_presidentielle": 6.7,
        "seul_t2_presidentielle": 3.4,
        "vote_intermitent_autre": 4.5,
        "source": "Insee Premiere 1670, figures 2 et 3, https://www.insee.fr/fr/statistiques/3138704",
    },
]


INSEE_AGE_LONG = {
    2002: {
        "18-24": {"vote_systematique": 32.4, "vote_intermitent": 53.8, "abstention_systematique": 13.9},
        "25-29": {"vote_systematique": 30.0, "vote_intermitent": 51.0, "abstention_systematique": 18.9},
        "30-34": {"vote_systematique": 35.3, "vote_intermitent": 48.7, "abstention_systematique": 16.1},
    },
    2007: {
        "18-24": {"vote_systematique": 31.3, "vote_intermitent": 57.9, "abstention_systematique": 10.8},
        "25-29": {"vote_systematique": 30.1, "vote_intermitent": 58.9, "abstention_systematique": 11.0},
        "30-34": {"vote_systematique": 37.7, "vote_intermitent": 53.3, "abstention_systematique": 9.0},
    },
    2012: {
        "18-24": {"vote_systematique": 25.9, "vote_intermitent": 57.5, "abstention_systematique": 16.6},
        "25-29": {"vote_systematique": 27.9, "vote_intermitent": 55.3, "abstention_systematique": 16.8},
        "30-34": {"vote_systematique": 34.3, "vote_intermitent": 52.9, "abstention_systematique": 12.9},
    },
    2017: {
        "18-24": {"vote_systematique": 18.0, "vote_intermitent": 62.7, "abstention_systematique": 19.4},
        "25-29": {"vote_systematique": 16.7, "vote_intermitent": 59.4, "abstention_systematique": 23.9},
        "30-34": {"vote_systematique": 23.2, "vote_intermitent": 59.0, "abstention_systematique": 17.8},
    },
}


INSEE_INTERMITTENT_DETAIL = {
    2002: {
        "deux_votes_uniquement_presidentielle": 8.8,
        "tout_sauf_legislatives_t2": 8.3,
        "tout_sauf_legislatives_t1": 4.9,
        "seul_t1_presidentielle": 1.6,
        "seul_t2_presidentielle": 4.5,
        "tout_sauf_presidentielle_t2": 1.7,
        "tout_sauf_presidentielle_t1": 4.6,
        "vote_intermitent_autre": 5.7,
    },
    2007: {
        "deux_votes_uniquement_presidentielle": 17.6,
        "tout_sauf_legislatives_t2": 7.1,
        "tout_sauf_legislatives_t1": 6.4,
        "seul_t1_presidentielle": 2.8,
        "seul_t2_presidentielle": 2.2,
        "tout_sauf_presidentielle_t2": 1.1,
        "tout_sauf_presidentielle_t1": 1.2,
        "vote_intermitent_autre": 2.1,
    },
    2012: {
        "deux_votes_uniquement_presidentielle": 15.5,
        "tout_sauf_legislatives_t2": 8.0,
        "tout_sauf_legislatives_t1": 6.5,
        "seul_t1_presidentielle": 2.8,
        "seul_t2_presidentielle": 2.9,
        "tout_sauf_presidentielle_t2": 1.1,
        "tout_sauf_presidentielle_t1": 1.7,
        "vote_intermitent_autre": 2.8,
    },
    2017: {
        "deux_votes_uniquement_presidentielle": 20.5,
        "tout_sauf_legislatives_t2": 11.4,
        "tout_sauf_legislatives_t1": 5.6,
        "seul_t1_presidentielle": 4.6,
        "seul_t2_presidentielle": 2.7,
        "tout_sauf_presidentielle_t2": 1.6,
        "tout_sauf_presidentielle_t1": 1.0,
        "vote_intermitent_autre": 3.4,
    },
}


# Published Insee 2022 statement for registered voters under 30.
# This is the cleanest directly published age class for 2022 found in the
# immediate literature, so it is treated as the robustness class.
INSEE_2022_UNDER30 = {
    "annee": 2022,
    "classe_age": "moins de 30 ans",
    "participation_au_moins_une_fois_presidentielle": 74.0,
    "participation_au_moins_une_fois_legislatives": 35.0,
    "source": "Insee Premiere 1928, cite dans https://fr.wikipedia.org/wiki/Abstention_de_vote_en_France",
}


def r1(value: float) -> float:
    return round(value, 1)


def r2(value: float) -> float:
    return round(value, 2)


def avg(values: list[float]) -> float:
    return sum(values) / len(values)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def average_age_bands(year: int, bands: list[str]) -> dict:
    keys = ["vote_systematique", "vote_intermitent", "abstention_systematique"]
    return {
        key: avg([INSEE_AGE_LONG[year][band][key] for band in bands])
        for key in keys
    }


def scale_intermittent_detail(year: int, intermittent_rate: float) -> dict:
    detail = INSEE_INTERMITTENT_DETAIL[year]
    total = sum(detail.values())
    return {key: intermittent_rate * value / total for key, value in detail.items()}


def age_estimate_from_public_tables(
    year: int, classe_age: str, bands: list[str], method_label: str
) -> dict:
    age = average_age_bands(year, bands)
    detail = scale_intermittent_detail(year, age["vote_intermitent"])
    sys = age["vote_systematique"]
    pres_only = detail["deux_votes_uniquement_presidentielle"]
    no_l2 = detail["tout_sauf_legislatives_t2"]
    no_l1 = detail["tout_sauf_legislatives_t1"]
    p1_only = detail["seul_t1_presidentielle"]
    p2_only = detail["seul_t2_presidentielle"]
    no_p2 = detail["tout_sauf_presidentielle_t2"]
    no_p1 = detail["tout_sauf_presidentielle_t1"]
    other = detail["vote_intermitent_autre"]
    pres_t1 = sys + pres_only + no_l2 + no_l1 + p1_only + no_p2
    pres_t2 = sys + pres_only + no_l2 + no_l1 + p2_only + no_p1
    leg_t1 = sys + no_l2 + no_p2 + no_p1
    leg_t2 = sys + no_l1 + no_p2 + no_p1
    return {
        "annee": year,
        "classe_age": classe_age,
        "presidentielle_t1": r1(pres_t1),
        "legislatives_t1": r1(leg_t1),
        "deperdition_t1": r1(pres_t1 - leg_t1),
        "incertitude_t1": r1(other),
        "presidentielle_t2": r1(pres_t2),
        "legislatives_t2": r1(leg_t2),
        "deperdition_t2": r1(pres_t2 - leg_t2),
        "incertitude_t2": r1(other),
        "deperdition_au_moins_un_tour": r1(pres_only + p1_only + p2_only),
        "vote_systematique": r1(age["vote_systematique"]),
        "vote_intermitent": r1(age["vote_intermitent"]),
        "abstention_systematique": r1(age["abstention_systematique"]),
        "methode": method_label,
        "methode_classe": "method-public-estimate",
        "source": "Insee Premiere 1671, figures 2 et 3; composition intermittence nationale appliquee a la classe d'age",
    }


def build_global_rows() -> list[dict]:
    rows = []
    for row in GLOBAL_TURNOUT:
        pres_mean = (row["presidentielle_t1"] + row["presidentielle_t2"]) / 2
        leg_mean = (row["legislatives_t1"] + row["legislatives_t2"]) / 2
        rows.append(
            {
                **row,
                "deperdition_t1": r2(row["presidentielle_t1"] - row["legislatives_t1"]),
                "deperdition_t2": r2(row["presidentielle_t2"] - row["legislatives_t2"]),
                "participation_moyenne_presidentielle": r2(pres_mean),
                "participation_moyenne_legislatives": r2(leg_mean),
                "deperdition_moyenne_tours": r2(pres_mean - leg_mean),
                "ratio_retention_moyen_leg_sur_pres": r2(leg_mean / pres_mean),
            }
        )
    return rows


def add_age_deperdition_to_global_rows(
    global_rows: list[dict], youth_rows: list[dict]
) -> list[dict]:
    rows_18_29 = {row["annee"]: row for row in build_18_29_public_rows()}
    rows_18_34 = {row["annee"]: row for row in build_18_34_rows()}
    youth_turnout_rows = build_youth_turnout_rows(youth_rows)
    by_year = {}
    for row in youth_turnout_rows:
        if row["classe_age"] == "18-34 approx. non pondere":
            by_year[row["annee"]] = {
                "classe_age_deperdition": row["classe_age"],
                "deperdition_age_t1": row["deperdition_age_t1_connue"],
                "deperdition_age_t2": row["deperdition_age_t2_connue"],
                "deperdition_age_au_moins_un_tour": "",
                "statut_deperdition_age": row["statut"],
            }
        elif row["classe_age"] == "moins de 30 ans":
            by_year[row["annee"]] = {
                "classe_age_deperdition": row["classe_age"],
                "deperdition_age_t1": "",
                "deperdition_age_t2": "",
                "deperdition_age_au_moins_un_tour": row[
                    "deperdition_pres_leg_au_moins_un_tour"
                ],
                "statut_deperdition_age": row["statut"],
            }

    enriched = []
    for row in global_rows:
        row_18_29 = rows_18_29.get(row["annee"], {})
        row_18_34 = rows_18_34.get(row["annee"], {})
        methode_classe = (
            row_18_29.get("methode_classe")
            or row_18_34.get("methode_classe")
            or ""
        )
        age_data = by_year.get(
            row["annee"],
            {
                "classe_age_deperdition": "",
                "deperdition_age_t1": "",
                "deperdition_age_t2": "",
                "deperdition_age_au_moins_un_tour": "",
                "statut_deperdition_age": "non calcule",
            },
        )
        enriched.append(
            {
                **row,
                **age_data,
                "deperdition_18_29_t1": row_18_29.get("deperdition_t1", ""),
                "deperdition_18_29_t2": row_18_29.get("deperdition_t2", ""),
                "deperdition_18_29_au_moins_un_tour": (
                    f'{row_18_29.get("deperdition_au_moins_un_tour")}*'
                    if row["annee"] == 2022
                    else row_18_29.get("deperdition_au_moins_un_tour", "")
                ),
                "methode_18_29": row_18_29.get("methode", ""),
                "deperdition_18_34_t1": row_18_34.get("deperdition_t1", ""),
                "deperdition_18_34_t2": row_18_34.get("deperdition_t2", ""),
                "deperdition_18_34_au_moins_un_tour": row_18_34.get(
                    "deperdition_au_moins_un_tour", ""
                ),
                "participation_legislatives_2024_18_34": row_18_34.get(
                    "participation_legislatives_2024", ""
                ),
                "methode_18_34": row_18_34.get("methode", ""),
                "methode_classe": methode_classe,
            }
        )
    return enriched


def build_youth_rows() -> list[dict]:
    rows = []
    for row in INSEE_2017_AGE:
        strict_pres_no_leg = (
            row["deux_votes_uniquement_presidentielle"]
            + row["seul_t1_presidentielle"]
            + row["seul_t2_presidentielle"]
        )
        rows.append(
            {
                **row,
                "indicateur_strict_presidentielle_sans_legislatives": r1(strict_pres_no_leg),
                "nature_indicateur": (
                    "Part des inscrits ayant vote a au moins un tour de presidentielle "
                    "et a aucun tour des legislatives, hors categories residuelles de la figure 3."
                ),
            }
        )

    row = INSEE_2022_UNDER30
    rows.append(
        {
            **row,
            "vote_systematique": "",
            "vote_intermitent": "",
            "abstention_systematique": "",
            "deux_votes_uniquement_presidentielle": "",
            "seul_t1_presidentielle": "",
            "seul_t2_presidentielle": "",
            "indicateur_strict_presidentielle_sans_legislatives": r1(
                row["participation_au_moins_une_fois_presidentielle"]
                - row["participation_au_moins_une_fois_legislatives"]
            ),
            "nature_indicateur": (
                "Ecart direct entre participation a au moins un tour de presidentielle "
                "et participation a au moins un tour des legislatives."
            ),
        }
    )
    return rows


def build_youth_turnout_rows(youth_rows: list[dict]) -> list[dict]:
    rows = []
    source_rows = [row for row in INSEE_2017_AGE]
    for row in source_rows:
        sys = row["vote_systematique"]
        pres_only = row["deux_votes_uniquement_presidentielle"]
        no_l2 = row["tout_sauf_legislatives_t2"]
        no_l1 = row["tout_sauf_legislatives_t1"]
        p1_only = row["seul_t1_presidentielle"]
        p2_only = row["seul_t2_presidentielle"]
        other = row["vote_intermitent_autre"]
        pres_t1_known = sys + pres_only + no_l2 + no_l1 + p1_only
        pres_t2_known = sys + pres_only + no_l2 + no_l1 + p2_only
        leg_t1_known = sys + no_l2
        leg_t2_known = sys + no_l1
        rows.append(
            {
                "annee": 2017,
                "classe_age": row["classe_age"],
                "presidentielle_t1_connue": r1(pres_t1_known),
                "legislatives_t1_connue": r1(leg_t1_known),
                "deperdition_age_t1_connue": r1(pres_t1_known - leg_t1_known),
                "incertitude_max_points_t1": r1(other),
                "presidentielle_t2_connue": r1(pres_t2_known),
                "legislatives_t2_connue": r1(leg_t2_known),
                "deperdition_age_t2_connue": r1(pres_t2_known - leg_t2_known),
                "incertitude_max_points_t2": r1(other),
                "statut": "reconstitution publique avec fourchette",
                "source": row["source"],
            }
        )

    bands = [row for row in rows if row["annee"] == 2017]
    avg_keys = [
        "presidentielle_t1_connue",
        "legislatives_t1_connue",
        "deperdition_age_t1_connue",
        "incertitude_max_points_t1",
        "presidentielle_t2_connue",
        "legislatives_t2_connue",
        "deperdition_age_t2_connue",
        "incertitude_max_points_t2",
    ]
    rows.append(
        {
            "annee": 2017,
            "classe_age": "18-34 approx. non pondere",
            **{key: r1(sum(float(row[key]) for row in bands) / len(bands)) for key in avg_keys},
            "statut": "moyenne simple des tranches 18-24, 25-29, 30-34",
            "source": "Calcul sur Insee Premiere 1670, figures 2 et 3",
        }
    )

    rows.append(
        {
            "annee": 2022,
            "classe_age": "moins de 30 ans",
            "presidentielle_t1_connue": "",
            "legislatives_t1_connue": "",
            "deperdition_age_t1_connue": "",
            "incertitude_max_points_t1": "",
            "presidentielle_t2_connue": "",
            "legislatives_t2_connue": "",
            "deperdition_age_t2_connue": "",
            "incertitude_max_points_t2": "",
            "deperdition_pres_leg_au_moins_un_tour": 39.0,
            "statut": "publie en agrege presidentielle versus legislatives; T1/T2 a calculer par microdonnees",
            "source": INSEE_2022_UNDER30["source"],
        }
    )
    return rows


def build_18_29_public_rows() -> list[dict]:
    rows = [
        age_estimate_from_public_tables(
            year,
            "18-29",
            ["18-24", "25-29"],
            "estimation publique: intermittence nationale appliquee aux 18-24 et 25-29",
        )
        for year in [2002, 2007, 2012]
    ]

    known_2017 = [
        row
        for row in build_youth_turnout_rows(build_youth_rows())
        if row["annee"] == 2017 and row["classe_age"] in {"18-24", "25-29"}
    ]
    avg_keys = [
        "presidentielle_t1_connue",
        "legislatives_t1_connue",
        "deperdition_age_t1_connue",
        "incertitude_max_points_t1",
        "presidentielle_t2_connue",
        "legislatives_t2_connue",
        "deperdition_age_t2_connue",
        "incertitude_max_points_t2",
    ]
    rows.append(
        {
            "annee": 2017,
            "classe_age": "18-29",
            "presidentielle_t1": r1(avg([float(row["presidentielle_t1_connue"]) for row in known_2017])),
            "legislatives_t1": r1(avg([float(row["legislatives_t1_connue"]) for row in known_2017])),
            "deperdition_t1": r1(avg([float(row["deperdition_age_t1_connue"]) for row in known_2017])),
            "incertitude_t1": r1(avg([float(row["incertitude_max_points_t1"]) for row in known_2017])),
            "presidentielle_t2": r1(avg([float(row["presidentielle_t2_connue"]) for row in known_2017])),
            "legislatives_t2": r1(avg([float(row["legislatives_t2_connue"]) for row in known_2017])),
            "deperdition_t2": r1(avg([float(row["deperdition_age_t2_connue"]) for row in known_2017])),
            "incertitude_t2": r1(avg([float(row["incertitude_max_points_t2"]) for row in known_2017])),
            "deperdition_au_moins_un_tour": r1(
                avg([44.3, 40.3])
            ),
            "vote_systematique": "",
            "vote_intermitent": "",
            "abstention_systematique": "",
            "methode": "reconstitution publique directe: figure 3 Insee 1670, moyenne 18-24 / 25-29",
            "methode_classe": "method-direct-2017",
            "source": "Insee Premiere 1670, figures 2 et 3",
        }
    )
    rows.append(
        {
            "annee": 2022,
            "classe_age": "moins de 30 ans",
            "presidentielle_t1": "",
            "legislatives_t1": "",
            "deperdition_t1": "",
            "incertitude_t1": "",
            "presidentielle_t2": "",
            "legislatives_t2": "",
            "deperdition_t2": "",
            "incertitude_t2": "",
            "deperdition_au_moins_un_tour": 39.0,
            "vote_systematique": "",
            "vote_intermitent": "",
            "abstention_systematique": "",
            "methode": "autre methode: ecart publie au moins un tour presidentielle moins au moins un tour legislatives",
            "methode_classe": "method-other-2022",
            "source": INSEE_2022_UNDER30["source"],
        }
    )
    return rows


def build_18_34_rows() -> list[dict]:
    rows = [
        age_estimate_from_public_tables(
            year,
            "18-34",
            ["18-24", "25-29", "30-34"],
            "estimation publique provisoire; microdonnees requises pour une mesure 18-34 definitive",
        )
        for year in [2002, 2007, 2012]
    ]

    row_2017 = next(
        row
        for row in build_youth_turnout_rows(build_youth_rows())
        if row["classe_age"] == "18-34 approx. non pondere"
    )
    rows.append(
        {
            "annee": 2017,
            "classe_age": "18-34",
            "presidentielle_t1": row_2017["presidentielle_t1_connue"],
            "legislatives_t1": row_2017["legislatives_t1_connue"],
            "deperdition_t1": row_2017["deperdition_age_t1_connue"],
            "incertitude_t1": row_2017["incertitude_max_points_t1"],
            "presidentielle_t2": row_2017["presidentielle_t2_connue"],
            "legislatives_t2": row_2017["legislatives_t2_connue"],
            "deperdition_t2": row_2017["deperdition_age_t2_connue"],
            "incertitude_t2": row_2017["incertitude_max_points_t2"],
            "deperdition_au_moins_un_tour": 41.2,
            "vote_systematique": "",
            "vote_intermitent": "",
            "abstention_systematique": "",
            "participation_legislatives_2024": "",
            "methode": "reconstitution publique directe; moyenne simple 18-24, 25-29, 30-34",
            "methode_classe": "method-direct-2017",
            "source": "Insee Premiere 1670, figures 2 et 3",
        }
    )
    rows.append(
        {
            "annee": 2022,
            "classe_age": "18-34",
            "presidentielle_t1": "",
            "legislatives_t1": "",
            "deperdition_t1": "",
            "incertitude_t1": "",
            "presidentielle_t2": "",
            "legislatives_t2": "",
            "deperdition_t2": "",
            "incertitude_t2": "",
            "deperdition_au_moins_un_tour": "",
            "vote_systematique": "",
            "vote_intermitent": "",
            "abstention_systematique": "",
            "participation_legislatives_2024": "",
            "methode": "microdonnees Insee EPE/EDP necessaires: la publication disponible donne seulement moins de 30 ans",
            "methode_classe": "method-microdata-needed",
            "source": "Insee Premiere 1928; microdonnees non presentes dans le depot local",
        }
    )
    rows.append(
        {
            "annee": 2024,
            "classe_age": "18-34",
            "presidentielle_t1": "",
            "legislatives_t1": "",
            "deperdition_t1": "",
            "incertitude_t1": "",
            "presidentielle_t2": "",
            "legislatives_t2": "",
            "deperdition_t2": "",
            "incertitude_t2": "",
            "deperdition_au_moins_un_tour": "",
            "vote_systematique": "",
            "vote_intermitent": "",
            "abstention_systematique": "",
            "participation_legislatives_2024": 54.0,
            "methode": "participation legislative estimee par sondage: moyenne simple 18-24 (57 %) et 25-34 (51 %); pas une deperdition presidentielle-legislatives",
            "methode_classe": "method-partial-2024",
            "source": "Ipsos 2024 cite dans la synthese publique; microdonnees Insee 2024 non trouvees localement",
        }
    )
    return rows


def weighted_2017_18_34_proxy(rows: list[dict]) -> dict:
    bands = [row for row in rows if row["annee"] == 2017]
    keys = [
        "vote_systematique",
        "vote_intermitent",
        "abstention_systematique",
        "deux_votes_uniquement_presidentielle",
        "seul_t1_presidentielle",
        "seul_t2_presidentielle",
        "indicateur_strict_presidentielle_sans_legislatives",
    ]
    return {
        "annee": 2017,
        "classe_age": "18-34 approx. non pondere",
        **{key: r1(sum(float(row[key]) for row in bands) / len(bands)) for key in keys},
        "nature_indicateur": (
            "Moyenne simple des tranches 18-24, 25-29, 30-34. "
            "A remplacer par une moyenne ponderee par effectifs EDP ou RP."
        ),
        "source": "Calcul sur Insee Premiere 1670, figures 2 et 3",
    }


def render_table(rows: list[dict], columns: list[str]) -> str:
    head = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
    body = []
    for row in rows:
        row_class = row.get("methode_classe", "")
        body.append(
            f"<tr class=\"{html.escape(str(row_class))}\">"
            + "".join(f"<td>{html.escape(str(row.get(col, '')))}</td>" for col in columns)
            + "</tr>"
        )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render_table_labeled(
    rows: list[dict], columns: list[tuple[str, str]], raw_columns: set[str] | None = None
) -> str:
    raw_columns = raw_columns or set()
    head = "".join(f"<th>{html.escape(label)}</th>" for _, label in columns)
    body = []
    for row in rows:
        row_class = row.get("methode_classe", "")
        cells = []
        for key, _ in columns:
            value = str(row.get(key, ""))
            cell = value if key in raw_columns else html.escape(value)
            cells.append(f"<td>{cell}</td>")
        body.append(
            f"<tr class=\"{html.escape(str(row_class))}\">"
            + "".join(cells)
            + "</tr>"
        )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def with_global_gap(value: object, reference: float, keep_star: bool = False) -> str:
    if value == "" or value is None:
        return ""
    text_value = str(value)
    numeric_text = text_value.replace("*", "")
    try:
        numeric_value = float(numeric_text)
    except ValueError:
        return text_value
    gap = numeric_value - reference
    sign = "+" if gap >= 0 else ""
    suffix = "*" if keep_star or text_value.endswith("*") else ""
    gap_class = "gap-positive" if gap >= 0 else "gap-negative"
    return (
        f"{numeric_value:.1f}{suffix} "
        f"<span class=\"{gap_class}\">({sign}{gap:.1f})</span>"
    )


def numeric(value: object) -> float | None:
    if value == "" or value is None:
        return None
    try:
        return float(str(value).replace("*", ""))
    except ValueError:
        return None


def build_gap_chart(global_rows: list[dict]) -> str:
    values = []
    for row in global_rows:
        year_values = []
        for key, ref_key, label, color in [
            ("deperdition_18_29_t1", "deperdition_t1", "18-29 T1", "#b42318"),
            ("deperdition_18_29_t2", "deperdition_t2", "18-29 T2", "#e46b5d"),
            ("deperdition_18_34_t1", "deperdition_t1", "18-34 T1", "#245f9d"),
            ("deperdition_18_34_t2", "deperdition_t2", "18-34 T2", "#6aa1cf"),
        ]:
            value = numeric(row.get(key, ""))
            if value is not None:
                year_values.append(
                    {
                        "label": label,
                        "color": color,
                        "gap": round(value - row[ref_key], 1),
                    }
                )
        value = numeric(row.get("deperdition_18_29_au_moins_un_tour", ""))
        if value is not None and row["annee"] == 2022:
            year_values.append(
                {
                    "label": "<30 au moins 1 tour",
                    "color": "#b42318",
                    "gap": round(value - row["deperdition_moyenne_tours"], 1),
                    "marker": "dot",
                }
            )
        values.append({"year": row["annee"], "values": year_values})
    values = [row for row in values if row["values"]]
    years = [row["year"] for row in values]

    width = 980
    height = 330
    margin = {"left": 52, "right": 22, "top": 42, "bottom": 58}
    inner_w = width - margin["left"] - margin["right"]
    inner_h = height - margin["top"] - margin["bottom"]
    max_gap = max(
        [item["gap"] for row in values for item in row["values"]] + [0]
    )
    min_gap = min(
        [item["gap"] for row in values for item in row["values"]] + [0]
    )
    y_min = min(-2, int(min_gap) - 1)
    y_max = max(14, int(max_gap) + 1)

    def x_pos(index: int) -> float:
        if not years:
            return margin["left"] + inner_w / 2
        if len(years) == 1:
            return margin["left"] + inner_w / 2
        return margin["left"] + (index + 0.5) / len(years) * inner_w

    def y_pos(value: float) -> float:
        return margin["top"] + (y_max - value) / (y_max - y_min) * inner_h

    zero_y = y_pos(0)
    parts = [
        f'<svg class="gap-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Ecarts de deperdition jeunes par rapport a la deperdition generale">',
        '<text x="52" y="22" class="chart-title">Sur-deperdition jeune par rapport a la deperdition generale</text>',
    ]
    for tick in range(0, y_max + 1, 4):
        y = y_pos(tick)
        parts.append(
            f'<line x1="{margin["left"]}" x2="{width - margin["right"]}" y1="{y:.1f}" y2="{y:.1f}" class="grid-line"/>'
        )
        parts.append(
            f'<text x="{margin["left"] - 8}" y="{y + 4:.1f}" class="axis-label" text-anchor="end">+{tick}</text>'
        )
    parts.append(
        f'<line x1="{margin["left"]}" x2="{width - margin["right"]}" y1="{zero_y:.1f}" y2="{zero_y:.1f}" class="zero-line"/>'
    )

    bar_width = 12
    bar_gap = 4
    for index, row in enumerate(values):
        center = x_pos(index)
        row_values = row["values"]
        group_width = len(row_values) * bar_width + max(0, len(row_values) - 1) * bar_gap
        start_x = center - group_width / 2
        for item_index, item in enumerate(row_values):
            x = start_x + item_index * (bar_width + bar_gap)
            y = y_pos(max(0, item["gap"]))
            h = abs(y_pos(item["gap"]) - zero_y)
            if item.get("marker") == "dot":
                cx = x + bar_width / 2
                cy = y_pos(item["gap"])
                parts.append(
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{item["color"]}" stroke="#67120d" stroke-width="1.5"/>'
                )
                parts.append(
                    f'<text x="{cx:.1f}" y="{cy - 10:.1f}" class="value-label" text-anchor="middle">+{item["gap"]:.1f}</text>'
                )
            else:
                parts.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{h:.1f}" fill="{item["color"]}"/>'
                )
                parts.append(
                    f'<text x="{x + bar_width / 2:.1f}" y="{y - 4:.1f}" class="value-label" text-anchor="middle">+{item["gap"]:.1f}</text>'
                )
        parts.append(
            f'<text x="{center:.1f}" y="{height - 24}" class="axis-label" text-anchor="middle">{row["year"]}</text>'
        )

    legend_items = [
        ("18-29 T1", "#b42318"),
        ("18-29 T2", "#e46b5d"),
        ("18-34 T1", "#245f9d"),
        ("18-34 T2", "#6aa1cf"),
        ("2022 <30", "#b42318"),
    ]
    legend_x = 600
    legend_y = 18
    for i, (label, color) in enumerate(legend_items):
        x = legend_x + (i % 3) * 120
        y = legend_y + (i // 3) * 18
        parts.append(f'<rect x="{x}" y="{y - 9}" width="10" height="10" fill="{color}"/>')
        parts.append(f'<text x="{x + 15}" y="{y}" class="legend-label">{html.escape(label)}</text>')

    parts.append("</svg>")
    return "".join(parts)


def build_scatter_points(global_rows: list[dict]) -> list[dict]:
    points = []
    for row in global_rows:
        if row["annee"] == 2024:
            continue
        for key, ref_key, label, color in [
            ("deperdition_18_29_t1", "deperdition_t1", "Dep. 18-29 T1", "#b42318"),
            ("deperdition_18_29_t2", "deperdition_t2", "Dep. 18-29 T2", "#b42318"),
            ("deperdition_18_34_t1", "deperdition_t1", "Dep. 18-34 T1", "#245f9d"),
            ("deperdition_18_34_t2", "deperdition_t2", "Dep. 18-34 T2", "#245f9d"),
        ]:
            value = numeric(row.get(key, ""))
            if value is not None:
                points.append(
                    {
                        "annee": row["annee"],
                        "label": label,
                        "x": row[ref_key],
                        "y": value,
                        "gap": value - row[ref_key],
                        "color": color,
                        "shape": "circle",
                    }
                )
        value = numeric(row.get("deperdition_18_29_au_moins_un_tour", ""))
        if value is not None and row["annee"] == 2022:
            points.append(
                {
                    "annee": row["annee"],
                    "label": "Dep. <30 au moins 1 tour",
                    "x": row["deperdition_moyenne_tours"],
                    "y": value,
                    "gap": value - row["deperdition_moyenne_tours"],
                    "color": "#b42318",
                    "shape": "diamond",
                }
            )
        for ref_key, label in [
            ("deperdition_t1", "Déperdition générale T1"),
            ("deperdition_t2", "Déperdition générale T2"),
        ]:
            points.append(
                {
                    "annee": row["annee"],
                    "label": label,
                    "x": row[ref_key],
                    "y": row[ref_key],
                    "gap": 0,
                    "color": "#5f6368",
                    "shape": "square",
                }
            )
    return points


def build_scatter_svg(global_rows: list[dict]) -> str:
    points = build_scatter_points(global_rows)
    width = 1080
    height = 660
    margin = {"left": 112, "right": 72, "top": 72, "bottom": 88}
    inner_w = width - margin["left"] - margin["right"]
    inner_h = height - margin["top"] - margin["bottom"]
    years = sorted({point["annee"] for point in points})
    method_by_year = {row["annee"]: row.get("methode_classe", "") for row in global_rows}
    method_axis_colors = {
        "method-public-estimate": "#fff8e8",
        "method-direct-2017": "#eef7ff",
        "method-other-2022": "#eef8ee",
        "method-microdata-needed": "#f6eefb",
        "method-partial-2024": "#f3f3f1",
    }
    method_axis_strokes = {
        "method-public-estimate": "#d08a00",
        "method-direct-2017": "#1f77b4",
        "method-other-2022": "#3a9d45",
        "method-microdata-needed": "#8a4dbf",
        "method-partial-2024": "#777",
    }
    max_value = max([point["y"] for point in points] + [45])
    axis_max = max(50, int(max_value) + 4)

    series_offsets = {
        "Déperdition générale T1": 0,
        "Dep. 18-29 T1": 0,
        "Dep. 18-34 T1": 0,
        "Déperdition générale T2": 34,
        "Dep. 18-29 T2": 34,
        "Dep. 18-34 T2": 34,
        "Dep. <30 au moins 1 tour": 17,
    }
    gap_offsets = {
        "Dep. 18-29 T1": -10,
        "Dep. 18-29 T2": -10,
        "Dep. 18-34 T1": 10,
        "Dep. 18-34 T2": 10,
        "Dep. <30 au moins 1 tour": 0,
    }
    max_series_offset = max(series_offsets.values())
    year_span_w = inner_w - max_series_offset

    def x_pos(year: int) -> float:
        if len(years) == 1:
            return margin["left"] + year_span_w / 2
        return margin["left"] + years.index(year) / (len(years) - 1) * year_span_w

    def y_pos(value: float) -> float:
        return margin["top"] + (axis_max - value) / axis_max * inner_h

    parts = [
        f'<svg class="scatter" viewBox="0 0 {width} {height}" role="img" aria-label="Évolution par année de la déperdition générale et de la déperdition jeune">',
        '<text x="112" y="30" class="chart-title">Évolution de la déperdition générale et de la déperdition jeune</text>',
        '<text x="112" y="51" class="chart-subtitle">Abscisses : années électorales. Ordonnées : déperdition en points de pourcentage de participation.</text>',
    ]
    for tick in range(0, axis_max + 1, 10):
        y = y_pos(tick)
        parts.append(f'<line x1="{margin["left"]}" x2="{width - margin["right"]}" y1="{y:.1f}" y2="{y:.1f}" class="grid-line"/>')
        parts.append(f'<text x="{margin["left"] - 10}" y="{y + 4:.1f}" class="axis-label" text-anchor="end">{tick}</text>')

    for year in years:
        x = x_pos(year)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{margin["top"]}" y2="{height - margin["bottom"]}" class="year-guide"/>')
        method_class = method_by_year.get(year, "")
        axis_fill = method_axis_colors.get(method_class, "#fff")
        axis_stroke = method_axis_strokes.get(method_class, "#d0d2ca")
        parts.append(
            f'<rect x="{x - 24:.1f}" y="{height - margin["bottom"] + 8}" width="48" height="22" rx="4" '
            f'fill="{axis_fill}" stroke="{axis_stroke}" class="year-axis-chip"/>'
        )
        parts.append(f'<text x="{x:.1f}" y="{height - margin["bottom"] + 24}" class="year-axis-label" text-anchor="middle">{year}</text>')

    turn_groups = {
        "T1": {"Déperdition générale T1", "Dep. 18-29 T1", "Dep. 18-34 T1"},
        "T2": {"Déperdition générale T2", "Dep. 18-29 T2", "Dep. 18-34 T2"},
    }
    for year in years:
        year_points = [point for point in points if point["annee"] == year]
        for turn, labels in turn_groups.items():
            turn_points = [point for point in year_points if point["label"] in labels]
            if not turn_points:
                continue
            label_y = max(margin["top"] + 12, min(y_pos(point["y"]) for point in turn_points) - 12)
            label_x = x_pos(year) + series_offsets[next(iter(labels))]
            parts.append(
                f'<text x="{label_x:.1f}" y="{label_y:.1f}" class="turn-label" text-anchor="middle">{turn}</text>'
            )

    parts.append(f'<text x="{margin["left"] + (year_span_w + max_series_offset) / 2:.1f}" y="{height - 28}" class="axis-title" text-anchor="middle">Année électorale</text>')
    parts.append(f'<text x="20" y="{margin["top"] + inner_h / 2:.1f}" class="axis-title rotate" transform="rotate(-90 20 {margin["top"] + inner_h / 2:.1f})" text-anchor="middle">Déperdition, en points de %</text>')

    for point in points:
        if point["shape"] == "square" or abs(point["gap"]) < 0.05:
            continue
        point_x = x_pos(point["annee"]) + series_offsets.get(point["label"], 0)
        guide_x = point_x + gap_offsets.get(point["label"], 0)
        y_general = y_pos(point["x"])
        y_youth = y_pos(point["y"])
        y_top = min(y_general, y_youth)
        y_bottom = max(y_general, y_youth)
        gap_label = f'{point["gap"]:+.1f}'.replace(".", ",") + " pts"
        label_anchor = "end" if gap_offsets.get(point["label"], 0) < 0 else "start"
        label_dx = -4 if label_anchor == "end" else 4
        parts.append(
            f'<line x1="{guide_x:.1f}" x2="{guide_x:.1f}" y1="{y_top:.1f}" y2="{y_bottom:.1f}" '
            f'stroke="{point["color"]}" class="gap-guide"/>'
        )
        parts.append(
            f'<line x1="{guide_x - 3:.1f}" x2="{guide_x + 3:.1f}" y1="{y_top:.1f}" y2="{y_top:.1f}" '
            f'stroke="{point["color"]}" class="gap-cap"/>'
        )
        parts.append(
            f'<line x1="{guide_x - 3:.1f}" x2="{guide_x + 3:.1f}" y1="{y_bottom:.1f}" y2="{y_bottom:.1f}" '
            f'stroke="{point["color"]}" class="gap-cap"/>'
        )
        parts.append(
            f'<text x="{guide_x + label_dx:.1f}" y="{(y_top + y_bottom) / 2 + 3:.1f}" '
            f'fill="{point["color"]}" class="gap-label" text-anchor="{label_anchor}">{gap_label}</text>'
        )

    for point in points:
        x = x_pos(point["annee"]) + series_offsets.get(point["label"], 0)
        y = y_pos(point["y"])
        color = point["color"]
        title = (
            f'{point["annee"]} - {point["label"]}: '
            f'déperdition {point["y"]:.1f} pt, '
            f'écart {point["gap"]:+.1f} pt'
        )
        if point["shape"] == "square":
            parts.append(
                f'<rect x="{x - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" rx="2" '
                f'class="general-point" tabindex="0"><title>{html.escape(title)}</title></rect>'
            )
        elif point["shape"] == "diamond":
            parts.append(
                f'<path d="M {x:.1f} {y - 8:.1f} L {x + 8:.1f} {y:.1f} L {x:.1f} {y + 8:.1f} L {x - 8:.1f} {y:.1f} Z" '
                f'fill="{color}" stroke="#67120d" stroke-width="1.5" tabindex="0"><title>{html.escape(title)}</title></path>'
            )
        else:
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.2" fill="{color}" opacity="0.92" '
                f'stroke="#fff" stroke-width="1.5" tabindex="0"><title>{html.escape(title)}</title></circle>'
            )

    parts.append("</svg>")
    return "".join(parts)


def build_scatter_html(global_rows: list[dict]) -> str:
    scatter_svg = build_scatter_svg(global_rows)
    legend_html = """
    <div class="scatter-legend" aria-label="Légende du graphique">
      <span class="legend-item"><span class="legend-symbol legend-square"></span>Déperdition générale</span>
      <span class="legend-item"><span class="legend-symbol legend-dot red"></span>18-29</span>
      <span class="legend-item"><span class="legend-symbol legend-dot blue"></span>18-34</span>
      <span class="legend-item"><span class="legend-symbol legend-diamond red"></span>2022 &lt;30 ans</span>
    </div>
    """
    method_legend_html = """
    <div class="method-legend-wrap">
      <div class="method-legend-heading">Sources et méthodes par année</div>
      <div class="method-legend" aria-label="Légende des sources et méthodes">
        <div class="method-legend-item"><i class="method-swatch" style="background:white"></i><span><span class="method-legend-title">Lecture des écarts</span><span class="method-legend-text">Les valeurs sont des points de pourcentage de participation. Dans les infobulles, l’écart indique la différence avec la déperdition générale du même tour. Pour “au moins 1 tour”, la référence est la déperdition générale moyenne T1/T2.</span></span></div>
        <div class="method-legend-item"><i class="method-swatch" style="background:#fff8e8"></i><span><span class="method-legend-title">2002-2012 : estimation publique</span><span class="method-legend-text">Source Insee Première 1671 : vote systématique, intermittent et abstention systématique par âge. La déperdition jeune est estimée en appliquant aux classes 18-29 et 18-34 la répartition nationale des formes de vote intermittent publiée dans la même étude.</span><a class="method-legend-link" href="https://www.insee.fr/fr/statistiques/3140794">Insee Première 1671</a></span></div>
        <div class="method-legend-item"><i class="method-swatch" style="background:#eef7ff"></i><span><span class="method-legend-title">2017 : reconstitution directe</span><span class="method-legend-text">Source Insee Première 1670 : catégories d’intermittence détaillées par âge (18-24, 25-29, 30-34). Elles permettent de reconstruire des déperditions T1/T2 par âge avec une incertitude résiduelle limitée.</span><a class="method-legend-link" href="https://www.insee.fr/fr/statistiques/3138704">Insee Première 1670</a></span></div>
        <div class="method-legend-item"><i class="method-swatch" style="background:#eef8ee"></i><span><span class="method-legend-title">2022 : indicateur publié moins de 30 ans</span><span class="method-legend-text">Source Insee Première 1928 : 74 % des moins de 30 ans ont voté à au moins un tour présidentiel, contre 35 % à au moins un tour législatif, soit 39 points. Pas de ventilation publique T1/T2 ni 18-34 comparable.</span><a class="method-legend-link" href="https://www.insee.fr/fr/statistiques/6658143">Insee Première 1928</a></span></div>
        <div class="method-legend-item"><i class="method-swatch" style="background:#f3f3f1"></i><span><span class="method-legend-title">2024 : données partielles</span><span class="method-legend-text">Source participation législatives 2024 + estimation par âge issue de sondage. Scrutin anticipé sans présidentielle la même année : information utile dans le tableau, mais non comparable comme déperdition présidentielle-législatives.</span><a class="method-legend-link" href="https://www.resultats-elections.interieur.gouv.fr/legislatives2024/">Résultats législatives 2024</a></span></div>
      </div>
    </div>
    """
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nuage de points - déperdition jeunes</title>
  <style>
    body {{ margin:0; font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:#202124; background:#f5f5f2; }}
    main {{ max-width:1120px; margin:0 auto; padding:24px 18px 34px; }}
    h1 {{ font-size:24px; margin:0 0 6px; line-height:1.1; }}
    p {{ font-size:13px; color:#5f6368; line-height:1.45; max-width:860px; }}
    a {{ color:#245f9d; font-weight:650; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .chart-panel {{ margin-top:16px; background:white; border:1px solid #d7d9d2; box-shadow:0 1px 2px rgba(0,0,0,.04); overflow-x:auto; }}
    .scatter {{ display:block; min-width:900px; width:100%; height:auto; }}
    .chart-title {{ font-size:17px; font-weight:760; fill:#202124; }}
    .chart-subtitle {{ font-size:12px; fill:#5f6368; }}
    .grid-line {{ stroke:#e6e7e1; stroke-width:1; }}
    .year-guide {{ stroke:#eceee8; stroke-width:1; }}
    .gap-guide {{ stroke-width:1.2; stroke-dasharray:2 3; opacity:.62; }}
    .gap-cap {{ stroke-width:1.2; opacity:.7; }}
    .gap-label {{ font-size:9.5px; font-weight:720; opacity:.82; }}
    .general-point {{ fill:#fff; stroke:#5f6368; stroke-width:2; }}
    .axis-label {{ font-size:11px; fill:#5f6368; }}
    .year-axis-label {{ font-size:12px; fill:#202124; font-weight:760; }}
    .turn-label {{ font-size:11px; fill:#111; font-weight:780; }}
    .axis-title {{ font-size:12px; font-weight:700; fill:#30332f; }}
    .scatter-legend {{ display:flex; flex-wrap:wrap; gap:10px 18px; align-items:center; padding:11px 16px 14px; border-top:1px solid #eceee8; font-size:12px; color:#3f453d; }}
    .legend-item {{ display:inline-flex; align-items:center; gap:7px; white-space:nowrap; }}
    .legend-symbol {{ display:inline-block; width:11px; height:11px; box-sizing:border-box; }}
    .legend-square {{ border:2px solid #5f6368; background:#fff; border-radius:2px; }}
    .legend-dot {{ border-radius:50%; border:1.5px solid #fff; }}
    .legend-diamond {{ transform:rotate(45deg); border:1px solid #67120d; }}
    .red {{ background:#b42318; }}
    .blue {{ background:#245f9d; }}
    .method-legend-wrap {{ border-top:1px solid #eceee8; padding:12px 16px 15px; }}
    .method-legend-heading {{ font-size:13px; font-weight:760; color:#252823; margin-bottom:8px; }}
    .method-legend {{ display:grid; grid-template-columns:1fr 1fr; gap:7px; font-size:11.5px; color:#3c4043; }}
    .method-legend-item {{ display:grid; grid-template-columns:12px minmax(0,1fr); gap:7px; align-items:start; padding:7px 8px; border:1px solid #dddfd8; background:rgba(255,255,255,.72); }}
    .method-swatch {{ width:12px; height:12px; border:1px solid #b9bbb4; display:inline-block; margin-top:1px; }}
    .method-legend-title {{ display:block; font-weight:750; color:#252823; margin-bottom:2px; }}
    .method-legend-text {{ display:block; line-height:1.3; }}
    .method-legend-link {{ display:inline-block; margin-top:3px; color:#245f9d; text-decoration:none; font-weight:650; }}
    .method-legend-link:hover {{ text-decoration:underline; }}
    @media (max-width: 900px) {{
      .method-legend {{ grid-template-columns:1fr; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Évolution de la déperdition générale et de la déperdition jeune</h1>
  <p>Chaque point place une année en abscisse et une déperdition en points de pourcentage de participation en ordonnée. Les carrés gris indiquent la déperdition générale ; les points colorés indiquent les classes d’âge disponibles.</p>
  <p><a href="deperdition-presidentielle-legislatives.html">Retour au tableau national</a></p>
  <div class="chart-panel">{scatter_svg}{legend_html}{method_legend_html}</div>
</main>
</body>
</html>
"""


def build_html(global_rows: list[dict], youth_rows: list[dict]) -> str:
    method_labels = {
        "method-public-estimate": ("Est. publique", "Est. publique"),
        "method-direct-2017": ("Direct Insee", "Direct Insee"),
        "method-other-2022": ("Publie <30*", "Microdonnees requises"),
        "method-partial-2024": ("", "Partiel sondage"),
    }
    display_rows = []
    for row in global_rows:
        row_display = dict(row)
        method_18_29, method_18_34 = method_labels.get(
            row.get("methode_classe", ""), ("", "")
        )
        row_display["methode_18_29_affichage"] = method_18_29
        row_display["methode_18_34_affichage"] = method_18_34
        row_display["deperdition_18_29_t1_affichage"] = with_global_gap(
            row.get("deperdition_18_29_t1", ""), row["deperdition_t1"]
        )
        row_display["deperdition_18_29_t2_affichage"] = with_global_gap(
            row.get("deperdition_18_29_t2", ""), row["deperdition_t2"]
        )
        row_display["deperdition_18_29_au_moins_un_tour_affichage"] = with_global_gap(
            row.get("deperdition_18_29_au_moins_un_tour", ""),
            row["deperdition_moyenne_tours"],
        )
        row_display["deperdition_18_34_t1_affichage"] = with_global_gap(
            row.get("deperdition_18_34_t1", ""), row["deperdition_t1"]
        )
        row_display["deperdition_18_34_t2_affichage"] = with_global_gap(
            row.get("deperdition_18_34_t2", ""), row["deperdition_t2"]
        )
        row_display["deperdition_18_34_au_moins_un_tour_affichage"] = with_global_gap(
            row.get("deperdition_18_34_au_moins_un_tour", ""),
            row["deperdition_moyenne_tours"],
        )
        display_rows.append(row_display)

    table_nationale_cols = [
        ("annee", "Annee"),
        ("couple_scrutin", "Couple"),
        ("presidentielle_t1", "Part. pres. T1"),
        ("legislatives_t1", "Part. leg. T1"),
        ("presidentielle_t2", "Part. pres. T2"),
        ("legislatives_t2", "Part. leg. T2"),
        ("deperdition_t1", "Déperdition générale T1"),
        ("deperdition_t2", "Déperdition générale T2"),
        ("deperdition_18_29_t1_affichage", "Dep. 18-29 T1"),
        ("deperdition_18_29_t2_affichage", "Dep. 18-29 T2"),
        ("deperdition_18_29_au_moins_un_tour_affichage", "Dep. 18-29 au moins 1 tour"),
        ("deperdition_18_34_t1_affichage", "Dep. 18-34 T1"),
        ("deperdition_18_34_t2_affichage", "Dep. 18-34 T2"),
        ("deperdition_18_34_au_moins_un_tour_affichage", "Dep. 18-34 au moins 1 tour"),
        ("participation_legislatives_2024_18_34", "Leg. 2024 18-34"),
    ]
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Deperdition presidentielle-legislatives : effet jeunes</title>
  <style>
    :root {{
      --line:#d7d9d2;
      --muted:#5f6368;
      --ink:#202124;
      --bg:#f5f5f2;
    }}
    body {{ margin:0; font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:var(--bg); }}
    main {{ max-width:1480px; margin:0 auto; padding:22px 18px 32px; }}
    header {{ margin-bottom:14px; }}
    h1 {{ font-size:24px; line-height:1.1; margin:0; letter-spacing:0; }}
    .subtitle {{ color:var(--muted); font-size:13px; line-height:1.35; margin:6px 0 0; max-width:760px; }}
    .note {{ font-size:12px; color:var(--muted); line-height:1.4; margin:9px 0 0; }}
    .legend {{ display:grid; grid-template-columns:1fr 1fr; gap:7px; margin-top:12px; font-size:11.5px; color:#3c4043; }}
    .legend-heading {{ font-size:13px; font-weight:750; margin:14px 0 0; color:#252823; }}
    .legend-item {{ display:grid; grid-template-columns:12px minmax(0,1fr); gap:7px; align-items:start; padding:7px 8px; border:1px solid #dddfd8; background:rgba(255,255,255,.72); }}
    .legend-title {{ display:block; font-weight:750; color:#252823; margin-bottom:2px; }}
    .legend-text {{ display:block; line-height:1.3; }}
    .legend-link {{ display:inline-block; margin-top:3px; color:#245f9d; text-decoration:none; font-weight:650; }}
    .legend-link:hover {{ text-decoration:underline; }}
    .swatch {{ width:12px; height:12px; border:1px solid #b9bbb4; display:inline-block; margin-top:1px; }}
    .gap-positive {{ color:#b42318; font-weight:750; }}
    .gap-negative {{ color:#247a3d; font-weight:750; }}
    .table-wrap {{ overflow-x:auto; border:1px solid var(--line); background:white; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
    table {{ border-collapse:separate; border-spacing:0; width:100%; min-width:1320px; background:white; font-size:12px; line-height:1.22; }}
    th, td {{ padding:6px 7px; border-bottom:1px solid #e6e7e1; border-right:1px solid #ecede8; text-align:right; vertical-align:top; }}
    th {{ position:sticky; top:0; z-index:1; background:#e9ebe4; font-weight:700; color:#30332f; white-space:normal; }}
    tbody tr:last-child td {{ border-bottom:0; }}
    th:first-child, td:first-child {{ text-align:left; font-weight:700; }}
    th:nth-child(2), td:nth-child(2) {{ text-align:left; }}
    th:nth-child(7), td:nth-child(7) {{ border-left:4px solid #111; }}
    th:nth-child(2), td:nth-child(2) {{ min-width:118px; }}
    th:nth-child(n+3):nth-child(-n+15) {{ min-width:58px; }}
    .method-public-estimate td {{ background:#fff8e8; }}
    .method-direct-2017 td {{ background:#eef7ff; }}
    .method-other-2022 td {{ background:#eef8ee; }}
    .method-microdata-needed td {{ background:#f6eefb; }}
    .method-partial-2024 td {{ background:#f3f3f1; }}
    .method-public-estimate td:first-child {{ box-shadow:inset 5px 0 #d08a00; }}
    .method-direct-2017 td:first-child {{ box-shadow:inset 5px 0 #1f77b4; }}
    .method-other-2022 td:first-child {{ box-shadow:inset 5px 0 #3a9d45; }}
    .method-microdata-needed td:first-child {{ box-shadow:inset 5px 0 #8a4dbf; }}
    .method-partial-2024 td:first-child {{ box-shadow:inset 5px 0 #777; }}
    .chart-link {{ display:inline-block; margin-top:10px; padding:7px 10px; border:1px solid #c8d3df; background:#fff; color:#245f9d; text-decoration:none; font-weight:700; font-size:12px; }}
    .chart-link:hover {{ text-decoration:underline; }}
    @media (max-width: 900px) {{
      header {{ display:block; }}
      .legend {{ grid-template-columns:1fr; margin-top:12px; max-width:none; }}
      main {{ padding:18px 12px 28px; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>Deperdition presidentielle-legislatives : effet jeunes et donnees disponibles</h1>
      <p class="subtitle">Deperdition de participation entre presidentielles et legislatives, avec indicateurs jeunes disponibles ou estimes. Les nombres du tableau sont des pourcentages.</p>
    </div>
  </header>
  <div class="table-wrap">{render_table_labeled(display_rows, table_nationale_cols, {"deperdition_18_29_t1_affichage", "deperdition_18_29_t2_affichage", "deperdition_18_29_au_moins_un_tour_affichage", "deperdition_18_34_t1_affichage", "deperdition_18_34_t2_affichage", "deperdition_18_34_au_moins_un_tour_affichage"})}</div>
  <p class="note">* En 2022, l'indicateur publie par l'Insee porte sur les inscrits de moins de 30 ans, classe tres proche mais legerement differente de 18-29 ans. Les libelles de methode sont detailles dans les CSV sources.</p>
  <a class="chart-link" href="deperdition-ecarts-nuage.html">Ouvrir le nuage de points des écarts</a>
  <div class="legend-heading">Sources et methodes par couleur</div>
  <div class="legend" aria-label="Legende des sources et methodes">
    <div class="legend-item"><i class="swatch" style="background:white"></i><span><span class="legend-title">Lecture des parentheses</span><span class="legend-text">Entre parentheses, l'ecart avec la deperdition generale : par exemple 41,7 (+12,6) signifie que la classe d'age perd 12,6 points de participation de plus que l'ensemble des inscrits. Pour "au moins 1 tour", la reference est la deperdition generale moyenne T1/T2.</span></span></div>
    <div class="legend-item"><i class="swatch" style="background:#fff8e8"></i><span><span class="legend-title">2002-2012 : estimation publique</span><span class="legend-text">Source Insee Premiere 1671 : vote systematique, intermittent et abstention systematique par age. La deperdition jeune est estimee en appliquant aux classes 18-29 et 18-34 la repartition nationale des formes de vote intermittent publiee dans la meme etude.</span><a class="legend-link" href="https://www.insee.fr/fr/statistiques/3140794">Insee Premiere 1671</a></span></div>
    <div class="legend-item"><i class="swatch" style="background:#eef7ff"></i><span><span class="legend-title">2017 : reconstitution directe</span><span class="legend-text">Source Insee Premiere 1670 : categories d'intermittence detaillees par age (18-24, 25-29, 30-34). Elles permettent de reconstruire des deperditions T1/T2 par age avec une incertitude residuelle limitee.</span><a class="legend-link" href="https://www.insee.fr/fr/statistiques/3138704">Insee Premiere 1670</a></span></div>
    <div class="legend-item"><i class="swatch" style="background:#eef8ee"></i><span><span class="legend-title">2022 : indicateur publie moins de 30 ans</span><span class="legend-text">Source Insee Premiere 1928 : 74 % des moins de 30 ans ont vote a au moins un tour presidentiel, contre 35 % a au moins un tour legislatif, soit 39 points. Pas de ventilation publique T1/T2 ni 18-34 comparable.</span><a class="legend-link" href="https://www.insee.fr/fr/statistiques/6658143">Insee Premiere 1928</a></span></div>
    <div class="legend-item"><i class="swatch" style="background:#f3f3f1"></i><span><span class="legend-title">2024 : donnees partielles</span><span class="legend-text">Source participation legislatives 2024 + estimation par age issue de sondage. Scrutin anticipe sans presidentielle la meme annee : la ligne est informative, mais non comparable comme deperdition presidentielle-legislatives.</span><a class="legend-link" href="https://www.resultats-elections.interieur.gouv.fr/legislatives2024/">Resultats legislatives 2024</a></span></div>
  </div>
</main>
</body>
</html>
"""


def build_report(global_rows: list[dict], youth_rows: list[dict]) -> str:
    rows_18_29 = build_18_29_public_rows()
    rows_18_34 = build_18_34_rows()
    global_peak = max(global_rows, key=lambda row: row["deperdition_moyenne_tours"])
    t1_2022 = next(row for row in global_rows if row["annee"] == 2022)
    return f"""# Deperdition du vote des jeunes entre presidentielles et legislatives

## Ce que mesure cette v1

Cette version ajoute deux lectures paralleles :

1. **Version 18-29 ans, 2002-2022** : serie exploitable avec les publications publiques Insee. Les annees 2002-2012 sont des estimations publiques ; 2017 utilise une reconstitution plus directe ; 2022 utilise l'indicateur publie "moins de 30 ans".
2. **Version 18-34 ans, 2002-2024** : serie cible. Elle conserve les estimations publiques disponibles, mais marque explicitement les annees qui demandent des microdonnees Insee EPE/EDP pour devenir definitives. La ligne 2024 est partielle car il n'y a pas de presidentielle 2024.

La ligne 2024 de la table nationale compare la presidentielle 2022 aux legislatives anticipees 2024. Elle est utile politiquement, mais elle ne constitue pas un cycle presidentielle-legislatives classique.

## Resultats nationaux

| Annee | Couple | Pres. T1 | Leg. T1 | Pres. T2 | Leg. T2 | Dep. globale T1 | Dep. globale T2 | Dep. 18-29 T1 | Dep. 18-29 T2 | Dep. 18-29 au moins un tour | Methode 18-29 | Dep. 18-34 T1 | Dep. 18-34 T2 | Dep. 18-34 au moins un tour | Participation leg. 2024 18-34 | Methode 18-34 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
{chr(10).join(f'| {row["annee"]} | {row["couple_scrutin"]} | {row["presidentielle_t1"]:.2f} | {row["legislatives_t1"]:.2f} | {row["presidentielle_t2"]:.2f} | {row["legislatives_t2"]:.2f} | {row["deperdition_t1"]:.2f} | {row["deperdition_t2"]:.2f} | {row["deperdition_18_29_t1"]} | {row["deperdition_18_29_t2"]} | {row["deperdition_18_29_au_moins_un_tour"]} | {row["methode_18_29"]} | {row["deperdition_18_34_t1"]} | {row["deperdition_18_34_t2"]} | {row["deperdition_18_34_au_moins_un_tour"]} | {row["participation_legislatives_2024_18_34"]} | {row["methode_18_34"]} |' for row in global_rows)}

* En 2022, l'indicateur publie par l'Insee porte sur les inscrits de moins de 30 ans, classe tres proche mais legerement differente de 18-29 ans.

Point saillant : le maximum de la serie est **{global_peak["annee"]}**, avec **{global_peak["deperdition_moyenne_tours"]:.1f} points** de participation perdus en moyenne entre presidentielle et legislatives. En 2022, la deperdition reste tres elevee : **{t1_2022["deperdition_t1"]:.1f} points au T1** et **{t1_2022["deperdition_t2"]:.1f} points au T2**.

## Version 18-29 ans

| Annee | Classe | Dep. T1 | Dep. T2 | Dep. au moins un tour | Incert. | Methode |
|---:|---|---:|---:|---:|---:|---|
{chr(10).join(f'| {row["annee"]} | {row["classe_age"]} | {row["deperdition_t1"]} | {row["deperdition_t2"]} | {row["deperdition_au_moins_un_tour"]} | {row["incertitude_t1"]} | {row["methode"]} |' for row in rows_18_29)}

## Version 18-34 ans

| Annee | Classe | Dep. T1 | Dep. T2 | Dep. au moins un tour | Participation leg. 2024 | Methode |
|---:|---|---:|---:|---:|---:|---|
{chr(10).join(f'| {row["annee"]} | {row["classe_age"]} | {row["deperdition_t1"]} | {row["deperdition_t2"]} | {row["deperdition_au_moins_un_tour"]} | {row.get("participation_legislatives_2024", "")} | {row["methode"]} |' for row in rows_18_34)}

## Lecture methodologique

- 2002-2012 : estimation publique a partir de la figure 3 Insee 1671, en appliquant aux classes d'age la composition nationale de l'intermittence publiee en figure 2.
- 2017 : reconstitution plus directe avec les categories d'intermittence publiees par tranche d'age dans Insee Premiere 1670.
- 2022 : l'indicateur public robuste est "moins de 30 ans", avec 39 points d'ecart entre au moins un tour presidentiel et au moins un tour legislatif.
- 2024 : pas de presidentielle la meme annee ; la ligne 18-34 est donc une participation legislative partielle, pas une deperdition.
- Microdonnees : aucun fichier EPE/EDP individuel n'a ete trouve dans le depot local. La version 18-34 definitive demande donc une recuperation externe des microdonnees Insee lorsque disponibles.

## Forme de rendu recommandee

- **Table nationale** : tableau large avec colonnes globales, 18-29 et 18-34, et statut methodologique.
- **Deux tables de version** : une table 18-29 publique et une table 18-34 cible.
- **Encadrement couleur** : orange pour estimation publique, bleu pour reconstitution directe, vert pour autre methode publiee, violet pour microdonnees requises, gris pour 2024 partiel.

## Sources

- Insee Premiere 1670, *Elections presidentielle et legislatives de 2017 : neuf inscrits sur dix ont vote a au moins un tour de scrutin* : https://www.insee.fr/fr/statistiques/3138704
- Insee Premiere 1671, *Elections presidentielles et legislatives de 2002 a 2017 : une participation atypique en 2017* : https://www.insee.fr/fr/statistiques/3140794
- Insee Premiere 1928, *Elections presidentielle et legislatives de 2022 : seul un tiers des electeurs a vote a tous les tours*.
- Ministere de l'Interieur, resultats nationaux par scrutin.
- Elections legislatives 2024 : resultats nationaux et participation finale, Ministere de l'Interieur.

## Fichiers produits

- `data/04_analysis/participation/deperdition_globale_2002_2024.csv`
- `data/04_analysis/participation/deperdition_18_29_public_2002_2022.csv`
- `data/04_analysis/participation/deperdition_18_34_microdonnees_2002_2024.csv`
- `data/04_analysis/participation/deperdition_jeunes_insee_2017_2022.csv`
- `analyses/deperdition-jeunes-2002-2022/deperdition-presidentielle-legislatives.html`
"""


def main() -> None:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_ANALYSIS.mkdir(parents=True, exist_ok=True)

    youth_rows = build_youth_rows()
    global_rows = add_age_deperdition_to_global_rows(build_global_rows(), youth_rows)
    rows_18_29 = build_18_29_public_rows()
    rows_18_34 = build_18_34_rows()

    write_csv(
        OUT_DATA / "deperdition_globale_2002_2024.csv",
        global_rows,
        [
            "annee",
            "couple_scrutin",
            "presidentielle_t1",
            "presidentielle_t2",
            "legislatives_t1",
            "legislatives_t2",
            "deperdition_t1",
            "deperdition_t2",
            "deperdition_18_29_t1",
            "deperdition_18_29_t2",
            "deperdition_18_29_au_moins_un_tour",
            "methode_18_29",
            "deperdition_18_34_t1",
            "deperdition_18_34_t2",
            "deperdition_18_34_au_moins_un_tour",
            "participation_legislatives_2024_18_34",
            "methode_18_34",
            "methode_classe",
            "deperdition_age_t1",
            "deperdition_age_t2",
            "deperdition_age_au_moins_un_tour",
            "classe_age_deperdition",
            "statut_deperdition_age",
            "participation_moyenne_presidentielle",
            "participation_moyenne_legislatives",
            "deperdition_moyenne_tours",
            "ratio_retention_moyen_leg_sur_pres",
            "source",
        ],
    )
    age_series_fields = [
        "annee",
        "classe_age",
        "presidentielle_t1",
        "legislatives_t1",
        "deperdition_t1",
        "incertitude_t1",
        "presidentielle_t2",
        "legislatives_t2",
        "deperdition_t2",
        "incertitude_t2",
        "deperdition_au_moins_un_tour",
        "vote_systematique",
        "vote_intermitent",
        "abstention_systematique",
        "participation_legislatives_2024",
        "methode",
        "methode_classe",
        "source",
    ]
    write_csv(
        OUT_DATA / "deperdition_18_29_public_2002_2022.csv",
        rows_18_29,
        age_series_fields,
    )
    write_csv(
        OUT_DATA / "deperdition_18_34_microdonnees_2002_2024.csv",
        rows_18_34,
        age_series_fields,
    )
    write_csv(
        OUT_DATA / "deperdition_jeunes_insee_2017_2022.csv",
        youth_rows + [weighted_2017_18_34_proxy(youth_rows)],
        [
            "annee",
            "classe_age",
            "vote_systematique",
            "vote_intermitent",
            "abstention_systematique",
            "deux_votes_uniquement_presidentielle",
            "tout_sauf_legislatives_t2",
            "tout_sauf_legislatives_t1",
            "seul_t1_presidentielle",
            "seul_t2_presidentielle",
            "vote_intermitent_autre",
            "participation_au_moins_une_fois_presidentielle",
            "participation_au_moins_une_fois_legislatives",
            "indicateur_strict_presidentielle_sans_legislatives",
            "nature_indicateur",
            "source",
        ],
    )
    write_csv(
        OUT_DATA / "deperdition_age_par_tour_2017_2022.csv",
        build_youth_turnout_rows(youth_rows),
        [
            "annee",
            "classe_age",
            "presidentielle_t1_connue",
            "legislatives_t1_connue",
            "deperdition_age_t1_connue",
            "incertitude_max_points_t1",
            "presidentielle_t2_connue",
            "legislatives_t2_connue",
            "deperdition_age_t2_connue",
            "incertitude_max_points_t2",
            "deperdition_pres_leg_au_moins_un_tour",
            "statut",
            "source",
        ],
    )

    (OUT_ANALYSIS / "deperdition-presidentielle-legislatives.html").write_text(
        build_html(global_rows, youth_rows), encoding="utf-8"
    )
    (OUT_ANALYSIS / "deperdition-ecarts-nuage.html").write_text(
        build_scatter_html(global_rows), encoding="utf-8"
    )
    (OUT_ANALYSIS / "README.md").write_text(
        build_report(global_rows, youth_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
