# Déploiement Streamlit

Cette app publie les rendus publics suivants :

- nuage NUPES 2022 T2 sans outliers, avec bulles de mal-inscrits estimés ;
- nuage Mélenchon/LFI 2022 sans outliers, avec bulles de mal-inscrits estimés ;
- carte territorialisée NUPES 2022 T2 ;
- carte territorialisée Mélenchon/LFI 2022 ;
- tableaux top 25 des départements.

## Fichier d'entrée Streamlit

```text
streamlit_app.py
```

## Dépendances

```text
requirements.txt
```

Le fichier contient déjà `streamlit>=1.41,<2`.

## Déployer depuis GitHub

1. Utiliser le dépôt GitHub :

```text
lfi-pee/non-mal-inscription
```

2. Vérifier que la branche `master` contient bien l'app Streamlit et les rendus HTML.

3. Aller sur Streamlit Community Cloud :

```text
https://share.streamlit.io/
```

4. Créer une nouvelle app avec :

```text
Repository: lfi-pee/non-mal-inscription
Branch: master
Main file path: streamlit_app.py
```

5. L'URL publique Streamlit obtenue pourra être partagée directement.

## Fichiers nécessaires

Les fichiers suivants doivent être présents dans le repo déployé :

```text
streamlit_app.py
requirements.txt
.streamlit/config.toml
maps/2022-nuage-points-mal-inscrits-nupes-departements-bulles-sans-outliers.html
maps/2022-nuage-points-mal-inscrits-melenchon-departements-bulles-sans-outliers.html
maps/2022-croisement-mal-inscrits-nupes-departements-t2.html
maps/2022-croisement-mal-inscrits-melenchon-presidentielle-departements-web.html
top-25-departements-mal-inscrits-nupes-t2-2022.md
top-25-departements-mal-inscrits-melenchon-2022.md
```
