from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent

ASSETS = {
    "scatter_nupes_t2": ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-departements-bulles-sans-outliers.html",
    "scatter_nupes_t1": ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-t1-departements-bulles-sans-outliers.html",
    "scatter_melenchon": ROOT
    / "maps/2022-nuage-points-mal-inscrits-melenchon-departements-bulles-sans-outliers.html",
    "map_nupes_t2": ROOT
    / "maps/2022-croisement-mal-inscrits-nupes-departements-t2.html",
    "map_nupes_t1": ROOT
    / "maps/2022-croisement-mal-inscrits-nupes-departements-t1.html",
    "map_melenchon": ROOT
    / "maps/2022-croisement-mal-inscrits-melenchon-presidentielle-departements-web.html",
    "table_nupes_t2": ROOT / "top-25-departements-mal-inscrits-nupes-t2-2022.md",
    "table_nupes_t1": ROOT / "top-25-departements-mal-inscrits-nupes-t1-2022.md",
    "table_melenchon": ROOT / "top-25-departements-mal-inscrits-melenchon-2022.md",
}


@st.cache_data
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_assets_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in ASSETS.values() if not path.exists()]
    if not missing:
        return

    st.error("Fichiers de rendu introuvables dans le dépôt déployé.")
    st.code("\n".join(missing), language="text")
    st.stop()


def html_view(path: Path, height: int = 900) -> None:
    components.html(read_text(path), height=height, scrolling=True)
    st.download_button(
        "Télécharger le HTML",
        data=path.read_bytes(),
        file_name=path.name,
        mime="text/html",
        key=f"download-{path.name}",
    )


def markdown_view(path: Path) -> None:
    st.markdown(read_text(path))
    st.download_button(
        "Télécharger le tableau Markdown",
        data=path.read_bytes(),
        file_name=path.name,
        mime="text/markdown",
        key=f"download-{path.name}",
    )


st.set_page_config(
    page_title="Mal-inscription, NUPES et LFI en 2022",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

assert_assets_exist()

st.title("Mal-inscription, NUPES et LFI en 2022")
st.caption(
    "Croisements départementaux entre la mal-inscription Insee 2022, "
    "le vote NUPES aux législatives 2022 et le vote Mélenchon au premier tour de la présidentielle 2022."
)

scatter_tab, map_tab, table_tab, method_tab = st.tabs(
    ["Nuages sans outliers", "Cartes territorialisées", "Top 25", "Méthode"]
)

with scatter_tab:
    st.subheader("Nuages de points hors outliers")
    st.write(
        "Les axes montrent la part de vote et la part de mal-inscrits. "
        "La couleur représente le score croisé ; la surface de la bulle représente "
        "le nombre estimé de mal-inscrits dans le département."
    )
    choice = st.segmented_control(
        "Scrutin",
        [
            "NUPES législatives 2022 T2",
            "NUPES législatives 2022 T1",
            "Mélenchon présidentielle 2022 T1",
        ],
        default="NUPES législatives 2022 T2",
    )
    if choice == "NUPES législatives 2022 T2":
        html_view(ASSETS["scatter_nupes_t2"], height=920)
    elif choice == "NUPES législatives 2022 T1":
        html_view(ASSETS["scatter_nupes_t1"], height=920)
    else:
        html_view(ASSETS["scatter_melenchon"], height=920)

with map_tab:
    st.subheader("Cartes territorialisées")
    st.write(
        "Rouge : niveau faible sur au moins une dimension. "
        "Vert : niveaux élevés simultanément de mal-inscription et de vote."
    )
    choice = st.segmented_control(
        "Carte",
        [
            "NUPES législatives 2022 T2",
            "NUPES législatives 2022 T1",
            "Mélenchon présidentielle 2022 T1",
        ],
        default="NUPES législatives 2022 T2",
    )
    if choice == "NUPES législatives 2022 T2":
        html_view(ASSETS["map_nupes_t2"], height=920)
    elif choice == "NUPES législatives 2022 T1":
        html_view(ASSETS["map_nupes_t1"], height=920)
    else:
        html_view(ASSETS["map_melenchon"], height=920)

with table_tab:
    st.subheader("Top 25 des départements")
    st.write(
        "Classements selon la moyenne géométrique des rangs percentiles de "
        "mal-inscription et de vote."
    )
    choice = st.segmented_control(
        "Tableau",
        [
            "NUPES législatives 2022 T2",
            "NUPES législatives 2022 T1",
            "Mélenchon présidentielle 2022 T1",
        ],
        default="NUPES législatives 2022 T2",
    )
    if choice == "NUPES législatives 2022 T2":
        markdown_view(ASSETS["table_nupes_t2"])
    elif choice == "NUPES législatives 2022 T1":
        markdown_view(ASSETS["table_nupes_t1"])
    else:
        markdown_view(ASSETS["table_melenchon"])

with method_tab:
    st.subheader("Lecture des indicateurs")
    st.markdown(
        """
**Mal-inscription**  
Part des électeurs inscrits dans une commune différente de leur commune de
résidence principale, d'après l'Insee Première n°1986.

**Nombre estimé de mal-inscrits**  
Le volume affiché dans les nuages de points est calculé ainsi :

```text
part départementale de mal-inscription Insee × inscrits du scrutin
```

Il ne s'agit pas de l'ancienne approximation uniforme `mal-inscrits × 52 %`.

**Score croisé**

```text
score_croise =
    racine(score_percentile_mal_inscription
           × score_percentile_vote)
```

La moyenne géométrique exige qu'un département soit bien placé sur les deux
dimensions pour obtenir un score élevé.

**Outliers des nuages de points**  
Les versions publiées ici excluent les points extrêmes avec une règle IQR 1,5
sur les deux axes : vote et part de mal-inscrits.

**Limite d'interprétation**  
Cette analyse est territoriale. Elle montre des coïncidences départementales,
mais ne permet pas de conclure au comportement individuel des personnes
mal-inscrites.
"""
    )

st.divider()
st.caption(
    "Sources : Insee, ministère de l'Intérieur via Hexagonal, résultats de coalition "
    "contrôlés sur Wikipédia. Champ de la mal-inscription : France hors Mayotte."
)
