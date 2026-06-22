import csv
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1] / "src/scripts/cartographie"
)
sys.path.insert(0, str(SCRIPT_DIR))

import cartes_departements_mal_inscrits_nupes_2022 as maps


BASE_HEADERS = [
    "Code du département",
    "Libellé du département",
    "Code de la circonscription",
    "Code de la commune",
    "Code du b.vote",
    "Inscrits",
    "Votants",
    "Blancs",
    "Nuls",
    "Exprimés",
]
CANDIDATE_HEADERS = [
    "N°Panneau",
    "Sexe",
    "Nom",
    "Prénom",
    "Nuance",
    "Voix",
    "% Voix/Ins",
    "% Voix/Exp",
]


def candidate(number, nuance, votes):
    return [str(number), "F", f"Nom {number}", "Prénom", nuance, votes, "", ""]


def election_row(dep, name, candidates):
    return [
        dep,
        name,
        "1",
        "001",
        "0001",
        "100",
        "60",
        "1",
        "1",
        "58",
        *candidates,
    ]


class CandidateAggregationTests(unittest.TestCase):
    def write_source(self, rows):
        temporary = tempfile.NamedTemporaryFile(
            mode="w", encoding="cp1252", newline="", suffix=".csv", delete=False
        )
        path = Path(temporary.name)
        with temporary:
            writer = csv.writer(temporary, delimiter=";", lineterminator="\n")
            writer.writerow(BASE_HEADERS + CANDIDATE_HEADERS * 3)
            writer.writerows(rows)
        self.addCleanup(path.unlink)
        return path

    def test_empty_candidate_votes_do_not_stop_later_candidates(self):
        row = election_row(
            "01",
            "Ain",
            candidate(1, "DIV", "")
            + candidate(2, "NUP", "17")
            + candidate(3, "RN", "10"),
        )
        totals = maps.aggregate_candidate_votes(
            self.write_source([row]), 1, set()
        )

        self.assertEqual(totals["01"]["voix_nupes"], 17)
        self.assertEqual(totals["01"]["bureaux_avec_nupes"], 1)

    def test_duplicate_bureau_is_ignored_for_votes_and_counters(self):
        row = election_row(
            "01",
            "Ain",
            candidate(1, "NUP", "17")
            + candidate(2, "RN", "10")
            + candidate(3, "DIV", "4"),
        )
        duplicate_with_changed_turnout = row.copy()
        duplicate_with_changed_turnout[5] = "101"
        totals = maps.aggregate_candidate_votes(
            self.write_source([row, duplicate_with_changed_turnout]), 1, set()
        )

        self.assertEqual(totals["01"]["bureaux"], 1)
        self.assertEqual(totals["01"]["voix_nupes"], 17)
        self.assertEqual(totals["01"]["bureaux_avec_nupes"], 1)

    def test_bureau_deduplication_is_scoped_by_department(self):
        candidates = (
            candidate(1, "NUP", "17")
            + candidate(2, "RN", "10")
            + candidate(3, "DIV", "4")
        )
        rows = [
            election_row("01", "Ain", candidates),
            election_row("02", "Aisne", candidates),
        ]
        totals = maps.aggregate_candidate_votes(
            self.write_source(rows), 2, set()
        )

        self.assertEqual(totals["01"]["bureaux"], 1)
        self.assertEqual(totals["02"]["bureaux"], 1)
        self.assertEqual(totals["01"]["voix_nupes"], 17)
        self.assertEqual(totals["02"]["voix_nupes"], 17)

    def test_legis_candidate_key_can_identify_nupes_without_nup_nuance(self):
        row = election_row(
            "01",
            "Ain",
            candidate(1, "DVG", "19")
            + candidate(2, "RN", "10")
            + candidate(3, "DIV", "4"),
        )
        totals = maps.aggregate_candidate_votes(
            self.write_source([row]), 1, {("01", "01", 1)}
        )

        self.assertEqual(totals["01"]["voix_nupes"], 19)


class DepartmentCodeTests(unittest.TestCase):
    def test_department_codes_are_normalized_consistently(self):
        self.assertEqual(maps.code_departement(1), "01")
        self.assertEqual(maps.code_departement("2A"), "2A")
        self.assertEqual(maps.code_departement("ZA"), "971")
        self.assertEqual(maps.code_departement(971), "971")


if __name__ == "__main__":
    unittest.main()
