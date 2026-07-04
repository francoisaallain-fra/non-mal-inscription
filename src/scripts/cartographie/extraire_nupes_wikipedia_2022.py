import argparse
import csv
import json
import re
import time
import unicodedata
from urllib.error import HTTPError
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[3]
DEPARTMENTS_CSV = ROOT / "data/04_analysis/insee/2022-mal-inscription-departements.csv"
OUTPUT_CSV = (
    ROOT
    / "data/04_analysis/elections/2022-legislatives-nupes-wikipedia-overrides.csv"
)
QA_MISSING = ROOT / "data/04_analysis/qa/2022-nupes-wikipedia-non-extraits.csv"

API_URL = "https://fr.wikipedia.org/w/api.php"
USER_AGENT = "non-mal-inscription/1.0 (recherche reproductible; contact via GitHub)"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extrait les totaux NUPES T1 et T2 des pages Wikipédia départementales."
    )
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--missing-output", type=Path, default=QA_MISSING)
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Délai en secondes entre deux appels à l'API (défaut : 0,5).",
    )
    return parser.parse_args()


def api_call(params):
    query = urlencode(
        {"format": "json", "formatversion": 2, "maxlag": 5, **params}
    )
    request = Request(f"{API_URL}?{query}", headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=60) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise
            retry_after = error.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else 2 ** attempt
            time.sleep(max(wait, 1))
    raise RuntimeError("échec inattendu de l'API Wikipédia")


