import json
import math
from pathlib import Path

import nuage_points_mal_inscrits_melenchon_2022 as melenchon
import nuage_points_mal_inscrits_nupes_2022 as nupes
from nuages_points_mal_inscrits_sans_outliers_2022 import (
    format_excluded,
    split_outliers,
)


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_NUPES = (
    ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-departements-bulles-sans-outliers.html"
)
OUTPUT_MELENCHON = (
    ROOT
    / "maps/2022-nuage-points-mal-inscrits-melenchon-departements-bulles-sans-outliers.html"
)


def format_int(value):
    return f"{round(value):,}".replace(",", " ")


def build_html(
    rows,
    excluded,
    x_key,
    vote_label,
    title,
    source_note,
    pearson,
    spearman,
):
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    excluded_text = format_excluded(excluded, x_key)
    volumes = [row["mal_inscrits_estimes"] for row in rows if row["mal_inscrits_estimes"]]
    min_volume = min(volumes)
    max_volume = max(volumes)
    legend_values = [
        min_volume,
        sorted(volumes)[len(volumes) // 2],
        max_volume,
    ]
    legend_payload = json.dumps(legend_values, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme:light; --ink:#1f2529; --muted:#667078; --line:#d9dddf; --paper:#fff; --wash:#f5f6f3; --accent:#194f70; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--wash); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    header {{ padding:18px 24px 14px; background:var(--paper); border-bottom:1px solid var(--line); }}
    h1 {{ margin:0; max-width:1120px; font-size:23px; line-height:1.2; letter-spacing:0; }}
    header p {{ margin:7px 0 0; color:var(--muted); font-size:14px; }}
    main {{ display:grid; grid-template-columns:minmax(0,1fr) 340px; min-height:calc(100vh - 92px); }}
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
    #selection {{ margin:18px 0; padding:14px; border:1px solid var(--line); border-radius:6px; background:#fafafa; min-height:150px; }}
    #selection strong {{ display:block; margin-bottom:8px; font-size:16px; }}
    #selection div {{ margin:4px 0; font-size:13px; }}
    .legend {{ margin:16px 0; }}
    .legend-bar {{ height:14px; border:1px solid #c9cdca; background:linear-gradient(90deg,#b2182b,#f7f7d4 50%,#1a9850); }}
    .legend-labels {{ display:flex; justify-content:space-between; margin-top:5px; color:var(--muted); font-size:11px; }}
    #size-legend svg {{ width:100%; height:92px; display:block; }}
    .grid {{ stroke:#e7e9e9; stroke-width:1; }}
    .axis {{ stroke:#7f888d; stroke-width:1.2; }}
    .median {{ stroke:#8c969b; stroke-width:1; stroke-dasharray:5 5; }}
    .regression {{ stroke:#174f70; stroke-width:2.2; }}
    .tick-label,.axis-label {{ fill:#59636a; font-size:12px; }}
    .axis-label {{ font-size:13px; font-weight:600; }}
    .point {{ stroke:#fff; stroke-width:1.3; cursor:pointer; fill-opacity:.82; transition:opacity 120ms ease; }}
    .point:hover,.point.selected {{ stroke:#111; stroke-width:2.2; fill-opacity:.95; }}
    .point-label {{ fill:#30383d; font-size:10px; font-weight:700; pointer-events:none; paint-order:stroke; stroke:#fff; stroke-width:3px; stroke-linejoin:round; }}
    #tooltip {{ position:fixed; z-index:10; display:none; pointer-events:none; padding:8px 10px; border:1px solid #bcc2c5; border-radius:4px; background:rgba(255,255,255,.97); box-shadow:0 4px 16px rgba(0,0,0,.12); font-size:12px; line-height:1.4; }}
    @media (max-width:900px) {{ main {{ grid-template-columns:1fr; }} aside {{ border-left:0; border-top:1px solid var(--line); }} #chart {{ height:580px; min-height:480px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>Un point par département · couleur : score croisé · surface : mal-inscrits estimés</p>
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
      <div class="metric"><strong>{pearson:.3f}</strong><span>Corrélation de Pearson, hors outliers.</span></div>
      <div class="metric"><strong>{spearman:.3f}</strong><span>Corrélation de Spearman, hors outliers.</span></div>
      <div id="selection"><strong>Sélection</strong><div>Cliquez sur un département.</div></div>
      <div class="legend"><div class="legend-bar"></div><div class="legend-labels"><span>Score croisé faible</span><span>élevé</span></div></div>
      <div class="metric" id="size-legend"><strong>Surface des bulles</strong><span>Nombre estimé de mal-inscrits.</span></div>
      <p class="note">Version sans outliers : exclusion par règle IQR 1,5 sur les deux axes. Départements exclus : {excluded_text}.</p>
      <p class="note">{source_note}</p>
    </aside>
  </main>
  <div id="tooltip"></div>
  <script>
    const data = {payload};
    const legendValues = {legend_payload};
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
      return value.toLocaleString("fr-FR", {{minimumFractionDigits:digits, maximumFractionDigits:digits}}) + " %";
    }}
    function integer(value) {{
      return value?.toLocaleString("fr-FR", {{maximumFractionDigits:0}}) ?? "n.d.";
    }}
    function correlation(xs, ys) {{
      const mx = xs.reduce((a,b)=>a+b,0) / xs.length;
      const my = ys.reduce((a,b)=>a+b,0) / ys.length;
      const num = xs.reduce((sum, x, i) => sum + (x - mx) * (ys[i] - my), 0);
      const den = Math.sqrt(xs.reduce((sum, x) => sum + (x - mx) ** 2, 0) * ys.reduce((sum, y) => sum + (y - my) ** 2, 0));
      return num / den;
    }}
    function regression(xs, ys) {{
      const mx = xs.reduce((a,b)=>a+b,0) / xs.length;
      const my = ys.reduce((a,b)=>a+b,0) / ys.length;
      const slope = xs.reduce((sum, x, i) => sum + (x - mx) * (ys[i] - my), 0) / xs.reduce((sum, x) => sum + (x - mx) ** 2, 0);
      return {{slope, intercept: my - slope * mx}};
    }}
    function median(values) {{
      const ordered = [...values].sort((a,b)=>a-b);
      const mid = Math.floor(ordered.length / 2);
      return ordered.length % 2 ? ordered[mid] : (ordered[mid - 1] + ordered[mid]) / 2;
    }}

    function renderSizeLegend(radius) {{
      const wrap = document.getElementById("size-legend");
      const chart = node("svg", {{viewBox:"0 0 300 92", "aria-hidden":"true"}});
      const baseline = 62;
      [legendValues[0], legendValues[1], legendValues[2]].forEach((value, index) => {{
        const r = radius(value);
        const x = 34 + index * 112;
        chart.append(node("circle", {{cx:x, cy:baseline-r, r:r, fill:"#8fb9c9", "fill-opacity":".35", stroke:"#487083"}}));
        chart.append(node("text", {{x:x, y:84, "text-anchor":"middle", class:"tick-label"}}, integer(value)));
      }});
      wrap.append(chart);
    }}

    function render() {{
      svg.replaceChildren();
      document.querySelector("#size-legend svg")?.remove();
      const box = svg.getBoundingClientRect();
      const width = Math.max(720, box.width);
      const height = Math.max(480, box.height);
      svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);

      const margin = {{top:28, right:34, bottom:62, left:70}};
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;
      const xs = data.map(d => d.x);
      const ys = data.map(d => d.mal);
      const volumes = data.map(d => d.mal_inscrits_estimes).filter(Boolean);
      const minX = Math.floor((Math.min(...xs) - 2) / 5) * 5;
      const maxX = Math.ceil((Math.max(...xs) + 2) / 5) * 5;
      const minY = Math.floor((Math.min(...ys) - 1) / 2) * 2;
      const maxY = Math.ceil((Math.max(...ys) + 1) / 2) * 2;
      const minVolume = Math.min(...volumes);
      const maxVolume = Math.max(...volumes);
      const x = value => margin.left + (value - minX) / (maxX - minX) * innerWidth;
      const y = value => margin.top + innerHeight - (value - minY) / (maxY - minY) * innerHeight;
      const radius = value => 4 + Math.sqrt((value - minVolume) / (maxVolume - minVolume)) * 18;
      const stats = regression(xs, ys);
      const medianX = median(xs);
      const medianY = median(ys);

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
      svg.append(node("text", {{x:margin.left+innerWidth/2, y:height-16, "text-anchor":"middle", class:"axis-label"}}, "{vote_label} parmi les suffrages exprimés"));
      svg.append(node("text", {{x:18, y:margin.top+innerHeight/2, transform:`rotate(-90 18 ${{margin.top+innerHeight/2}})`, "text-anchor":"middle", class:"axis-label"}}, "Part de mal-inscrits"));

      const medians = node("g", {{id:"median-lines"}});
      medians.append(node("line", {{x1:x(medianX), y1:margin.top, x2:x(medianX), y2:margin.top+innerHeight, class:"median"}}));
      medians.append(node("line", {{x1:margin.left, y1:y(medianY), x2:margin.left+innerWidth, y2:y(medianY), class:"median"}}));
      svg.append(medians);
      svg.append(node("line", {{id:"regression-line", x1:x(minX), y1:y(stats.slope * minX + stats.intercept), x2:x(maxX), y2:y(stats.slope * maxX + stats.intercept), class:"regression"}}));

      data.forEach(d => {{
        const circle = node("circle", {{cx:x(d.x), cy:y(d.mal), r:radius(d.mal_inscrits_estimes), fill:d.couleur, class:"point", tabindex:"0"}});
        const showTooltip = event => {{
          tooltip.style.display = "block";
          tooltip.innerHTML = `<strong>${{d.nom}} (${{d.code}})</strong><br>{vote_label} : ${{pct(d.x,2)}}<br>Mal-inscrits : ${{pct(d.mal)}}<br>Mal-inscrits estimés : ${{integer(d.mal_inscrits_estimes)}}<br>Score croisé : ${{d.score.toFixed(3).replace(".",",")}}`;
          tooltip.style.left = `${{Math.min(event.clientX + 14, window.innerWidth - 230)}}px`;
          tooltip.style.top = `${{Math.min(event.clientY + 14, window.innerHeight - 130)}}px`;
        }};
        circle.addEventListener("mousemove", showTooltip);
        circle.addEventListener("mouseenter", showTooltip);
        circle.addEventListener("mouseleave", () => tooltip.style.display = "none");
        circle.addEventListener("click", () => {{
          svg.querySelectorAll(".point.selected").forEach(point => point.classList.remove("selected"));
          circle.classList.add("selected");
          selection.innerHTML = `<strong>${{d.nom}} (${{d.code}})</strong>
            <div>{vote_label} : <b>${{pct(d.x,2)}}</b></div>
            <div>Mal-inscrits : <b>${{pct(d.mal)}}</b></div>
            <div>Score croisé : <b>${{d.score.toFixed(3).replace(".",",")}}</b></div>
            <div>Mal-inscrits estimés : <b>${{integer(d.mal_inscrits_estimes)}}</b></div>
            <div>Voix : <b>${{integer(d.voix)}}</b></div>`;
        }});
        svg.append(circle);
        const label = node("text", {{x:x(d.x)+radius(d.mal_inscrits_estimes)+4, y:y(d.mal)-7, class:"point-label", "data-default":d.etiquette ? "1" : "0"}}, d.code);
        label.style.display = d.etiquette ? "" : "none";
        svg.append(label);
      }});
      renderSizeLegend(radius);
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


def normalize_rows(rows, x_key, vote_key):
    normalized = []
    for row in rows:
        normalized.append(
            {
                **row,
                "x": row[x_key],
                "voix": row[vote_key],
            }
        )
    label_codes = {
        row["code"]
        for row in sorted(normalized, key=lambda row: row["score"], reverse=True)[:10]
    }
    for row in normalized:
        row["etiquette"] = row["code"] in label_codes
    return normalized


def write_chart(label, module, x_key, vote_key, vote_label, output_path, source_note):
    rows = module.load_rows()
    kept, excluded = split_outliers(rows, x_key)
    kept = normalize_rows(kept, x_key, vote_key)
    xs = [row["x"] for row in kept]
    ys = [row["mal"] for row in kept]
    pearson = module.correlation(xs, ys)
    spearman = module.correlation(module.average_ranks(xs), module.average_ranks(ys))
    output_path.write_text(
        build_html(
            kept,
            excluded,
            x_key,
            vote_label,
            f"Mal-inscription et vote {label} en 2022 - bulles sans outliers",
            source_note,
            pearson,
            spearman,
        ),
        encoding="utf-8",
    )
    print(f"{label}: {output_path}")
    print(f"{label}: {len(kept)} départements conservés, Pearson {pearson:.6f}, Spearman {spearman:.6f}")


def main():
    write_chart(
        "NUPES",
        nupes,
        "nupes",
        "voix_nupes",
        "NUPES",
        OUTPUT_NUPES,
        "Sources : Insee Première n°1986, figure 4 ; Wikipédia, pages départementales des législatives 2022, avec agrégats du ministère de l'Intérieur via Hexagonal conservés comme contrôle. Volume : part Insee de mal-inscrits × inscrits législatives 2022 T2.",
    )
    write_chart(
        "Mélenchon",
        melenchon,
        "melenchon",
        "voix_melenchon",
        "Mélenchon",
        OUTPUT_MELENCHON,
        "Sources : Insee Première n°1986, figure 4 ; ministère de l'Intérieur via Hexagonal, présidentielle 2022 T1. Volume : part Insee de mal-inscrits × inscrits présidentielle 2022.",
    )


if __name__ == "__main__":
    main()
