# Plan de production des cartes mal-inscription / vote NUPES 2022

Objectif : produire trois cartes au niveau du bureau de vote pour les élections législatives 2022 :

1. une carte de la part de mal-inscrits en 2022 ;
2. une carte de la part du vote NUPES en 2022 ;
3. une carte croisée mal-inscription x vote NUPES, avec un gradient allant du rouge au vert.

## Point d'attention méthodologique

Les résultats électoraux 2022 sont disponibles par bureau de vote dans Hexagonal. En revanche, les données publiques INSEE sur la mal-inscription ne sont pas directement publiées au niveau du bureau de vote.

Deux chemins sont donc possibles :

- **Chemin public reproductible** : produire une mesure communale, départementale ou par carreau/zone disponible, puis l'affecter aux bureaux de vote correspondants. C'est exploitable cartographiquement, mais ce n'est pas une vraie mesure observée au bureau.
- **Chemin robuste au bureau de vote** : obtenir les données individuelles ou agrégées fines via l'INSEE/CASD, puis construire un indicateur à partir de l'appariement entre résidence principale et commune d'inscription électorale. C'est le chemin à privilégier pour une analyse scientifique.

Le plan ci-dessous distingue ces deux niveaux.

## Données nécessaires

### 1. Mal-inscription 2022

Source publique INSEE de référence :

- `Insee Première n°1986`, mars 2024 : "Élection présidentielle 2022 : 16,5 % des électeurs inscrits l'étaient dans une autre commune que celle de leur résidence principale".
- Fichier associé : `donnees_insee_premiere_n1986.xlsx`.

Indicateur INSEE utile :

- inscrit dans une commune différente de la commune de résidence principale ;
- non-inscrit parmi les Français majeurs résidant en France hors Mayotte.

Limite :

- le fichier public est surtout exploitable pour des tableaux nationaux, départementaux et sociodémographiques ;
- il ne donne pas directement un taux par bureau de vote.

Chemin robuste recommandé :

- demander l'accès au CASD ou à une extraction INSEE agréée combinant :
  - enquête annuelle de recensement 2022 ;
  - Répertoire électoral unique 2022 ;
  - commune de résidence principale ;
  - commune d'inscription électorale ;
  - si possible, localisation infra-communale ou rattachement au bureau de vote.

Variable cible :

```text
part_mal_inscrits = nb_inscrits_residant_dans_la_zone_et_inscrits_autre_commune
                    / nb_inscrits_residant_dans_la_zone
```

À défaut d'accès fin :

```text
part_mal_inscrits_bureau = part_mal_inscrits_commune
```

Chaque bureau d'une même commune reçoit alors la même valeur.

### 2. Votes NUPES 2022

Sources Hexagonal déjà ciblées :

- `data/01_raw/ministere_interieur/2022-legislatives-1-bureau_de_vote.csv`
- `data/01_raw/ministere_interieur/2022-legislatives-2-bureau_de_vote.csv`
- extraction produite :
  - `data/04_analysis/elections/2022-legislatives-nupes-bureau_de_vote.csv`

Indicateurs par bureau :

```text
part_nupes_exprimes = voix_nupes / exprimes
part_nupes_inscrits = voix_nupes / inscrits
```

Choix recommandé :

- utiliser `part_nupes_exprimes` pour mesurer la préférence électorale exprimée ;
- garder `part_nupes_inscrits` en variable secondaire, car elle intègre aussi l'abstention.

Tour recommandé :

- carte principale : premier tour, car NUPES est présente dans quasiment toutes les circonscriptions ;
- carte complémentaire : second tour, utile mais structurellement biaisée par les qualifications et désistements.

## Géographie des bureaux de vote

Besoin minimal :

```text
code_commune
bureau_de_vote
geometry
```

Trois options :

1. **Points de bureaux** : géocoder les adresses des bureaux de vote si une source d'adresses est disponible.
2. **Polygones réels de bureaux** : récupérer les découpages quand les communes les publient, puis harmoniser. C'est très variable selon les territoires.
3. **Approximation par commune** : rattacher les résultats des bureaux au centroïde de la commune ou répartir les bureaux dans la commune. C'est moins précis mais rapidement cartographiable.

Pour une carte nationale, commencer par l'option 1 ou 3. Pour une étude locale, privilégier l'option 2.

## Pipeline proposé

### Étape A - Préparer le vote NUPES par bureau

Entrée :

```text
data/04_analysis/elections/2022-legislatives-nupes-bureau_de_vote.csv
```

Traitement :

1. filtrer `tour == 1` ;
2. agréger par `code_commune`, `bureau_de_vote`, `circonscription` ;
3. calculer :
   - `voix_nupes`;
   - `exprimes`;
   - `inscrits`;
   - `part_nupes_exprimes`;
   - `part_nupes_inscrits`.

Sortie :

```text
data/04_analysis/elections/2022-legislatives-nupes-bureau_de_vote-t1.csv
```

### Étape B - Préparer la mal-inscription

Chemin public :

1. télécharger `donnees_insee_premiere_n1986.xlsx` ;
2. extraire le tableau territorial le plus fin disponible ;
3. normaliser les codes géographiques ;
4. produire une table :

