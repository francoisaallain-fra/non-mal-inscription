# Mal-inscription et vote NUPES aux législatives de 2022

Ce projet cartographie, à l'échelle départementale, deux dimensions de la
participation politique en 2022 :

- la part des électeurs inscrits dans une commune différente de leur commune de
  résidence principale ;
- la part des suffrages exprimés obtenue par la NUPES au premier ou au second
  tour des élections législatives.

L'objectif initial était de rechercher une relation territoriale entre
mal-inscription et vote NUPES, puis de rendre cette relation visible grâce à une
carte croisée allant du rouge, pour les territoires faibles sur les deux
variables, au vert, pour les territoires élevés sur les deux variables.

## App Streamlit

Une version web partageable est fournie dans [`streamlit_app.py`](streamlit_app.py).
Elle embarque les rendus HTML publics suivants :

- nuages de points NUPES 2022 T1/T2 et Mélenchon présidentielle 2022 T1, sans outliers ;
- cartes territorialisées NUPES 2022 T1/T2 et Mélenchon présidentielle 2022 T1 ;
- tableaux top 25 des départements.

Pour déployer sur Streamlit Community Cloud :

```text
Repository: francoisaallain-fra/non-mal-inscription
Branch: master
Main file path: streamlit_app.py
```

Les dépendances sont listées dans [`requirements.txt`](requirements.txt), et
la configuration visuelle Streamlit dans [`.streamlit/config.toml`](.streamlit/config.toml).

Le projet est aussi devenu un travail sur la qualité des données électorales :
les premières cartes ont révélé des résultats NUPES incomplets dans plusieurs
territoires. Les versions successives documentent les erreurs observées, les
corrections apportées et les limites qui demeurent.

## Point de départ

La première intention était de produire des cartes par bureau de vote. Les
résultats électoraux de 2022 sont disponibles à cette échelle dans les données
Hexagonal. En revanche, l'étude publique de l'Insee ne fournit pas de taux de
mal-inscription par bureau de vote.

La donnée publique la plus fine directement disponible dans l'étude est le
**département**, dans la figure 4 de l'Insee Première n°1986. Le projet a donc
été recentré sur cette échelle afin de ne pas attribuer artificiellement une
valeur départementale à chaque bureau de vote.

Cette décision permet une comparaison géographiquement cohérente :

```text
mal-inscription départementale
        x
vote NUPES agrégé au département
```

Le [plan initial par bureau de vote](plan-cartes-mal-inscrits-nupes-2022.md)
reste dans le dépôt pour documenter cette première piste et les données qui
seraient nécessaires pour la mener correctement.

## Définition de la mal-inscription

Dans les titres des cartes, le terme court « mal-inscription » est utilisé pour
faciliter la lecture. La variable mesurée par l'Insee est plus précisément :

> la part des électeurs inscrits sur les listes électorales d'une commune
> différente de leur commune de résidence principale.

Cette situation n'est pas toujours une mal-inscription au sens juridique. Elle
peut notamment concerner des jeunes encore inscrits chez leurs parents, des
personnes vivant en institution ou des électeurs ayant récemment déménagé.

Le champ de l'étude Insee est la France hors Mayotte, pour les personnes de
nationalité française âgées de 18 ans ou plus.

## Données mobilisées

### Sources Web

