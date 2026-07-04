import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_GEOJSON = (
    ROOT
    / "data/04_analysis/cartographie/2022-departements-mal-inscription-melenchon.geojson"
)
OUTPUT_HTML = (
    ROOT / "maps/2022-nuage-points-mal-inscrits-melenchon-departements.html"
)


def average_ranks(values):
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start
        while end + 1 < len(ordered) and ordered[end + 1][1] == ordered[start][1]:
            end += 1
        average = (start + end) / 2
        for position in range(start, end + 1):
            ranks[ordered[position][0]] = average
        start = end + 1
    return ranks


def correlation(xs, ys):
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
    )
    return numerator / denominator


def linear_regression(xs, ys):
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum(
        (x - mean_x) ** 2 for x in xs
    )
    return slope, mean_y - slope * mean_x


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def load_rows():
    data = json.loads(INPUT_GEOJSON.read_text(encoding="utf-8"))
    rows = []
    for feature in data["features"]:
        properties = feature["properties"]
        required = [
            properties.get("part_melenchon_exprimes"),
            properties.get("part_mal_inscrits"),
            properties.get("score_croise"),
        ]
        if not all(isinstance(value, (int, float)) for value in required):
            continue
        rows.append(
            {
                "code": properties["code_departement"],
                "nom": properties["libelle_departement"],
                "melenchon": properties["part_melenchon_exprimes"] * 100,
                "mal": properties["part_mal_inscrits"] * 100,
                "score": properties["score_croise"],
                "couleur": properties["_color_cross"],
                "mal_inscrits_estimes": (
                    properties["part_mal_inscrits"] * properties["inscrits"]
                    if isinstance(properties.get("inscrits"), (int, float))
                    else None
                ),
                "voix_melenchon": properties.get("voix_melenchon"),
                "source_melenchon": properties.get("source_melenchon", ""),
            }
        )
    return rows


