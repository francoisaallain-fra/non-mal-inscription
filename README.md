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
| Résultats du ministère de l'Intérieur, distribués dans Hexagonal | Résultats des législatives 2022 par bureau de vote, premier et second tours | [github.com/lafranceinsoumise/hexagonal](https://github.com/lafranceinsoumise/hexagonal) |
| Table de codage Legis-2022 distribuée dans Hexagonal | Identification complémentaire des candidats rattachés à la NUPES | [github.com/lafranceinsoumise/hexagonal](https://github.com/lafranceinsoumise/hexagonal) |
| Pages Wikipédia départementales des législatives de 2022 | Totaux de coalition NUPES au premier tour, utilisés pour corriger les sous-comptes | [Résultats par département](https://fr.wikipedia.org/wiki/R%C3%A9sultats_par_d%C3%A9partement_des_%C3%A9lections_l%C3%A9gislatives_fran%C3%A7aises_de_2022) |

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
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson) | Jointure finale utilisée pour la V6 du premier tour |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t1-ministere-legis2022.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t1-ministere-legis2022.geojson) | Premier tour calculé uniquement avec les mêmes sources que le second tour |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson) | Jointure du second tour |

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

Cette méthode est conservée pour produire une comparaison T1/T2 à sources
constantes :

- premier tour : ministère de l'Intérieur + Legis-2022 ;
- second tour : ministère de l'Intérieur + Legis-2022.

### Limite découverte

Cette méthode était cohérente techniquement mais imparfaite politiquement. La
nuance administrative `NUP` ne recouvrait pas partout l'ensemble des candidats
présentés ou soutenus comme appartenant à la coalition NUPES.

Les premières cartes faisaient donc apparaître des valeurs manifestement
incomplètes, surtout dans les outre-mer, en Corse et dans quelques départements
métropolitains.

### Méthode V6

La V6 conserve les dénominateurs départementaux issus des résultats du
ministère, mais remplace le nombre de voix NUPES par le total de coalition
affiché sur la page Wikipédia départementale lorsqu'il a pu être extrait.

La méthode devient :

```text
si total de coalition Wikipédia disponible :
    voix_nupes = total de coalition Wikipédia
sinon :
    voix_nupes = calcul ministère + Legis-2022
                 ou correction territoriale déjà identifiée
```

Au terme du contrôle, 100 départements ou territoires utilisent un total de
coalition extrait de Wikipédia. Sept territoires conservent un repli sur les
totaux territoriaux déjà identifiés.

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

Ces résultats sont désormais repris dans la V6 depuis les pages Wikipédia
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

## Évolution des cartes

| Version | Évolution principale |
|---|---|
| V1 | Agrégation initiale des résultats ministériels par département |
| V2 | Meilleure représentation de l'outre-mer |
| V3 | Correction des totaux ultramarins de coalition |
| V4 | Intégration complémentaire de la Corse via Legis-2022 |
| V5 | Correction explicite des totaux de Corse |
| V6 | Contrôle département par département avec les totaux de coalition Wikipédia |

Les principales cartes sont :

- [mal-inscription par département](maps/2022-mal-inscrits-departements.html) ;
- [vote NUPES V6 par département](maps/2022-vote-nupes-departements.html) ;
- [vote NUPES V6, palette inspirée de l'Insee](maps/2022-vote-nupes-departements-v6-style-insee.html) ;
- [croisement mal-inscription x NUPES V6](maps/2022-croisement-mal-inscrits-nupes-departements-v6.html) ;
- [croisement au premier tour, sources comparables au second tour](maps/2022-croisement-mal-inscrits-nupes-departements-t1-ministere-legis2022.html) ;
- [croisement au second tour](maps/2022-croisement-mal-inscrits-nupes-departements-t2.html).

## Méthode cartographique

### Carte croisée

Chaque variable est transformée en rang percentile parmi les départements :

```text
score_mal_inscription = rang percentile de part_mal_inscrits
score_nupes = rang percentile de part_nupes_exprimes
score_croise = (score_mal_inscription + score_nupes) / 2
```

Le gradient demandé est ensuite appliqué :

```text
rouge : faibles niveaux de mal-inscription et de vote NUPES
vert  : niveaux élevés de mal-inscription et de vote NUPES
```

Ce score est exploratoire. Il résume bien les territoires où les deux variables
évoluent dans le même sens, mais distingue moins clairement les situations
discordantes, par exemple forte mal-inscription et faible vote NUPES.

### Carte NUPES de style Insee

La carte rose-bordeaux répartit les départements en quartiles de la part NUPES
parmi les exprimés :

```text
moins de 21,5 %
de 21,5 % à 24,8 %
de 24,8 % à 28,6 %
plus de 28,6 %
```

Les seuils sont affichés directement dans la légende de la carte.

## Premier et second tours

Le premier tour est privilégié pour mesurer l'implantation électorale NUPES,
car la coalition est présente dans beaucoup plus de circonscriptions.

La carte du second tour est complémentaire mais ne mesure pas la même chose :
les scores dépendent des qualifications, éliminations, retraits et
configurations de duel ou de triangulaire. Un département sans candidat NUPES
au second tour peut donc apparaître à zéro sans que cela traduise une absence
d'électorat NUPES.

Deux cartes à sources identiques ont été produites pour permettre une
comparaison prudente :

```text
T1 ministère + Legis-2022 : 5 977 283 voix NUPES, 26,28 % des exprimés
T2 ministère + Legis-2022 : 6 797 881 voix NUPES, 32,76 % des exprimés
```

La V6 du premier tour, enrichie par les totaux de coalition Wikipédia, atteint
`6 028 524` voix et `26,51 %` des exprimés dans le périmètre calculé.

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
3. applique les corrections V6 au premier tour ;
4. joint les résultats au fond départemental ;
5. calcule les scores et couleurs ;
6. génère les GeoJSON et les cartes HTML interactives.

## Limites et pistes de prolongement

- L'analyse est écologique : une corrélation départementale ne permet pas de
  conclure que les personnes mal inscrites votent davantage NUPES.
- La variable Insee ne correspond pas toujours juridiquement à une
  mal-inscription.
- La V6 dépend de totaux de coalition issus de pages Wikipédia, dont la méthode
  de regroupement doit rester documentée et contrôlée.
- Le second tour est structurellement affecté par la sélection des candidats.
- Une analyse véritablement fine par bureau de vote nécessiterait une donnée
  Insee ou CASD permettant de rattacher résidence et inscription électorale à
  une géographie infra-départementale.

Le cheminement complet envisagé pour l'échelle départementale est conservé
dans le [plan méthodologique](plan-cartes-departements-mal-inscrits-nupes-2022.md).