```text
code_commune ou code_departement
part_mal_inscrits
part_non_inscrits
source_niveau_geo
```

Sortie :

```text
data/04_analysis/insee/2022-mal-inscription.csv
```

Chemin robuste :

1. obtenir l'extraction INSEE/CASD ;
2. calculer la commune de résidence principale ;
3. comparer avec la commune d'inscription électorale ;
4. agréger au bureau de vote si le rattachement est disponible, sinon à la commune ;
5. documenter précisément le niveau de géographie.

### Étape C - Créer le fond de carte des bureaux

Sortie attendue :

```text
data/04_analysis/geodata/2022-bureaux_vote.geojson
```

Colonnes minimales :

```text
code_commune
bureau_de_vote
geometry
```

Contrôles :

- chaque couple `code_commune + bureau_de_vote` doit être unique ;
- les codes communes doivent être au format INSEE sur 5 caractères ;
- les bureaux doivent garder les zéros initiaux, par exemple `0001`.

### Étape D - Joindre les trois dimensions

Jointures :

```text
bureaux_geo
  left join vote_nupes
    on code_commune, bureau_de_vote

  left join mal_inscription
    on code_commune
```

Si la mal-inscription n'est disponible qu'au département :

```text
left join mal_inscription
  on code_departement
```

Sortie :

```text
data/04_analysis/cartographie/2022-bureaux-mal-inscription-nupes.geojson
```

## Cartes à produire

### Carte 1 - Mal-inscrits 2022

Variable :

```text
part_mal_inscrits
```

Palette :

- clair : faible part de mal-inscrits ;
- foncé : forte part de mal-inscrits.

Mention obligatoire :

- préciser le niveau réel de la donnée : bureau, commune ou département.

### Carte 2 - Vote NUPES 2022

Variable principale :

```text
part_nupes_exprimes
```

Palette :

- clair : faible vote NUPES ;
- foncé : fort vote NUPES.

Variante :

```text
part_nupes_inscrits
```

utile si l'on veut intégrer l'abstention dans l'intensité électorale.

### Carte 3 - Croisement mal-inscription x vote NUPES

Variables :

```text
x = part_mal_inscrits
y = part_nupes_exprimes
```

Créer deux scores normalisés :

```text
score_mal_inscription = rang_percentile(part_mal_inscrits)
score_nupes = rang_percentile(part_nupes_exprimes)
score_croise = (score_mal_inscription + score_nupes) / 2
```

Palette demandée :

- rouge : peu de mal-inscrits et peu de vote NUPES ;
- vert : part significative de mal-inscrits et vote NUPES élevé.

Définition opérationnelle :

```text
rouge intense : score_mal_inscription < 0.33 et score_nupes < 0.33
vert intense  : score_mal_inscription > 0.66 et score_nupes > 0.66
intermédiaire : gradient continu selon score_croise
gris/neutre   : cas discordants, par exemple mal-inscription forte mais vote NUPES faible
```

Recommandation importante :

- ne pas forcer tous les cas discordants dans un simple gradient rouge-vert ;
- utiliser une couleur neutre ou désaturée pour les bureaux où une seule des deux variables est élevée.

Une classification plus lisible :

```text
faible mal-inscription + faible NUPES      -> rouge
forte mal-inscription + fort NUPES         -> vert
forte mal-inscription + faible NUPES       -> bleu/gris
faible mal-inscription + fort NUPES        -> jaune/gris
valeurs intermédiaires                     -> gradient désaturé
```

## Contrôles qualité

Avant publication :

1. vérifier les totaux de voix NUPES contre les résultats nationaux du ministère ;
2. vérifier que les bureaux sans candidat NUPES au premier tour sont explicitement codés à `0` et non manquants ;
3. vérifier la couverture géographique des bureaux ;
4. documenter le niveau réel de la variable mal-inscription ;
5. produire une table des bureaux non appariés après jointure.

Fichiers de contrôle :

```text
data/04_analysis/qa/2022-bureaux-non-apparies.csv
data/04_analysis/qa/2022-controles-totaux-nupes.csv
data/04_analysis/qa/2022-couverture-mal-inscription.csv
```

## Livrables

```text
data/04_analysis/elections/2022-legislatives-nupes-bureau_de_vote-t1.csv
data/04_analysis/insee/2022-mal-inscription.csv
data/04_analysis/geodata/2022-bureaux_vote.geojson
data/04_analysis/cartographie/2022-bureaux-mal-inscription-nupes.geojson
maps/2022-mal-inscrits-bureaux.html
maps/2022-vote-nupes-bureaux.html
maps/2022-croisement-mal-inscrits-nupes-bureaux.html
```

## Décision à prendre

La décision structurante est le niveau de précision attendu pour la mal-inscription :

- si l'objectif est exploratoire, utiliser le chemin public avec approximation communale ou départementale ;
- si l'objectif est analytique ou publiable, chercher un accès INSEE/CASD et ne pas présenter la carte comme une mesure au bureau tant que la donnée n'est pas réellement disponible à ce niveau.
