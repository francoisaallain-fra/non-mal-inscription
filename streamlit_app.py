from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent

ASSETS = {
    "figure_2": ROOT / "assets/notion/figure-2-insee-mal-inscription-2022.png",
    "scatter_nupes_t1": ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-t1-departements-bulles-sans-outliers.html",
    "scatter_nupes_t2": ROOT
    / "maps/2022-nuage-points-mal-inscrits-nupes-departements-bulles-sans-outliers.html",
    "scatter_melenchon": ROOT
    / "maps/2022-nuage-points-mal-inscrits-melenchon-departements-bulles-sans-outliers.html",
    "map_nupes_t1": ROOT
    / "maps/2022-croisement-mal-inscrits-nupes-departements-t1.html",
    "map_nupes_t2": ROOT
    / "maps/2022-croisement-mal-inscrits-nupes-departements-t2.html",
    "map_melenchon": ROOT
    / "maps/2022-croisement-mal-inscrits-melenchon-presidentielle-departements-web.html",
    "table_nupes_t1": ROOT / "top-25-departements-mal-inscrits-nupes-t1-2022.md",
    "table_nupes_t2": ROOT / "top-25-departements-mal-inscrits-nupes-t2-2022.md",
    "table_melenchon": ROOT / "top-25-departements-mal-inscrits-melenchon-2022.md",
}

SCATTERS = {
    "NUPES législatives 2022 T1": ASSETS["scatter_nupes_t1"],
    "NUPES législatives 2022 T2": ASSETS["scatter_nupes_t2"],
    "Mélenchon présidentielle 2022 T1": ASSETS["scatter_melenchon"],
}

MAPS = {
    "NUPES législatives 2022 T1": ASSETS["map_nupes_t1"],
    "NUPES législatives 2022 T2": ASSETS["map_nupes_t2"],
    "Mélenchon présidentielle 2022 T1": ASSETS["map_melenchon"],
}

TABLES = {
    "NUPES législatives 2022 T1": ASSETS["table_nupes_t1"],
    "NUPES législatives 2022 T2": ASSETS["table_nupes_t2"],
    "Mélenchon présidentielle 2022 T1": ASSETS["table_melenchon"],
}


@st.cache_data
def read_text(path: Path, mtime_ns: int) -> str:
    return path.read_text(encoding="utf-8")


def assert_assets_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in ASSETS.values() if not path.exists()]
    if not missing:
        return
    st.error("Fichiers de rendu introuvables dans le dépôt déployé.")
    st.code("\n".join(missing), language="text")
    st.stop()


def local_text(path: Path) -> str:
    return read_text(path, path.stat().st_mtime_ns)


def html_view(path: Path, height: int = 900) -> None:
    components.html(local_text(path), height=height, scrolling=True)
    st.download_button(
        "Télécharger le HTML",
        data=path.read_bytes(),
        file_name=path.name,
        mime="text/html",
        key=f"download-{path.name}",
    )


def markdown_view(path: Path) -> None:
    st.markdown(local_text(path))
    st.download_button(
        "Télécharger le tableau Markdown",
        data=path.read_bytes(),
        file_name=path.name,
        mime="text/markdown",
        key=f"download-{path.name}",
    )


def section(title: str) -> None:
    st.markdown(f"## {title}")


def callout(text: str) -> None:
    st.markdown(f'<div class="callout">{text}</div>', unsafe_allow_html=True)


