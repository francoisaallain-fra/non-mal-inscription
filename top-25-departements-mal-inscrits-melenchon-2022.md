# Top 25 des départements mal-inscription x vote Mélenchon en 2022

Classement selon la moyenne géométrique des rangs percentiles de mal-inscription et de vote Mélenchon au premier tour de la présidentielle :

`score_croise = sqrt(score_mal_inscription * score_melenchon)`

La nouvelle estimation territorialisée des 18-34 ans applique les taux nationaux de mal-inscription par âge de la figure 3 de l'Insee aux populations d'âge départementales RP2022. L'ancienne méthode uniforme est conservée dans une colonne explicitement marquée « 52 % ».

| Rang | Département | Mal-inscrits estimés | 18-34 ans estimés, méthode territorialisée | 18-34 ans estimés, ancienne méthode uniforme 52 % | Population scolarisée 18-29 ans | Part scolarisée des 18-29 ans | Mal-inscrits | Vote Mélenchon | Score croisé |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Guyane | 27 293 | 24 186 | 14 192 | 11 125 | 22,9 % | 26,5 % | 50,59 % | 0,991 |
| 2 | Guadeloupe | 74 581 | 22 979 | 38 782 | 13 838 | 30,8 % | 23,6 % | 56,16 % | 0,990 |
| 3 | Martinique | 66 401 | 20 864 | 34 529 | 11 953 | 29,4 % | 21,8 % | 53,10 % | 0,970 |
| 4 | Paris | 322 854 | 215 027 | 167 884 | 206 948 | 45,6 % | 23,6 % | 30,08 % | 0,947 |
| 5 | Haute-Garonne | 194 437 | 128 044 | 101 107 | 114 108 | 43,7 % | 20,9 % | 25,84 % | 0,903 |
| 6 | Rhône | 249 239 | 165 869 | 129 604 | 145 380 | 42,8 % | 21,1 % | 25,20 % | 0,898 |
| 7 | Seine-Saint-Denis | 142 907 | 141 273 | 74 312 | 101 122 | 36,6 % | 18,0 % | 49,09 % | 0,897 |
| 8 | Ariège | 21 903 | 8 463 | 11 390 | 3 116 | 19,9 % | 18,4 % | 26,07 % | 0,877 |
| 9 | Hérault | 163 541 | 91 754 | 85 042 | 79 875 | 43,2 % | 19,3 % | 24,24 % | 0,874 |
| 10 | Bouches-du-Rhône | 283 648 | 148 979 | 147 497 | 110 103 | 37,7 % | 20,1 % | 23,59 % | 0,869 |
| 11 | Val-d'Oise | 127 634 | 98 758 | 66 370 | 70 595 | 36,8 % | 17,4 % | 33,17 % | 0,857 |
| 12 | Val-de-Marne | 137 723 | 119 019 | 71 616 | 98 568 | 41,6 % | 17,3 % | 32,67 % | 0,841 |
| 13 | Seine-et-Marne | 155 579 | 108 219 | 80 901 | 68 046 | 32,6 % | 17,3 % | 25,87 % | 0,814 |
| 14 | Gironde | 221 283 | 128 861 | 115 067 | 100 899 | 39,7 % | 19,1 % | 21,84 % | 0,804 |
| 15 | Essonne | 135 116 | 102 305 | 70 260 | 74 326 | 36,9 % | 16,9 % | 28,12 % | 0,794 |
| 16 | Hauts-de-Seine | 167 608 | 136 036 | 87 156 | 109 770 | 41,4 % | 16,8 % | 25,77 % | 0,761 |
| 17 | Puy-de-Dôme | 91 748 | 48 125 | 47 709 | 39 536 | 41,2 % | 19,6 % | 20,84 % | 0,758 |
| 18 | Isère | 152 296 | 93 174 | 79 194 | 67 045 | 36,7 % | 17,2 % | 22,83 % | 0,755 |
| 19 | Meurthe-et-Moselle | 93 491 | 57 854 | 48 615 | 49 800 | 42,5 % | 19,0 % | 20,89 % | 0,751 |
| 20 | Loire-Atlantique | 177 524 | 109 474 | 92 313 | 76 964 | 36,1 % | 16,8 % | 23,43 % | 0,730 |
| 21 | Ille-et-Vilaine | 130 406 | 87 484 | 67 811 | 71 924 | 40,9 % | 16,9 % | 22,20 % | 0,715 |
| 22 | Lot | 22 424 | 8 294 | 11 660 | 3 217 | 21,4 % | 16,1 % | 23,71 % | 0,709 |
| 23 | Vienne | 52 328 | 32 338 | 27 210 | 27 972 | 42,4 % | 17,1 % | 21,22 % | 0,698 |
| 24 | Indre-et-Loire | 76 647 | 44 225 | 39 857 | 35 302 | 39,9 % | 17,4 % | 20,77 % | 0,691 |
| 25 | Nord | 292 039 | 207 114 | 151 860 | 157 605 | 37,8 % | 16,1 % | 21,95 % | 0,678 |
| **Total top 25** | **25 départements** | **3 580 652** | **2 348 719** | **1 861 939** | **1 849 137** | **39,5 %** | **18,7 %** | **n.d.** | **-** |

## Méthodes et limites

### Mal-inscrits estimés

`part départementale Insee × inscrits électoraux à la présidentielle 2022`.

### 18-34 ans, méthode territorialisée

```text
population 18-24 ans × 38,7 %
+ population 25-29 ans × 35,18 %
+ (population 30-44 ans / 3) × 30,9 %
```

Cette méthode territorialise les volumes, mais les données publiques utilisées portent sur toute la population résidente et non uniquement sur les personnes de nationalité française. Elle reste donc une approximation exploratoire.

Sources : Insee Première n°1986, figures 3 et 4 ; Insee RP2022, dossiers complets départementaux, tableaux POP T0 et FOR T1 ; ministère de l'Intérieur via Hexagonal, présidentielle 2022 T1.
