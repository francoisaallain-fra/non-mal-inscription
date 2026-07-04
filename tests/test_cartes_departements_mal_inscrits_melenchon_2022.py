import csv
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "src/scripts/cartographie"
sys.path.insert(0, str(SCRIPT_DIR))

import cartes_departements_mal_inscrits_melenchon_2022 as maps


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
    "Voix",
    "% Voix/Ins",
    "% Voix/Exp",
]


def candidate(number, name, first_name, votes):
    return [str(number), "M", name, first_name, votes, "", ""]


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


class PresidentialAggregationTests(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.output_dir.cleanup)
        output_root = Path(self.output_dir.name)

        old_csv = maps.MELENCHON_CSV
        old_qa = maps.QA_TOTALS
        maps.MELENCHON_CSV = output_root / "melenchon.csv"
        maps.QA_TOTALS = output_root / "qa.csv"
        self.addCleanup(setattr, maps, "MELENCHON_CSV", old_csv)
        self.addCleanup(setattr, maps, "QA_TOTALS", old_qa)

    def write_source(self, rows):
        temporary = tempfile.NamedTemporaryFile(
            mode="w", encoding="latin1", newline="", suffix=".csv", delete=False
        )
        path = Path(temporary.name)
        with temporary:
            writer = csv.writer(temporary, delimiter=";", lineterminator="\n")
            writer.writerow(BASE_HEADERS + CANDIDATE_HEADERS)
            writer.writerows(rows)
        self.addCleanup(path.unlink)
        return path

    def test_melenchon_candidate_is_identified_with_accents(self):
        row = election_row(
            "01",
            "Ain",
            candidate(1, "MACRON", "Emmanuel", "20")
            + candidate(7, "MÉLENCHON", "Jean-Luc", "17")
            + candidate(12, "DUPONT-AIGNAN", "Nicolas", "5"),
        )

        old_source = maps.PRESIDENTIELLE_T1
        maps.PRESIDENTIELLE_T1 = self.write_source([row])
        self.addCleanup(setattr, maps, "PRESIDENTIELLE_T1", old_source)

        totals = maps.aggregate_melenchon_t1()

        self.assertEqual(totals["01"]["voix_melenchon"], 17)
        self.assertEqual(totals["01"]["bureaux_avec_melenchon"], 1)
        self.assertEqual(totals["01"]["part_melenchon_exprimes"], "0.293103")

    def test_duplicate_bureau_is_ignored(self):
        row = election_row(
            "01",
            "Ain",
            candidate(7, "MELENCHON", "Jean Luc", "17"),
        )
        duplicate = row.copy()
        duplicate[5] = "101"

        old_source = maps.PRESIDENTIELLE_T1
        maps.PRESIDENTIELLE_T1 = self.write_source([row, duplicate])
        self.addCleanup(setattr, maps, "PRESIDENTIELLE_T1", old_source)

        totals = maps.aggregate_melenchon_t1()

        self.assertEqual(totals["01"]["bureaux"], 1)
        self.assertEqual(totals["01"]["voix_melenchon"], 17)


if __name__ == "__main__":
    unittest.main()
