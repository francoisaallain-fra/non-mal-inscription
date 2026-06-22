from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent
MAP_HTML = (
    ROOT
    / "maps/2022-croisement-mal-inscrits-nupes-departements-coalition-web.html"
)
SCATTER_HTML = (
    ROOT / "maps/2022-nuage-points-mal-inscrits-nupes-departements.html"
)


@st.cache_data
def read_html(path):
    return path.read_text(encoding="utf-8")


st.set_page_config(
    page_title="Mal-inscription x vote NUPES 2022",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Mal-inscription et vote NUPES en 2022")
st.caption(
    "Analyse départementale du premier tour des élections législatives de 2022"
)

map_tab, scatter_tab, method_tab = st.tabs(
    ["Carte départementale", "Nuage de points", "Méthodologie"]
)

with map_tab:
    st.subheader("Indice croisé par département")
    st.write(
        "Rouge : niveau faible sur au moins une dimension. "
        "Vert : niveaux élevés simultanément de mal-inscription et de vote NUPES."
    )
    components.html(read_html(MAP_HTML), height=920, scrolling=True)
    st.download_button(
        "Télécharger la carte HTML",
        data=MAP_HTML.read_bytes(),
        file_name=MAP_HTML.name,
        mime="text/html",
    )

with scatter_tab:
    st.subheader("Relation entre mal-inscription et vote NUPES")
    st.write(
        "Chaque point représente un département. La couleur correspond au "
        "score croisé utilisé dans la carte."
    )
    components.html(read_html(SCATTER_HTML), height=900, scrolling=True)
    st.download_button(
        "Télécharger le nuage de points HTML",
        data=SCATTER_HTML.read_bytes(),
        file_name=SCATTER_HTML.name,
        mime="text/html",
    )

with method_tab:
    st.subheader("Lecture des indicateurs")
    st.markdown(
        """
**Mal-inscription**  
Part des électeurs inscrits dans une commune différente de leur commune de
résidence principale, d'après l'Insee Première n°1986.

**Vote NUPES**  
Part des suffrages exprimés obtenue par la coalition au premier tour des
législatives de 2022. Les totaux départementaux de coalition sont contrôlés
avec les pages Wikipédia et les résultats du ministère de l'Intérieur.

**Score croisé**

```text
score_croise =
    racine(score_percentile_mal_inscription
           x score_percentile_vote_nupes)
```

La moyenne géométrique exige qu'un département soit bien placé sur les deux
dimensions pour obtenir un score élevé.

**Corrélations du nuage de points**

- Pearson : **0,199**
- Spearman : **0,321**

La relation est positive mais limitée. Cette analyse territoriale ne permet
pas de conclure au comportement individuel des personnes mal inscrites.
"""
    )
    st.link_button(
        "Consulter le repository GitHub",
        "https://github.com/lfi-pee/non-mal-inscription",
    )

st.divider()
st.caption(
    "Sources : Insee, ministère de l'Intérieur, résultats de coalition "
    "contrôlés sur Wikipédia. Champ de la mal-inscription : France hors Mayotte."
)