| Source | Utilisation | Adresse |
|---|---|---|
| Insee Première n°1986, figure 4 | Part départementale des personnes non inscrites dans leur commune de résidence principale | [insee.fr/fr/statistiques/7766966](https://www.insee.fr/fr/statistiques/7766966) |
| Insee RP2022, dossiers complets départementaux | Populations par âge et populations scolarisées utilisées dans le tableau Top 25 | [insee.fr/fr/statistiques/2011101](https://www.insee.fr/fr/statistiques/2011101) |
| Résultats du ministère de l'Intérieur, distribués dans Hexagonal | Résultats des législatives 2022 par bureau de vote, premier et second tours | [github.com/lafranceinsoumise/hexagonal](https://github.com/lafranceinsoumise/hexagonal) |
| Table de codage Legis-2022 distribuée dans Hexagonal | Identification complémentaire des candidats rattachés à la NUPES | [github.com/lafranceinsoumise/hexagonal](https://github.com/lafranceinsoumise/hexagonal) |
| Pages Wikipédia départementales des législatives de 2022 | Totaux de coalition NUPES aux premier et second tours, utilisés pour corriger les sous-comptes | [Résultats par département](https://fr.wikipedia.org/wiki/R%C3%A9sultats_par_d%C3%A9partement_des_%C3%A9lections_l%C3%A9gislatives_fran%C3%A7aises_de_2022) |

Les résultats du ministère constituent la source électorale officielle. Les
pages Wikipédia ont été utilisées comme source de **totaux de coalition** et
comme outil de contrôle, car la seule nuance ministérielle `NUP` ne permet pas
de retrouver partout le périmètre politique retenu pour la NUPES.

### Entrées locales nécessaires au script

Le script principal attend les fichiers bruts suivants :

```text
data/01_raw/insee/donnees_insee_premiere_n1986.xlsx
data/01_raw/ministere_interieur/2022-legislatives-1-bureau_de_vote.csv
data/01_raw/ministere_interieur/2022-legislatives-2-bureau_de_vote.csv
data/01_raw/legis_2022/2022-legislatives-nuances.csv
data/04_analysis/elections/2022-legislatives-nupes-wikipedia-overrides.csv
```

Ces entrées volumineuses ou intermédiaires ne sont pas toutes versionnées dans
ce dépôt. Elles ont été mobilisées localement depuis les téléchargements Insee,
les données Hexagonal et l'extraction des pages Wikipédia.

### Données versionnées dans ce dépôt

| Fichier | Contenu |
|---|---|
| [`data/04_analysis/geodata/departements-2022.geojson`](data/04_analysis/geodata/departements-2022.geojson) | Fond géographique départemental, avec outre-mer rapproché |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson) | Jointure finale de la méthode « coalition contrôlée » du premier tour |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t1-ministere-legis2022.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t1-ministere-legis2022.geojson) | Premier tour calculé uniquement avec les mêmes sources que le second tour |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson) | Jointure du second tour |
| [`data/04_analysis/elections/`](data/04_analysis/elections/) | Agrégats électoraux et table des valeurs Wikipédia |
| [`data/04_analysis/insee/2022-age-scolarisation-departements-top25.csv`](data/04_analysis/insee/2022-age-scolarisation-departements-top25.csv) | Populations 18-24, 25-29 et 30-44 ans et populations scolarisées du Top 25 |
| [`data/04_analysis/qa/`](data/04_analysis/qa/) | Contrôles de couverture et de totaux |

## Construction de l'indicateur NUPES

### Première méthode

La première méthode agrégeait par département les voix des candidats :

1. portant la nuance ministérielle `NUP` ;
2. ou identifiés comme NUPES dans la table Legis-2022.

Les indicateurs calculés sont :

```text
part_nupes_exprimes = voix_nupes / exprimes
part_nupes_inscrits = voix_nupes / inscrits
```

La carte principale utilise `part_nupes_exprimes`, qui mesure la préférence
électorale exprimée sans intégrer directement l'abstention.

Cette méthode reste conservée comme contrôle à sources constantes :

- premier tour : ministère de l'Intérieur + Legis-2022 ;
- second tour : ministère de l'Intérieur + Legis-2022.

### Limite découverte

Cette méthode était cohérente techniquement mais imparfaite politiquement. La
nuance administrative `NUP` ne recouvrait pas partout l'ensemble des candidats
présentés ou soutenus comme appartenant à la coalition NUPES.

Les premières cartes faisaient donc apparaître des valeurs manifestement
incomplètes, surtout dans les outre-mer, en Corse et dans quelques départements
métropolitains.

### Méthode « coalition contrôlée »

La méthode utilise ensemble le nombre de voix et le pourcentage de coalition
affichés sur la page Wikipédia départementale lorsqu'ils ont pu être extraits,
au premier comme au second tour.
Elle ne calcule plus un taux hybride avec un numérateur Wikipédia et un
dénominateur ministère.

La méthode devient :

```text
si voix et pourcentage de coalition Wikipédia disponibles :
    voix_nupes = total de coalition Wikipédia
    part_nupes_exprimes = pourcentage Wikipédia
sinon :
    voix_nupes = calcul ministère + Legis-2022
    part_nupes_exprimes = voix_nupes / exprimés ministère

si une correction de voix existe sans pourcentage source cohérent :
    part_nupes_exprimes = indisponible
```

Au terme du contrôle, 100 départements ou territoires utilisent un total de
coalition extrait de Wikipédia. Sept territoires conservent un repli sur les
totaux territoriaux déjà identifiés ; lorsque leur pourcentage de coalition
n'est pas disponible dans la même source, ils ne participent pas au classement
cartographique.

La colonne `exprimes` est conservée pour contrôler les données du ministère,
mais elle n'est pas utilisée pour recalculer les pourcentages Wikipédia. La
colonne `methode_part_nupes_exprimes` indique explicitement la méthode employée.

## Décisions prises après revue méthodologique

Trois commentaires de revue ont conduit aux changements suivants :

1. **Fin du ratio hybride Wikipédia/ministère.** Les pourcentages Wikipédia
   sont utilisés directement avec les voix Wikipédia. Une correction de voix
   dépourvue de pourcentage source cohérent reste sans taux.
2. **Fin du faux versionnement cartographique.** Les anciennes cartes V2 à V6,
   qui utilisaient toutes le même GeoJSON final, ont été retirées. Les versions
   restent uniquement comme historique de l'investigation.
3. **Moyenne géométrique pour le croisement.** Le score croisé est désormais
   `sqrt(score_mal_inscription * score_nupes)`, afin qu'un département ne soit
   considéré élevé que s'il l'est réellement sur les deux dimensions.
4. **Territorialisation de l'estimation des 18-34 ans.** L'application uniforme
   de 52 % à tous les départements est conservée uniquement comme ancienne
   méthode de comparaison. Une nouvelle estimation utilise les populations par
   âge propres à chaque département.
5. **Reproductibilité de l'extraction Wikipédia.** Le script ayant servi à
   produire les totaux départementaux est désormais versionné et enregistre
   l'URL, l'identifiant et la date de chaque révision utilisée.
6. **Fiabilisation du calcul candidat par candidat.** Les premier et second
   tours utilisent désormais un même moteur d'agrégation. Une voix vide dans
   un bloc candidat n'interrompt plus la lecture des candidats suivants ; les
   bureaux sont dédoublonnés par département, circonscription, commune et
   numéro de bureau ; `bureaux_avec_nupes` et les voix ne sont comptés qu'une
   fois par bureau. Les codes départementaux Insee suivent la même
   normalisation que les données électorales.

## Erreurs détectées et corrigées

### Outre-mer

Les premières versions ne faisaient pas correctement apparaître les résultats
NUPES ultramarins. Le cas de la Martinique a servi de test décisif :

```text
Martinique, premier tour :
23 286 voix
37,50 % des suffrages exprimés
```

La méthode fondée uniquement sur les nuances candidates sous-comptait fortement
ce résultat. Les totaux de coalition ont ensuite été intégrés pour la
Martinique et les autres territoires concernés.

### Corse

La première intégration Legis-2022 de la Corse restait incomplète. Les valeurs
de référence utilisées pour corriger la méthode sont :

```text
Corse-du-Sud : 4 667 voix, soit 9,47 %
Haute-Corse  : 4 828 voix, soit 8,54 %
```

Ces résultats sont désormais repris dans la méthode de coalition contrôlée depuis les pages Wikipédia
départementales.

### Meurthe-et-Moselle

La comparaison systématique avec Wikipédia a révélé la divergence la plus
importante en métropole :

```text
calcul candidat/nuance initial : 52 043 voix
total de coalition Wikipédia   : 68 436 voix
```

Le calcul initial omettait notamment un candidat classé administrativement
divers gauche mais intégré au total politique de coalition.

### Loire-Atlantique

La comparaison a aussi révélé un écart d'une voix :

```text
calcul initial : 182 739 voix
Wikipédia      : 182 738 voix
```

Même minime, cet écart a confirmé l'intérêt d'un contrôle département par
département plutôt que d'un simple contrôle national.

### Variantes de structure des pages Wikipédia

L'extraction initiale des pages Wikipédia cherchait uniquement un champ de type
`votesN`. Plusieurs infobox utilisaient plutôt `vote électoralN`.

Cette différence de structure empêchait d'extraire correctement plusieurs
départements, dont le Calvados, la Corse et la Martinique. L'extracteur a été
adapté aux deux variantes, faisant passer la couverture de 86 à 100
départements ou territoires.

### Codes géographiques

Le pipeline harmonise également :

- `2A` et `2B` pour la Corse ;
- les codes Hexagonal ultramarins comme `ZA`, `ZB`, `ZC` avec les codes Insee
  `971`, `972`, `973`, etc. ;
- les territoires sans géométrie départementale classique, affichés sous forme
  d'encarts schématiques.

Mayotte et plusieurs collectivités restent sans valeur de mal-inscription, car
elles ne sont pas couvertes par la figure départementale Insee utilisée.

## Évolution de l'investigation

| Version | Évolution principale |
|---|---|
| V1 | Agrégation initiale des résultats ministériels par département |
| V2 | Meilleure représentation de l'outre-mer |
| V3 | Correction des totaux ultramarins de coalition |
| V4 | Intégration complémentaire de la Corse via Legis-2022 |
| V5 | Correction explicite des totaux de Corse |
| V6 | Contrôle département par département avec les totaux de coalition Wikipédia |

Ces versions décrivent le cheminement de l'enquête sur les données. Elles ne
constituent plus des cartes publiées distinctes : dans le code initial, V2 à V6
étaient toutes régénérées avec le même GeoJSON final, malgré des titres
différents. Ces sorties redondantes ont été supprimées.

Les principales cartes sont :

- [mal-inscription par département](maps/2022-mal-inscrits-departements.html) ;
- [vote NUPES par département, coalition contrôlée](maps/2022-vote-nupes-departements.html) ;
- [vote NUPES, coalition contrôlée et palette inspirée de l'Insee](maps/2022-vote-nupes-departements-coalition-style-insee.html) ;
- [croisement mal-inscription x NUPES, coalition contrôlée](maps/2022-croisement-mal-inscrits-nupes-departements-coalition.html) ;
- [croisement mal-inscription x NUPES, version web allégée](maps/2022-croisement-mal-inscrits-nupes-departements-coalition-web.html) ;
- [croisement au premier tour, sources comparables au second tour](maps/2022-croisement-mal-inscrits-nupes-departements-t1-ministere-legis2022.html) ;
- [croisement au second tour](maps/2022-croisement-mal-inscrits-nupes-departements-t2.html) ;
- [nuage de points mal-inscription x vote NUPES](maps/2022-nuage-points-mal-inscrits-nupes-departements.html) ;
- [tableau des 25 départements les plus intéressants](top-25-departements-mal-inscrits-nupes-2022.md).

### Versions en ligne

Le dépôt est privé. Pour permettre le partage sans rendre son contenu public,
les deux visualisations suivantes sont publiées séparément sous forme de
fichiers HTML autonomes :

- [nuage de points en ligne](https://htmlpreview.github.io/?https://gist.githubusercontent.com/francoisaallain-fra/72d74b0fafba49ca3820bdb92919be67/raw/a72175e6a3f4dff7ffdbb0dea6a039f8e46cc05a/2022-nuage-points-mal-inscrits-nupes-departements.html) ;
- [carte croisée départementale en ligne](https://htmlpreview.github.io/?https://gist.githubusercontent.com/francoisaallain-fra/6dd245021ce8159d7901961bdf9c9a48/raw/81e3e09f541a74d75f0d3b68422aa609cebff712/2022-croisement-mal-inscrits-nupes-departements-coalition-web.html).

La carte en ligne utilise des contours géographiques simplifiés afin de
réduire le fichier d'environ 4,1 Mo à 393 Ko. Les valeurs, scores et couleurs
restent identiques.

### Application Streamlit

Les deux visualisations sont également intégrées dans une application
Streamlit :

```bash
streamlit run streamlit_app.py
```

L'application propose :

- un onglet pour la carte départementale ;
- un onglet pour le nuage de points ;
- une synthèse méthodologique ;
- le téléchargement des deux fichiers HTML autonomes.

## Méthode cartographique

### Carte croisée

Chaque variable est transformée en rang percentile parmi les départements :

```text
score_mal_inscription = rang percentile de part_mal_inscrits
score_nupes = rang percentile de part_nupes_exprimes
score_croise = racine(score_mal_inscription * score_nupes)
```

La moyenne géométrique est retenue afin de représenter une présence élevée
**simultanément** sur les deux dimensions. Contrairement à une moyenne
arithmétique, un score très élevé sur un axe compense moins facilement un score
très faible sur l'autre.

Le gradient est ensuite appliqué :

```text
rouge : niveau faible sur au moins une des deux dimensions
vert  : niveaux élevés de mal-inscription et de vote NUPES
```

Ce score reste exploratoire et ne constitue pas un test statistique.

## Tableau des 25 départements les plus intéressants

Après la production de la carte croisée, un tableau complémentaire a été
construit pour identifier les 25 départements arrivant en tête selon le même
score :

```text
score_croise = sqrt(score_mal_inscription * score_nupes)
```

Ce tableau est disponible ici :

```text
top-25-departements-mal-inscrits-nupes-2022.md
```

Il reprend, pour chaque département :

- le rang selon le score croisé ;
- la part de mal-inscription issue de l'Insee ;
- la part de vote NUPES au premier tour, méthode coalition contrôlée ;
- le score croisé ;
- un effectif estimé de personnes mal inscrites ;
- une estimation territorialisée des 18-34 ans mal inscrits ;
- l'ancienne projection uniforme à 52 %, conservée à titre de comparaison ;
- la population scolarisée de 18 à 29 ans.

### Reconstitution du nombre de mal-inscrits par département

L'étude Insee Première n°1986 fournit dans sa figure 4 la part départementale
des personnes inscrites dans une autre commune que leur commune de résidence
principale. Elle ne fournit pas, dans cette figure, l'effectif brut par
département.

Pour obtenir une approximation exploitable dans le tableau, l'effectif a donc
été reconstitué à partir des données déjà jointes dans le GeoJSON final :

```text
mal_inscrits_estimes =
    part_mal_inscrits_insee
    x inscrits_electoraux_du_departement
```

Exemple pour Paris :

```text
23,6 % x 1 362 500 inscrits environ = 321 550 mal-inscrits estimés
```

Le nombre d'inscrits utilisé provient des résultats électoraux agrégés au
département dans le jeu de carte, c'est-à-dire des fichiers du ministère de
l'Intérieur distribués via Hexagonal. Ce calcul donne donc un ordre de grandeur
cohérent avec la carte, mais pas un effectif Insee officiel publié tel quel par
département.

La ligne de total du tableau additionne les effectifs estimés des 25
départements affichés. Elle ne correspond pas à un total France entière. La part
totale de mal-inscription y est recalculée comme une moyenne pondérée par les
inscrits électoraux de ces 25 départements :

```text
part_mal_inscrits_top25 =
    somme(mal_inscrits_estimes)
    / somme(inscrits_electoraux)
```

### Estimation territorialisée des 18-34 ans mal inscrits

La méthode principale applique les taux nationaux par âge de la figure 3 de
l'étude Insee aux populations d'âge de chaque département :

```text
population 18-24 ans x 38,7 %
+ population 25-29 ans x 35,18 %
+ (population 30-44 ans / 3) x 30,9 %
```

Les données d'âge proviennent des dossiers complets départementaux RP2022 :

- les populations 18-24 ans et 25-29 ans viennent du tableau `FOR T1` ;
- la population 30-34 ans est estimée par un tiers de la classe 30-44 ans du
  tableau `POP T0` ;
- le taux de 35,18 % répartit uniformément la classe 25-29 ans, avec un
  cinquième à 38,7 % pour les 25 ans et quatre cinquièmes à 34,3 % pour les
  26-29 ans.

Cette méthode crée une variation départementale réelle, mais elle reste
approximative. Les populations publiques utilisées ne sont pas limitées aux
personnes de nationalité française, alors que l'étude sur la mal-inscription
porte sur ce champ.

### Ancienne méthode uniforme 52 %

L'ancienne colonne est conservée avec un intitulé explicite :

```text
18_34_ans_ancienne_methode_52_pourcent =
    mal_inscrits_estimes x 0,52
```

Elle ne crée pas d'information territoriale nouvelle et ne modifie pas le
classement, puisque tous les départements sont multipliés par la même constante.
Elle sert uniquement à comprendre et comparer l'ancienne méthode de calcul.

### Indicateur de population scolarisée

Le tableau ajoute séparément :

```text
population scolarisee 18-29 ans =
    population scolarisee 18-24 ans
    + population scolarisee 25-29 ans
```

La part correspondante est calculée sur l'ensemble des 18-29 ans du
département. Cet indicateur peut aider à identifier les territoires
universitaires, mais il ne doit pas être interprété comme un nombre d'étudiants
mal inscrits.

### Carte NUPES de style Insee

La carte rose-bordeaux répartit les départements en quartiles de la part NUPES
parmi les exprimés :

```text
moins de 21,9 %
de 21,9 % à 24,9 %
de 24,9 % à 28,7 %
plus de 28,7 %
```

Les seuils sont affichés directement dans la légende de la carte et sont
recalculés sur les 100 territoires disposant d'un pourcentage cohérent.

### Nuage de points et corrélation

Le nuage de points place chaque département selon :

```text
axe x = part du vote NUPES parmi les exprimés
axe y = part de mal-inscription
couleur = score croisé par moyenne géométrique des rangs
```

Il affiche aussi la droite de régression, les médianes et deux coefficients :

```text
Pearson  = 0,199
Spearman = 0,321
```

La relation observée est positive mais limitée. Elle est plus nette dans les
rangs que sous la forme d'une relation linéaire. Comme le reste de l'analyse,
elle est écologique : une corrélation entre départements ne décrit pas le
comportement individuel des personnes mal inscrites.

Le graphique est généré par :

```bash
python3 src/scripts/cartographie/nuage_points_mal_inscrits_nupes_2022.py
```

## Premier et second tours

Le premier tour est privilégié pour mesurer l'implantation électorale NUPES,
car la coalition est présente dans beaucoup plus de circonscriptions.

La carte du second tour est complémentaire mais ne mesure pas la même chose :
les scores dépendent des qualifications, éliminations, retraits et
configurations de duel ou de triangulaire. Un département sans candidat NUPES
au second tour peut donc apparaître à zéro sans que cela traduise une absence
d'électorat NUPES.

Deux agrégats ministère + Legis-2022 à sources identiques sont conservés comme
contrôle :

```text
T1 ministère + Legis-2022 : 5 977 283 voix NUPES, 26,28 % des exprimés
T2 ministère + Legis-2022 : 6 797 881 voix NUPES, 32,76 % des exprimés
```

Les rendus principaux utilisent désormais les totaux de coalition Wikipédia
pour les 100 départements au premier comme au second tour. Quand l'entrée NUPES
existe dans Wikipédia mais ne possède aucun total de second tour, le T2 est
codé explicitement à zéro afin de ne pas retomber sur une définition
ministère/Legis-2022 différente.

Le total de voix de coalition contrôlée peut être additionné, mais aucun taux
national n'est calculé en mélangeant les dénominateurs ministère et les
pourcentages départementaux Wikipédia.

## Reproduire les cartes

Le générateur principal est :

```text
src/scripts/cartographie/cartes_departements_mal_inscrits_nupes_2022.py
```

Il nécessite Python et `openpyxl`, ainsi que les entrées locales listées plus
haut. Une fois les fichiers placés aux chemins attendus :

```bash
python src/scripts/cartographie/cartes_departements_mal_inscrits_nupes_2022.py
```

Le script :

1. extrait la figure 4 du fichier Insee ;
2. agrège les résultats NUPES des premier et second tours ;
3. applique les valeurs de coalition contrôlées aux premier et second tours ;
4. joint les résultats au fond départemental ;
5. calcule les scores et couleurs ;
6. génère les GeoJSON et les cartes HTML interactives.

### Reproduire le tableau Top 25

Le générateur du tableau est :

```text
src/scripts/cartographie/construire_tableau_top25_mal_inscrits_nupes_2022.py
```

Pour retélécharger les données RP2022 des 25 départements et reconstruire le
CSV intermédiaire puis le Markdown :

```bash
python src/scripts/cartographie/construire_tableau_top25_mal_inscrits_nupes_2022.py \
  --refresh-insee
```

Sans `--refresh-insee`, le script réutilise le CSV local déjà versionné.

### Reproduire les overrides Wikipédia

Le fichier
`data/04_analysis/elections/2022-legislatives-nupes-wikipedia-overrides.csv`
est produit par :

```text
src/scripts/cartographie/extraire_nupes_wikipedia_2022.py
```

Commande :

```bash
python src/scripts/cartographie/extraire_nupes_wikipedia_2022.py
```

Le script :

1. part de la liste départementale Insee ;
2. retrouve les pages Wikipédia départementales ;
3. interroge l'API MediaWiki par lots ;
4. extrait l'entrée officielle NUPES de l'infobox ;
5. accepte les variantes de champ `votesN` et `vote électoralN` ;
6. extrait aussi les champs de second tour `votes2vN` et `pourcentage2vN`
   lorsqu'ils existent ;
7. exclut les entrées explicitement dissidentes lorsque l'entrée officielle
   est identifiée par son logo ou sa couleur ;
8. écrit les voix, le pourcentage, l'URL permanente, l'identifiant et
   l'horodatage de la révision ;
9. génère un CSV de contrôle pour les pages non extraites.

L'application des overrides sur les agrégats déjà produits est faite par :

```text
src/scripts/cartographie/appliquer_overrides_nupes_wikipedia_2022.py
```

## Limites et pistes de prolongement

- L'analyse est écologique : une corrélation départementale ne permet pas de
  conclure que les personnes mal inscrites votent davantage NUPES.
- La variable Insee ne correspond pas toujours juridiquement à une
  mal-inscription.
- La méthode de coalition contrôlée dépend de pages Wikipédia, dont la méthode
  de regroupement doit rester documentée et contrôlée.
- Le second tour est structurellement affecté par la sélection des candidats.
- Une analyse véritablement fine par bureau de vote nécessiterait une donnée
  Insee ou CASD permettant de rattacher résidence et inscription électorale à
  une géographie infra-départementale.

Le cheminement complet envisagé pour l'échelle départementale est conservé
dans le [plan méthodologique](plan-cartes-departements-mal-inscrits-nupes-2022.md).
