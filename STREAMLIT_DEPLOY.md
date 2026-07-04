# Déploiement Streamlit

Cette app publie les rendus publics suivants :

- nuage NUPES 2022 sans outliers, avec bulles de mal-inscrits estimés ;
- nuage Mélenchon/LFI 2022 sans outliers, avec bulles de mal-inscrits estimés ;
- carte territorialisée NUPES 2022 ;
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

## Déployer depuis ton GitHub

1. Créer un repo GitHub sous ton compte personnel, par exemple :

```text
francoisaallain-fra/non-mal-inscription-streamlit
```

2. Pousser ce dossier dans ce repo personnel, pas dans `lfi-pee/non-mal-inscription`.

3. Aller sur Streamlit Community Cloud :

```text
https://share.streamlit.io/
```

4. Créer une nouvelle app avec :

```text
Repository: francoisaallain-fra/non-mal-inscription-streamlit
Branch: main
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
maps/2022-croisement-mal-inscrits-nupes-departements-coalition-web.html
maps/2022-croisement-mal-inscrits-melenchon-presidentielle-departements-web.html
top-25-departements-mal-inscrits-nupes-2022.md
top-25-departements-mal-inscrits-melenchon-2022.md
```
