# Plan de production des cartes départementales mal-inscription / vote NUPES 2022

Objectif : produire trois cartes par département pour 2022 :

1. une carte de la part de mal-inscrits ;
2. une carte de la part du vote NUPES aux législatives ;
3. une carte croisée mal-inscription x vote NUPES, avec un gradient allant du rouge au vert.

À cette échelle, le plan est plus robuste que la version par bureau de vote : l'étude INSEE publie les données de mal-inscription au département, et les résultats NUPES peuvent être agrégés au département depuis les données Hexagonal.

## Données sources

### 1. Mal-inscription 2022

Source :

```text
INSEE Première n°1986, mars 2024
Élection présidentielle 2022 : 16,5 % des électeurs inscrits l'étaient dans une autre commune que celle de leur résidence principale
```

Fichier :

```text
donnees_insee_premiere_n1986.xlsx
```

Niveau géographique public le plus fin :

```text
département
```

Tableau cible :

```text
Figure 4 - Part des personnes non inscrites sur les listes électorales de leur commune de résidence principale par département en 2022
```

Variable cible :

```text
part_mal_inscrits
```

Définition :

```text
part des électeurs inscrits dans une autre commune que leur commune de résidence principale
```

Point de vigilance :

- l'INSEE indique que cette situation ne correspond pas toujours juridiquement à une "mal-inscription" ;
- dans le projet, documenter la variable comme `inscription_hors_commune_residence` ou `part_inscrits_autre_commune`, puis réserver le libellé "mal-inscrits" à la visualisation grand public.

Sortie attendue :

```text
data/04_analysis/insee/2022-mal-inscription-departements.csv
```

Colonnes minimales :

```text
code_departement
libelle_departement
part_mal_inscrits
source
```

### 2. Vote NUPES 2022

Sources Hexagonal :

```text
data/01_raw/ministere_interieur/2022-legislatives-1-bureau_de_vote.csv
data/01_raw/ministere_interieur/2022-legislatives-2-bureau_de_vote.csv
data/04_analysis/elections/2022-legislatives-nupes-bureau_de_vote.csv
```

Source de travail déjà produite :

```text
data/04_analysis/elections/2022-legislatives-nupes-bureau_de_vote.csv
```

Tour recommandé :

```text
tour 1
```

Raison :

- le premier tour mesure mieux la présence électorale NUPES sur l'ensemble du territoire ;
- le second tour dépend des qualifications, triangulaires, duels et désistements.

Indicateurs à agréger par département :

```text
voix_nupes = somme(voix)
exprimes = somme(exprimes)
inscrits = somme(inscrits)
part_nupes_exprimes = voix_nupes / exprimes
part_nupes_inscrits = voix_nupes / inscrits
```

Choix recommandé pour la carte :

```text
part_nupes_exprimes
```

Sortie attendue :

```text
data/04_analysis/elections/2022-legislatives-nupes-departements-t1.csv
```

Colonnes minimales :

```text
code_departement
voix_nupes
exprimes
inscrits
part_nupes_exprimes
part_nupes_inscrits
```

## Fond de carte

Source possible dans Hexagonal :

```text
data/03_main/geodata/departements.geojson
```

Si absent, utiliser une source publique stable :

```text
Admin Express IGN
contours départements data.gouv.fr
Natural Earth uniquement pour une vue très simplifiée
```

Sortie attendue :

```text
data/04_analysis/geodata/departements-2022.geojson
```

Colonnes minimales :

```text
code_departement
libelle_departement
geometry
```

Contrôles :

- conserver les codes `2A` et `2B` pour la Corse ;
- harmoniser les départements d'outre-mer avec les codes INSEE `971`, `972`, `973`, `974`, `976` ;
- décider explicitement du traitement de Mayotte, car l'étude INSEE 2022 exclut parfois Mayotte selon le champ.

## Pipeline proposé

### Étape A - Extraire la mal-inscription INSEE

1. télécharger le fichier XLSX INSEE ;
2. identifier l'onglet ou la plage correspondant à la figure départementale ;
3. extraire les colonnes département et part de mal-inscrits ;
4. normaliser les codes départements ;
5. exporter en CSV.

Sortie :

```text
data/04_analysis/insee/2022-mal-inscription-departements.csv
```

Contrôle :

```text
France entière autour de 16,5 %
```

### Étape B - Agréger le vote NUPES par département

1. lire `2022-legislatives-nupes-bureau_de_vote.csv` ;
2. filtrer `tour == 1` ;
3. grouper par `code_departement` ;
4. sommer `voix`, `exprimes`, `inscrits` ;
5. calculer les parts.

Sortie :

```text
data/04_analysis/elections/2022-legislatives-nupes-departements-t1.csv
```

Contrôle :

```text
somme nationale des voix NUPES au premier tour = total attendu dans les résultats officiels
```

### Étape C - Joindre les données

Jointure :