st.set_page_config(
    page_title="Résumé mal-inscription x vote NUPES 2022",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

assert_assets_exist()

st.markdown(
    """
<style>
main .block-container {
  max-width: 1180px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}
h1, h2, h3 { letter-spacing: 0; }
h1 {
  font-size: 2.45rem;
  line-height: 1.08;
  margin-bottom: .35rem;
}
h2 {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.45rem;
  margin-top: 2.1rem;
}
p, li {
  font-size: 1.02rem;
  line-height: 1.62;
}
.intro {
  color: #4b5563;
  font-size: 1.08rem;
  line-height: 1.62;
  margin: .2rem 0 1.2rem;
}
.callout {
  border-left: 4px solid #174d6b;
  background: #f3f7f8;
  padding: 1rem 1.1rem;
  margin: 1.1rem 0 1.4rem;
  line-height: 1.58;
}
.source-note {
  color: #6b7280;
  font-size: .92rem;
}
div[data-testid="stMetricValue"] {
  font-size: 1.7rem;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Résumé mal-inscription x vote NUPES 2022")
st.markdown(
    """
<p class="intro">
Le pôle analyse électorale s’est réuni le samedi 30 mai sous un format
hackathon. Ce travail rassemble les résultats des réflexions au sujet de la
mal-inscription et de la non-inscription sur les listes électorales.
</p>
""",
    unsafe_allow_html=True,
)

st.caption(
    "Version Streamlit interactive inspirée de la page Notion fournie. "
    "Les cartes, nuages et tableaux Notion sont remplacés par les rendus HTML du dépôt ; "
    "la Figure 2 Insee est reprise comme image statique."
)

section("Contexte : des évolutions récentes sur la gestion des inscriptions")
st.markdown(
    """
Quelle piste d’analyse faut-il privilégier entre la mal-inscription et la
non-inscription ? Le groupe privilégie d’orienter davantage le travail vers la
mal-inscription. Depuis 2016, l’Insee centralise les listes électorales,
auparavant gérées par les communes, et assure la gestion du Répertoire électoral
unique (REU), ce qui a considérablement amélioré la qualité des données
disponibles sur l’inscription électorale.

Cette centralisation permet aujourd’hui la production de statistiques plus
fiables sur la mal-inscription. La non-inscription sur les listes électorales
est aujourd’hui devenue relativement rare, autour de 5 % au total, grâce aux
dispositifs d’inscription automatique mis en place ces dernières années. Les
populations concernées sont principalement certaines personnes naturalisées
récemment ou des électeurs plus âgés qui n’ont jamais actualisé leur situation
administrative.

Sur la mal-inscription, les données les plus récentes exploitables proviennent
des travaux réalisés à partir des élections municipales. L’Insee a notamment
publié une étude détaillée ainsi qu’une cartographie de la mal-inscription à
l’échelle nationale.
"""
)

section("Objectif : étudier la mal-inscription en 2022")
st.markdown(
    """
C’est dans ce contexte qu’il est décidé d’explorer une corrélation potentielle
entre cette mal-inscription en 2022 et le vote en faveur de la NUPES lors des
élections législatives de 2022. L’objectif général est de construire un premier
outil d’analyse territoriale permettant d’identifier les espaces où un fort
niveau de mal-inscription pourrait se combiner avec un niveau élevé de vote
NUPES, afin de dégager d’éventuelles priorités politiques ou militantes.

Trois sources de données sont croisées : l’étude de l’Insee sur la
mal-inscription observée autour de la présidentielle 2022, les résultats
Mélenchon au premier tour de la présidentielle, et les résultats NUPES des
législatives 2022.
"""
)

section("7,7 millions de personnes concernées, dont environ 4 millions entre 18 et 34 ans")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Mal-inscrits estimés", "7,7 M")
col_b.metric("Part des inscrits", "16,5 %")
col_c.metric("18-34 ans parmi les mal-inscrits", "52,6 %")

st.markdown(
    """
Premièrement, l’étude de l’Insee met en évidence l’ampleur du phénomène de
mal-inscription électorale, entendu ici dans une acception large : être inscrit
sur les listes électorales dans une commune différente de celle de sa résidence
principale. Sur les 47 millions de Français inscrits sur les listes électorales,
7,7 millions seraient concernés, soit environ un électeur inscrit sur six.

Ce volume important montre que la mal-inscription ne constitue pas un phénomène
marginal, mais un enjeu électoral et démocratique significatif. Cela n’implique
pas nécessairement l’abstention, mais peut devenir une barrière au vote le jour
du scrutin : déplacement empêché, difficulté à organiser une procuration,
incertitude sur le bureau de vote réellement praticable.
"""
)

st.image(
    ASSETS["figure_2"],
    caption="Figure 2 - Répartition des électeurs non inscrits dans leur commune de résidence principale selon le lieu de vie, l’âge et le mode de cohabitation en 2022. Source : Insee.",
    use_container_width=True,
)

st.markdown(
    """
L’infographie de l’Insee souligne que certaines catégories de population sont
particulièrement touchées. Les personnes ayant récemment déménagé sont fortement
concernées : une personne sur deux parmi celles ayant déménagé l’année précédente
est inscrite dans une commune différente de celle de sa résidence principale.

Ces éléments confirment l’importance de prendre en compte la mobilité
résidentielle, les trajectoires étudiantes et l’entrée dans la vie active pour
comprendre la mal-inscription. Ils donnent aussi un intérêt stratégique à une
analyse territoriale du phénomène, notamment si l’objectif est d’identifier des
espaces où un travail d’information, de réinscription ou de mobilisation
électorale pourrait être prioritaire.
"""
)

section("Mal-inscription, NUPES et Mélenchon : des relations territoriales proches")
callout(
    "Les données finales montrent que la mal-inscription est plus importante "
    "dans les territoires où la NUPES 2022 et le vote Mélenchon 2022 font de "
    "bons scores. Les nuages ci-dessous sont interactifs : survol et clic "
    "permettent d’inspecter les départements."
)

scatter_choice = st.segmented_control(
    "Nuage de points interactif",
    list(SCATTERS),
    default="NUPES législatives 2022 T1",
)
html_view(SCATTERS[scatter_choice], height=940)

st.markdown(
    """
Les deux croisements font remonter presque le même bloc territorial : 22
départements sur 25 sont communs dans les deux top 25. On retrouve notamment
Paris, la Haute-Garonne, le Rhône, la Seine-Saint-Denis, le Val-de-Marne, le
Val-d’Oise, la Gironde, les Bouches-du-Rhône, l’Hérault, la Loire-Atlantique,
l’Ille-et-Vilaine et l’Isère.

Dans le détail, les DOM et certains territoires populaires sont plus
spectaculaires côté présidentielle : Guyane, Guadeloupe, Martinique montent très
haut avec Mélenchon. Côté NUPES législatives, le signal est parfois atténué ou
transformé par les configurations locales. À l’inverse, la NUPES fait mieux
ressortir certains départements de gauche universitaire ou de coalition où le
score législatif dépasse nettement le score Mélenchon : Puy-de-Dôme,
Haute-Vienne, Loire-Atlantique, Ille-et-Vilaine, Calvados, Seine-Maritime.
"""
)

section("Carte croisée : identifier les territoires prioritaires")
st.markdown(
    """
Cette carte vise à représenter, à l’échelle départementale, les territoires où
se combinent des indices élevés de mal-inscription et de vote NUPES. Ce choix
se fonde sur l’hypothèse que la réduction de la mal-inscription dans les
départements favorables à la NUPES pourrait accentuer l’ampleur de ce vote, ou
au moins réduire une barrière pratique au vote dans des territoires
stratégiques.
"""
)

map_choice = st.segmented_control(
    "Carte interactive",
    list(MAPS),
    default="NUPES législatives 2022 T1",
)
html_view(MAPS[map_choice], height=960)

st.markdown(
    """
Parmi les départements qui ont un bon score de croisement mal-inscription et
vote NUPES 2022 ou Mélenchon 2022, certains ont aussi des réservoirs importants
en nombre de mal-inscrits : Paris, Bouches-du-Rhône, Rhône, Gironde, notamment.
Le tableau ci-dessous permet de passer du score territorial au volume estimé de
personnes concernées.
"""
)

section("Tableaux : top 25 des départements")
table_choice = st.segmented_control(
    "Tableau interactif",
    list(TABLES),
    default="NUPES législatives 2022 T1",
)
markdown_view(TABLES[table_choice])

section("Limites")
st.markdown(
    """
La définition de la mal-inscription de l’étude Insee 2022 est particulière. Elle
repose uniquement sur le fait d’être inscrit dans une commune différente de
celle de sa résidence principale. Mais la mal-inscription au sens large peut
également désigner des situations où une personne est inscrite à une mauvaise
adresse au sein même de sa commune de résidence principale. Ce second phénomène
semble toutefois avoir été réduit depuis que l’Insee est devenu gestionnaire des
données relatives aux inscriptions sur les listes électorales.

**Mal-inscription ≠ abstention.** La mal-inscription n’équivaut pas forcément à
de l’abstention, qu’elle soit structurelle ou conjoncturelle. Dans certaines
situations, elle favorise certainement l’abstention ; dans d’autres cas, comme
la mobilité étudiante régulière, elle peut au contraire être un facteur de
stabilité du vote.

L’échelle départementale est aussi insatisfaisante pour un usage de terrain.
Elle ne permet pas d’identifier précisément les communes, quartiers ou bureaux
de vote où la mal-inscription serait la plus forte. Pour des objectifs
opérationnels, une cartographie communale ou infra-communale serait beaucoup
plus utile.
"""
)

section("Conclusion : une carte pour l’action")
st.markdown(
    """
Le hackathon a permis de fournir une première base de travail utile autour du
croisement entre mal-inscription électorale et vote NUPES en 2022. La carte
obtenue constitue un outil exploratoire intéressant pour visualiser des
territoires où les deux phénomènes pourraient se recouper.

Elle permet aussi de poser les bases d’une réflexion stratégique sur les publics
et les espaces à cibler en priorité, notamment au regard de la forte proportion
de jeunes parmi les personnes mal inscrites. La prochaine étape consisterait à
stabiliser une définition opérationnelle de la mal-inscription, à approfondir
l’analyse qualitative et quantitative des liens entre mal-inscription et
abstention chez les 18-34 ans, puis à explorer une cartographie plus fine.
"""
)

section("Pistes d’action")
st.markdown(
    """
**Action 1.** La mal-inscription est corrélée à l’âge et à la mobilité
résidentielle. Il pourrait donc être pertinent de lancer, à la rentrée de
septembre-octobre 2026, une campagne de terrain contre la mal-inscription,
notamment dans les universités. Format possible : trois à quatre militant·e·s à
l’entrée principale d’une université ; une à deux personnes à une table avec un
ordinateur portable pour proposer aux passant·e·s de vérifier leur situation
d’inscription.

- Es-tu sûr·e d’être bien inscrit·e sur les listes électorales là où tu habites ?
- En avril-mai 2027, seras-tu chez tes parents ou dans ton logement personnel ?
- Es-tu en confiance avec tes parents ou des connaissances pour faire une procuration ?

Sur la question de l’âge, il y a, d’après l’Insee, un point de bascule statutaire
à 26 ans.
"""
)

st.info(
    "D’après l’Insee, les moins de 26 ans peuvent légalement rester inscrits "
    "dans la commune de leurs parents dans certains cas. Mais un déménagement "
    "durable implique généralement une nouvelle inscription, et les délais de "
    "régularisation peuvent créer une période de décalage entre résidence et "
    "commune d’inscription."
)

st.markdown(
    """
**Action 2.** À terme, les territoires ciblés pourraient être des territoires
prioritaires pour les caravanes populaires, des mobilisations militantes, voire
des meetings. Ces territoires pourraient être sélectionnés en croisant les
travaux des autres axes du pôle analyse électorale, notamment sur l’abstention
« de gauche » et les bassins de reports de voix pour le second tour.
"""
)

section("Remarques stratégiques")
st.markdown(
    """
Sur la question de la mal-inscription, notamment chez les jeunes et les
étudiant·es, il faudrait réfléchir à la stratégie électorale. Les étudiant·es
peuvent être confronté·es à une période de battement entre avril et juin, entre
la fin de leur année universitaire et le début de l’été.

Autant en avril, la probabilité qu’une part importante des étudiant·es soit dans
sa résidence principale universitaire est forte ; autant à partir de la mi-mai
et encore plus au mois de juin, une partie d’entre elles et eux n’est plus là :
vacances, job saisonnier, retour chez les parents.

Il faut donc éviter une doctrine trop descendante du type : inscrivez-vous dans
votre résidence principale. L’enjeu serait plutôt de demander aux personnes ce
qui correspond le mieux à leur situation : rester inscrites chez leurs parents,
ce qui offre une forme de stabilité, ou s’inscrire dans leur ville d’études, ce
qui peut être plus pratique lorsqu’elles y résident effectivement.

Cette question de temporalité et de sociogéographie recoupe des stratégies
politiques à arbitrer : présidentielle d’avril-mai, législatives de juin,
éventuelle dissolution, mobilité estivale, vote jeune urbain ou redistribution
du vote jeune vers des zones moins universitaires.
"""
)

section("Bibliographie")
st.markdown(
    """
**Mobilisée**

- Chantal Brutel (Insee). 2024. « Élection présidentielle 2022 : 16,5 % des
  électeurs inscrits l’étaient dans une autre commune que celle de leur résidence
  principale », *Insee Première* n°1986.

**Non mobilisée**

- Braconnier, Céline, Jean-Yves Dormagen, Ghislain Gabalda, et Xavier Niel.
  2016. « Sociologie de la mal-inscription et de ses conséquences sur la
  participation électorale ». *Revue française de sociologie* 57(1):17-44.
- Marchand, Laura et al. 2015. « Pistes pour mesurer la nature de la
  mal-inscription et comprendre ses effets différentiels sur la participation
  électorale ». Congrès AFSP Aix 2015.
"""
)

st.divider()
st.markdown(
    """
<p class="source-note">
Sources : Insee, ministère de l’Intérieur via Hexagonal, résultats de coalition
contrôlés sur Wikipédia. Champ de la mal-inscription : France hors Mayotte.
Page Notion source :
<a href="https://app.notion.com/p/francois-allain/R-sum-mal-inscription-x-vote-NUPES-2022-373be36b5cec801f97a2ca578a273267?source=copy_link">
Résumé mal-inscription x vote NUPES 2022</a>.
</p>
""",
    unsafe_allow_html=True,
)