def normalize(value):
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def load_departments():
    with DEPARTMENTS_CSV.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def existing_title_hints():
    if not OUTPUT_CSV.exists():
        return {}
    hints = {}
    with OUTPUT_CSV.open("r", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            source = row.get("source", "")
            prefix = "Wikipédia - "
            if source.startswith(prefix):
                hints[row["code_departement"]] = source[len(prefix) :]
    return hints


def find_article(department, hint=None):
    if hint:
        return hint

    name = department["libelle_departement"]
    response = api_call(
        {
            "action": "query",
            "list": "search",
            "srsearch": f'intitle:"Élections législatives de 2022" {name}',
            "srnamespace": 0,
            "srlimit": 10,
        }
    )
    candidates = [
        item["title"]
        for item in response["query"]["search"]
        if "Élections législatives de 2022" in item["title"]
    ]
    if not candidates:
        raise ValueError("aucune page trouvée")

    normalized_name = normalize(name)
    matching = [title for title in candidates if normalized_name in normalize(title)]
    return matching[0] if matching else candidates[0]


def fetch_revisions(titles):
    response = api_call(
        {
            "action": "query",
            "prop": "revisions",
            "rvprop": "ids|timestamp|content",
            "rvslots": "main",
            "titles": "|".join(titles),
        }
    )
    revisions = {}
    for page in response["query"]["pages"]:
        if page.get("missing"):
            continue
        revision = page["revisions"][0]
        revisions[page["title"]] = {
            "title": page["title"],
            "pageid": page["pageid"],
            "revid": revision["revid"],
            "timestamp": revision["timestamp"],
            "content": revision["slots"]["main"]["content"],
        }
    return revisions


def extract_balanced_template(content, marker="{{Infobox Élection"):
    start = content.lower().find(marker.lower())
    if start < 0:
        raise ValueError("infobox élection introuvable")
    depth = 0
    index = start
    while index < len(content) - 1:
        pair = content[index : index + 2]
        if pair == "{{":
            depth += 1
            index += 2
            continue
        if pair == "}}":
            depth -= 1
            index += 2
            if depth == 0:
                return content[start:index]
            continue
        index += 1
    raise ValueError("infobox élection non refermée")


def infobox_parameters(template):
    params = {}
    current_key = None
    for line in template.splitlines()[1:]:
        match = re.match(r"\s*\|\s*([^=]+?)\s*=\s*(.*)$", line)
        if match:
            current_key = re.sub(r"\s+", " ", match.group(1).strip().lower())
            params[current_key] = match.group(2).strip()
        elif current_key:
            params[current_key] += "\n" + line.strip()
    return params


def clean_number(value, decimal=False):
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    value = re.sub(r"\{\{\s*formatnum\s*:\s*([^}|]+).*?\}\}", r"\1", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("&nbsp;", " ").replace("\xa0", " ")
    value = re.sub(r"[^0-9,.\-]", "", value)
    if decimal:
        return float(value.replace(",", "."))
    return int(re.sub(r"[^0-9]", "", value))


def extract_nupes(content):
    params = infobox_parameters(extract_balanced_template(content))

    # Le logo et la couleur identifient l'entrée de coalition officielle.
    # Ils évitent d'additionner les candidatures explicitement dissidentes.
    official_indexes = set()
    for key, value in params.items():
        match = re.fullmatch(r"(?:image|couleur)(\d+)", key)
        if match and re.search(
            r"NUPES|Nouvelle Union populaire écologique et sociale",
            value,
            flags=re.I,
        ):
            official_indexes.add(match.group(1))

    candidate_indexes = official_indexes
    if not candidate_indexes:
        for key, value in params.items():
            match = re.fullmatch(r"parti(\d+)", key)
            if match and re.search(
                r"NUPES|Nouvelle Union populaire écologique et sociale",
                value,
                flags=re.I,
            ) and not re.search(r"dissident", value, flags=re.I):
                candidate_indexes.add(match.group(1))

    if not candidate_indexes:
        raise ValueError("coalition NUPES introuvable dans l'infobox")
    if len(candidate_indexes) > 1:
        raise ValueError("plusieurs entrées NUPES possibles dans l'infobox")

    index = candidate_indexes.pop()
    votes_t1_keys = [f"votes{index}", f"vote électoral{index}"]
    percentage_t1_keys = [f"pourcentage{index}"]
    votes_t2_keys = [f"votes2v{index}", f"votes 2v{index}", f"vote électoral2{index}"]
    percentage_t2_keys = [f"pourcentage2v{index}", f"pourcentage 2v{index}"]

    votes_t1_value = next((params[key] for key in votes_t1_keys if key in params), None)
    percentage_t1_value = next(
        (params[key] for key in percentage_t1_keys if key in params), None
    )
    votes_t2_value = next((params[key] for key in votes_t2_keys if key in params), None)
    percentage_t2_value = next(
        (params[key] for key in percentage_t2_keys if key in params), None
    )
    if votes_t2_value is not None and not str(votes_t2_value).strip():
        votes_t2_value = None
    if percentage_t2_value is not None and not str(percentage_t2_value).strip():
        percentage_t2_value = None

    if votes_t1_value is None or percentage_t1_value is None:
        raise ValueError(
            f"voix ou pourcentage absent pour l'entrée NUPES n°{index}"
        )

    # Quand l'infobox identifie une entrée NUPES mais ne renseigne aucun champ
    # de second tour, on code explicitement 0 : cela signifie que cette entrée
    # de coalition n'a pas de total au T2 dans la page Wikipédia.
    if votes_t2_value is None and percentage_t2_value is None:
        votes_t2 = 0
        percentage_t2 = 0.0
    else:
        votes_t2 = clean_number(votes_t2_value) if votes_t2_value else None
        percentage_t2 = (
            clean_number(percentage_t2_value, decimal=True)
            if percentage_t2_value
            else None
        )

    return {
        "voix_t1": clean_number(votes_t1_value),
        "pourcentage_t1": clean_number(percentage_t1_value, decimal=True),
        "voix_t2": votes_t2,
        "pourcentage_t2": percentage_t2,
    }


def article_url(title, revid):
    return (
        "https://fr.wikipedia.org/w/index.php?"
        + urlencode({"title": title, "oldid": revid}, quote_via=quote)
    )


def main():
    args = parse_args()
    departments = load_departments()
    hints = existing_title_hints()
    rows = []
    missing = []
    articles = {}

    for department in departments:
        code = department["code_departement"]
        try:
            articles[code] = find_article(department, hints.get(code))
        except Exception as error:
            missing.append(
                {
                    "code_departement": code,
                    "libelle_departement": department["libelle_departement"],
                    "raison": f"recherche de page : {error}",
                }
            )

    revisions = {}
    article_titles = list(dict.fromkeys(articles.values()))
    for offset in range(0, len(article_titles), 20):
        batch = article_titles[offset : offset + 20]
        revisions.update(fetch_revisions(batch))
        if offset + 20 < len(article_titles):
            time.sleep(args.delay)

    for department in departments:
        code = department["code_departement"]
        if code not in articles:
            continue
        title = articles[code]
        try:
            revision = revisions.get(title)
            if not revision:
                raise ValueError("page ou révision absente de la réponse groupée")
            nupes = extract_nupes(revision["content"])
            rows.append(
                {
                    "code_departement": code,
                    "voix_nupes_wikipedia_t1": nupes["voix_t1"],
                    "pourcentage_nupes_wikipedia_t1": f"{nupes['pourcentage_t1']:.2f}",
                    "voix_nupes_wikipedia_t2": (
                        nupes["voix_t2"] if nupes["voix_t2"] is not None else ""
                    ),
                    "pourcentage_nupes_wikipedia_t2": (
                        f"{nupes['pourcentage_t2']:.2f}"
                        if nupes["pourcentage_t2"] is not None
                        else ""
                    ),
                    "source": f"Wikipédia - {revision['title']}",
                    "methode": "total_coalition_wikipedia",
                    "url_revision": article_url(
                        revision["title"], revision["revid"]
                    ),
                    "revision_id": revision["revid"],
                    "revision_timestamp": revision["timestamp"],
                }
            )
        except Exception as error:
            missing.append(
                {
                    "code_departement": code,
                    "libelle_departement": department["libelle_departement"],
                    "raison": str(error),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = [
            "code_departement",
            "voix_nupes_wikipedia_t1",
            "pourcentage_nupes_wikipedia_t1",
            "voix_nupes_wikipedia_t2",
            "pourcentage_nupes_wikipedia_t2",
            "source",
            "methode",
            "url_revision",
            "revision_id",
            "revision_timestamp",
        ]
        writer = csv.DictWriter(
            stream, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["code_departement"]))

    args.missing_output.parent.mkdir(parents=True, exist_ok=True)
    with args.missing_output.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = ["code_departement", "libelle_departement", "raison"]
        writer = csv.DictWriter(
            stream, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(missing)

    print(f"Pages extraites : {len(rows)}")
    print(f"Pages non extraites : {len(missing)}")
    print(f"CSV : {args.output}")
    print(f"Contrôle : {args.missing_output}")
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