def build_html(rows):
    xs = [row["melenchon"] for row in rows]
    ys = [row["mal"] for row in rows]
    pearson = correlation(xs, ys)
    spearman = correlation(average_ranks(xs), average_ranks(ys))
    slope, intercept = linear_regression(xs, ys)
    median_x = median(xs)
    median_y = median(ys)

    label_codes = {
        row["code"] for row in sorted(rows, key=lambda row: row["score"], reverse=True)[:10]
    }
    for row in rows:
        row["etiquette"] = row["code"] in label_codes

    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nuage de points mal-inscription x vote Mélenchon en 2022</title>
  <style>
    :root {{
      color-scheme: light;
      --ink:#1f2529; --muted:#667078; --line:#d9dddf; --paper:#fff; --wash:#f5f6f3; --accent:#194f70;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--wash); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    header {{ padding:18px 24px 14px; background:var(--paper); border-bottom:1px solid var(--line); }}
    h1 {{ margin:0; max-width:1050px; font-size:23px; line-height:1.2; letter-spacing:0; }}
    header p {{ margin:7px 0 0; color:var(--muted); font-size:14px; }}
    main {{ display:grid; grid-template-columns:minmax(0,1fr) 320px; min-height:calc(100vh - 92px); }}
    .plot-wrap {{ min-width:0; padding:18px 12px 12px 18px; }}
    .toolbar {{ min-height:38px; display:flex; align-items:center; gap:18px; flex-wrap:wrap; padding:0 8px 10px; color:#434b50; font-size:13px; }}
    .toolbar label {{ display:inline-flex; align-items:center; gap:7px; cursor:pointer; }}
    input {{ accent-color:var(--accent); }}
    #chart {{ display:block; width:100%; height:min(760px,calc(100vh - 158px)); min-height:520px; background:var(--paper); border:1px solid var(--line); }}
    aside {{ padding:20px; background:var(--paper); border-left:1px solid var(--line); }}
    aside h2 {{ margin:0 0 12px; font-size:17px; letter-spacing:0; }}
    .metric {{ padding:12px 0; border-top:1px solid #eceeef; }}
    .metric strong {{ display:block; margin-bottom:3px; font-size:24px; color:var(--accent); }}
    .metric span,.note {{ color:var(--muted); font-size:13px; line-height:1.45; }}
    #selection {{ margin:18px 0; padding:14px; border:1px solid var(--line); border-radius:6px; background:#fafafa; min-height:126px; }}
    #selection strong {{ display:block; margin-bottom:8px; font-size:16px; }}
    #selection div {{ margin:4px 0; font-size:13px; }}
    .legend {{ margin:16px 0; }}
    .legend-bar {{ height:14px; border:1px solid #c9cdca; background:linear-gradient(90deg,#b2182b,#f7f7d4 50%,#1a9850); }}
    .legend-labels {{ display:flex; justify-content:space-between; margin-top:5px; color:var(--muted); font-size:11px; }}
    .grid {{ stroke:#e7e9e9; stroke-width:1; }}
    .axis {{ stroke:#7f888d; stroke-width:1.2; }}
    .median {{ stroke:#8c969b; stroke-width:1; stroke-dasharray:5 5; }}
    .regression {{ stroke:#174f70; stroke-width:2.2; }}
    .tick-label,.axis-label {{ fill:#59636a; font-size:12px; }}
    .axis-label {{ font-size:13px; font-weight:600; }}
    .point {{ stroke:#fff; stroke-width:1.3; cursor:pointer; transition:opacity 120ms ease; }}
    .point:hover,.point.selected {{ stroke:#111; stroke-width:2.2; }}
    .point-label {{ fill:#30383d; font-size:10px; font-weight:700; pointer-events:none; paint-order:stroke; stroke:#fff; stroke-width:3px; stroke-linejoin:round; }}
    #tooltip {{ position:fixed; z-index:10; display:none; pointer-events:none; padding:8px 10px; border:1px solid #bcc2c5; border-radius:4px; background:rgba(255,255,255,.97); box-shadow:0 4px 16px rgba(0,0,0,.12); font-size:12px; line-height:1.4; }}
    @media (max-width:900px) {{ main {{ grid-template-columns:1fr; }} aside {{ border-left:0; border-top:1px solid var(--line); }} #chart {{ height:580px; min-height:480px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Mal-inscription et vote Mélenchon au premier tour de la présidentielle de 2022</h1>
    <p>Un point par département · couleur : score croisé par moyenne géométrique des rangs percentiles</p>
  </header>
  <main>
    <section class="plot-wrap">
      <div class="toolbar">
        <label><input id="labels" type="checkbox"> Afficher tous les codes</label>
        <label><input id="regression" type="checkbox" checked> Droite de régression</label>
        <label><input id="medians" type="checkbox" checked> Médianes</label>
      </div>
      <svg id="chart" role="img" aria-label="Nuage de points des départements"></svg>
    </section>
    <aside>
      <h2>Relation statistique</h2>
      <div class="metric"><strong>{pearson:.3f}</strong><span>Corrélation de Pearson : relation linéaire entre les valeurs.</span></div>
      <div class="metric"><strong>{spearman:.3f}</strong><span>Corrélation de Spearman : association entre les rangs.</span></div>
      <div id="selection"><strong>Sélection</strong><div>Cliquez sur un département.</div></div>
      <div class="legend"><div class="legend-bar"></div><div class="legend-labels"><span>Score croisé faible</span><span>élevé</span></div></div>
      <p class="note">
        Population analysée : {len(rows)} départements disposant des deux taux.
        Ces corrélations départementales ne permettent pas de conclure au comportement individuel des mal-inscrits.
      </p>
      <p class="note">
        Sources : Insee Première n°1986, figure 4 ; ministère de l'Intérieur via Hexagonal, présidentielle 2022 T1.
      </p>
    </aside>
  </main>
  <div id="tooltip"></div>
  <script>
    const data = {payload};
    const stats = {{ slope:{slope:.12f}, intercept:{intercept:.12f}, medianX:{median_x:.12f}, medianY:{median_y:.12f} }};
    const svg = document.getElementById("chart");
    const tooltip = document.getElementById("tooltip");
    const selection = document.getElementById("selection");
    const ns = "http://www.w3.org/2000/svg";
    function node(name, attrs = {{}}, text = "") {{
      const element = document.createElementNS(ns, name);
      Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value));
      if (text) element.textContent = text;
      return element;
    }}
    function pct(value, digits = 1) {{
      return value.toLocaleString("fr-FR", {{ minimumFractionDigits:digits, maximumFractionDigits:digits }}) + " %";
    }}
    function render() {{
      svg.replaceChildren();
      const box = svg.getBoundingClientRect();
      const width = Math.max(720, box.width);
      const height = Math.max(480, box.height);
      svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);
      const margin = {{ top:28, right:34, bottom:62, left:70 }};
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;
      const minX = Math.floor((Math.min(...data.map(d => d.melenchon)) - 2) / 5) * 5;
      const maxX = Math.ceil((Math.max(...data.map(d => d.melenchon)) + 2) / 5) * 5;
      const minY = Math.floor((Math.min(...data.map(d => d.mal)) - 1) / 2) * 2;
      const maxY = Math.ceil((Math.max(...data.map(d => d.mal)) + 1) / 2) * 2;
      const x = value => margin.left + (value - minX) / (maxX - minX) * innerWidth;
      const y = value => margin.top + innerHeight - (value - minY) / (maxY - minY) * innerHeight;
      for (let value = Math.ceil(minX / 5) * 5; value <= maxX; value += 5) {{
        svg.append(node("line", {{x1:x(value), y1:margin.top, x2:x(value), y2:margin.top+innerHeight, class:"grid"}}));
        svg.append(node("text", {{x:x(value), y:margin.top+innerHeight+22, "text-anchor":"middle", class:"tick-label"}}, pct(value, 0)));
      }}
      for (let value = Math.ceil(minY / 2) * 2; value <= maxY; value += 2) {{
        svg.append(node("line", {{x1:margin.left, y1:y(value), x2:margin.left+innerWidth, y2:y(value), class:"grid"}}));
        svg.append(node("text", {{x:margin.left-11, y:y(value)+4, "text-anchor":"end", class:"tick-label"}}, pct(value, 0)));
      }}
      svg.append(node("line", {{x1:margin.left, y1:margin.top+innerHeight, x2:margin.left+innerWidth, y2:margin.top+innerHeight, class:"axis"}}));
      svg.append(node("line", {{x1:margin.left, y1:margin.top, x2:margin.left, y2:margin.top+innerHeight, class:"axis"}}));
      svg.append(node("text", {{x:margin.left+innerWidth/2, y:height-16, "text-anchor":"middle", class:"axis-label"}}, "Vote Mélenchon parmi les suffrages exprimés"));
      svg.append(node("text", {{x:18, y:margin.top+innerHeight/2, transform:`rotate(-90 18 ${{margin.top+innerHeight/2}})`, "text-anchor":"middle", class:"axis-label"}}, "Part de mal-inscrits"));
      const medians = node("g", {{id:"median-lines"}});
      medians.append(node("line", {{x1:x(stats.medianX), y1:margin.top, x2:x(stats.medianX), y2:margin.top+innerHeight, class:"median"}}));
      medians.append(node("line", {{x1:margin.left, y1:y(stats.medianY), x2:margin.left+innerWidth, y2:y(stats.medianY), class:"median"}}));
      svg.append(medians);
      svg.append(node("line", {{id:"regression-line", x1:x(minX), y1:y(stats.slope * minX + stats.intercept), x2:x(maxX), y2:y(stats.slope * maxX + stats.intercept), class:"regression"}}));
      data.forEach(d => {{
        const circle = node("circle", {{cx:x(d.melenchon), cy:y(d.mal), r:6.2, fill:d.couleur, class:"point", tabindex:"0", "aria-label":`${{d.nom}}, vote Mélenchon ${{pct(d.melenchon,2)}}, mal-inscrits ${{pct(d.mal)}}`}});
        const showTooltip = event => {{
          tooltip.style.display = "block";
          tooltip.innerHTML = `<strong>${{d.nom}} (${{d.code}})</strong><br>Mélenchon : ${{pct(d.melenchon,2)}}<br>Mal-inscrits : ${{pct(d.mal)}}<br>Score croisé : ${{d.score.toFixed(3).replace(".",",")}}`;
          tooltip.style.left = `${{Math.min(event.clientX + 14, window.innerWidth - 190)}}px`;
          tooltip.style.top = `${{Math.min(event.clientY + 14, window.innerHeight - 110)}}px`;
        }};
        circle.addEventListener("mousemove", showTooltip);
        circle.addEventListener("mouseenter", showTooltip);
        circle.addEventListener("mouseleave", () => tooltip.style.display = "none");
        circle.addEventListener("click", () => {{
          svg.querySelectorAll(".point.selected").forEach(point => point.classList.remove("selected"));
          circle.classList.add("selected");
          selection.innerHTML = `<strong>${{d.nom}} (${{d.code}})</strong>
            <div>Vote Mélenchon : <b>${{pct(d.melenchon,2)}}</b></div>
            <div>Mal-inscrits : <b>${{pct(d.mal)}}</b></div>
            <div>Score croisé : <b>${{d.score.toFixed(3).replace(".",",")}}</b></div>
            <div>Mal-inscrits estimés : <b>${{d.mal_inscrits_estimes?.toLocaleString("fr-FR", {{maximumFractionDigits:0}}) ?? "n.d."}}</b></div>
            <div>Voix Mélenchon : <b>${{d.voix_melenchon?.toLocaleString("fr-FR") ?? "n.d."}}</b></div>`;
        }});
        svg.append(circle);
        const label = node("text", {{x:x(d.melenchon)+8, y:y(d.mal)-7, class:"point-label", "data-default":d.etiquette ? "1" : "0"}}, d.code);
        label.style.display = d.etiquette ? "" : "none";
        svg.append(label);
      }});
      document.getElementById("labels").dispatchEvent(new Event("change"));
      document.getElementById("regression").dispatchEvent(new Event("change"));
      document.getElementById("medians").dispatchEvent(new Event("change"));
    }}
    document.getElementById("labels").addEventListener("change", event => {{
      svg.querySelectorAll(".point-label").forEach(label => {{
        label.style.display = event.target.checked || label.dataset.default === "1" ? "" : "none";
      }});
    }});
    document.getElementById("regression").addEventListener("change", event => {{
      const line = document.getElementById("regression-line");
      if (line) line.style.display = event.target.checked ? "" : "none";
    }});
    document.getElementById("medians").addEventListener("change", event => {{
      const lines = document.getElementById("median-lines");
      if (lines) lines.style.display = event.target.checked ? "" : "none";
    }});
    let resizeTimer;
    window.addEventListener("resize", () => {{
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(render, 120);
    }});
    render();
  </script>
</body>
</html>
"""


def main():
    rows = load_rows()
    if len(rows) < 3:
        raise SystemExit("Pas assez de départements comparables.")
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(build_html(rows), encoding="utf-8")

    xs = [row["melenchon"] for row in rows]
    ys = [row["mal"] for row in rows]
    print(f"Départements : {len(rows)}")
    print(f"Pearson : {correlation(xs, ys):.6f}")
    print(f"Spearman : {correlation(average_ranks(xs), average_ranks(ys)):.6f}")
    print(f"Nuage de points : {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
