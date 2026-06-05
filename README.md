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
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson) | Jointure finale de la méthode « coalition contrôlée » du premier tour |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t1-ministere-legis2022.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t1-ministere-legis2022.geojson) | Premier tour calculé uniquement avec les mêmes sources que le second tour |
| [`data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson`](data/04_analysis/cartographie/2022-departements-mal-inscription-nupes-t2.geojson) | Jointure du second tour |
| [`data/04_analysis/elections/`](data/04_analysis/elections/) | Agrégats électoraux et table des valeurs Wikipédia |
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

### Méthode « coalition contrôlée »

La méthode utilise ensemble le nombre de voix et le pourcentage de coalition
affichés sur la page Wikipédia départementale lorsqu'ils ont pu être extraits.
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
- [croisement au premier tour, sources comparables au second tour](maps/2022-croisement-mal-inscrits-nupes-departements-t1-ministere-legis2022.html) ;
- [croisement au second tour](maps/2022-croisement-mal-inscrits-nupes-departements-t2.html).

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
3. applique les valeurs de coalition contrôlées au premier tour ;
4. joint les résultats au fond départemental ;
5. calcule les scores et couleurs ;
6. génère les GeoJSON et les cartes HTML interactives.

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