```text
departements_geo
  left join mal_inscription
    on code_departement

  left join vote_nupes
    on code_departement
```

Sortie :

```text
data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson
```

Colonnes finales :

```text
code_departement
libelle_departement
part_mal_inscrits
voix_nupes
exprimes
inscrits
part_nupes_exprimes
part_nupes_inscrits
geometry
```

## Cartes à produire

### Carte 1 - Mal-inscrits 2022 par département

Variable :

```text
part_mal_inscrits
```

Palette :

```text
faible part -> couleur claire
forte part  -> couleur foncée
```

Titre recommandé :

```text
Part des inscrits votant hors de leur commune de résidence principale en 2022
```

Sous-titre recommandé :

```text
Données INSEE, agrégation départementale
```

### Carte 2 - Vote NUPES 2022 par département

Variable principale :

```text
part_nupes_exprimes
```

Palette :

```text
faible vote NUPES -> couleur claire
fort vote NUPES   -> couleur foncée
```

Titre recommandé :

```text
Part des voix NUPES au premier tour des législatives 2022
```

Variante :

```text
part_nupes_inscrits
```

Cette variante est utile si l'on veut représenter le poids électoral NUPES rapporté à l'ensemble des inscrits, abstention comprise.

### Carte 3 - Croisement mal-inscription x vote NUPES par département

Variables :

```text
x = part_mal_inscrits
y = part_nupes_exprimes
```

Normalisation :

```text
score_mal_inscription = rang_percentile(part_mal_inscrits)
score_nupes = rang_percentile(part_nupes_exprimes)
score_croise = sqrt(score_mal_inscription * score_nupes)
```

Gradient demandé :

```text
rouge -> peu de mal-inscrits et peu de vote NUPES
vert  -> forte mal-inscription et fort vote NUPES
```

Définition opérationnelle :

```text
rouge intense : score_mal_inscription < 0.33 et score_nupes < 0.33
vert intense  : score_mal_inscription > 0.66 et score_nupes > 0.66
intermédiaire : gradient rouge-jaune-vert selon score_croise
```

La moyenne géométrique est retenue pour privilégier les départements élevés
simultanément sur les deux variables et éviter qu'un score très fort compense
entièrement un score très faible.

Point important :

```text
Le gradient rouge-vert fonctionne bien pour les départements où les deux variables vont dans le même sens.
Il est moins lisible pour les cas discordants :
- forte mal-inscription mais faible vote NUPES ;
- faible mal-inscription mais fort vote NUPES.
```

Option recommandée :

Ajouter une variable de catégorie bivariée :

```text
faible mal-inscription + faible NUPES      -> rouge
forte mal-inscription + fort NUPES         -> vert
forte mal-inscription + faible NUPES       -> bleu-gris
faible mal-inscription + fort NUPES        -> jaune-gris
valeurs moyennes ou mixtes                 -> gris clair / couleur intermédiaire
```

Puis produire deux rendus :

1. une carte simple en gradient rouge-jaune-vert ;
2. une carte bivariée plus rigoureuse distinguant les cas discordants.

## Contrôles qualité

Contrôles INSEE :

```text
nombre de départements couverts
valeur France entière
codes départements harmonisés
présence ou absence de Mayotte documentée
```

Contrôles électoraux :

```text
total voix NUPES national
total exprimés national
absence de doublons départementaux
cohérence des codes Corse et outre-mer
```

Contrôles cartographiques :

```text
tous les départements du fond de carte ont une valeur NUPES
tous les départements du fond de carte ont une valeur mal-inscription ou une raison documentée d'absence
aucune géométrie vide
```

Sorties de contrôle :

```text
data/04_analysis/qa/2022-departements-non-apparies.csv
data/04_analysis/qa/2022-controles-totaux-nupes-departements.csv
data/04_analysis/qa/2022-controles-mal-inscription-departements.csv
```

## Livrables

Données :

```text
data/04_analysis/insee/2022-mal-inscription-departements.csv
data/04_analysis/elections/2022-legislatives-nupes-departements-t1.csv
data/04_analysis/cartographie/2022-departements-mal-inscription-nupes.geojson
```

Cartes :

```text
maps/2022-mal-inscrits-departements.html
maps/2022-vote-nupes-departements.html
maps/2022-croisement-mal-inscrits-nupes-departements-coalition.html
```

Documentation :

```text
docs/methodologie-cartes-departements-mal-inscrits-nupes-2022.md
```

## Décisions à prendre

1. Utiliser `part_nupes_exprimes` ou `part_nupes_inscrits` pour la carte NUPES principale.
2. Inclure ou exclure Mayotte selon la couverture INSEE.
3. Produire uniquement le gradient rouge-vert demandé, ou ajouter aussi une carte bivariée pour les cas discordants.
4. Employer le libellé court "mal-inscrits" dans les titres publics, tout en documentant la définition INSEE exacte dans la méthode.
