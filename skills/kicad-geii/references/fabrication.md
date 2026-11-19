# Dossier de fabrication IUT

Source : [consigne de remise du professeur](http://geii.pages.univ-lyon1.fr/cao/dossier_fabrication/) et exemple original `assets/DOSSIER DE FABRICATION.pdf`.

## Génération

Installer les dépendances si elles manquent dans le Python usuel :

```powershell
python -m pip install -r "<skill>/scripts/requirements.txt"
python "<skill>/scripts/dossier_iut.py" "<projet.kicad_pro>" --sortie "<nouveau-dossier>"
```

Le nom affiché reste fictif par défaut. `--nom` permet un cartouche local uniquement lorsque l'utilisateur l'a demandé ; ne pas publier de données personnelles par cette option.

La commande crée un dossier neuf. ERC, DRC, parité et zones sont vérifiés avant les exports. Une erreur empêche la fabrication du dossier ; avertissements et exclusions sont consignés, pas automatiquement acceptés.

Ordre du PDF : garde, sommaire, schéma, F.Fab avec contour et vue 3D, straps F.Cu avec contour, nomenclature Reference/Value. Le nombre de pages dépend du schéma et de la BOM. Pour un projet sans straps, une page l'indique.

Fichiers séparés : `schema.pdf`, `F_Fab.pdf`, `F_Cu.pdf`, `vue_3d.png`, `bom.csv`, `DOSSIER DE FABRICATION.pdf`, rapports JSON. Les Gerbers comprennent B.Cu, Edge.Cuts et F.Cu si la carte en utilise, ainsi que les perçages Excellon. Le ZIP n'inclut pas les annotations `Cmts.User`.

Ce profil cible une fabrication pédagogique sans vernis, sérigraphie ni métallisation. Pour un fabricant industriel, choisir ses couches et exigences : ne pas réutiliser ce ZIP en supposant les masques présents. Une carte double face sans trous métallisés exige aussi une revue de montage ; le script ne valide pas sa soudabilité.

## Contrôle des exports

```powershell
python "<skill>/scripts/gerber_vue.py" "<Gerber>" "<controle.png>"
```

Gerbonara interprète les unités, formats, arcs, macros et polarités ; resvg-py produit le PNG. L'aperçu est vu par transparence depuis le dessus, sans miroir horizontal supplémentaire. Il montre le cuivre bas en bleu, le haut en rouge, les trous blancs et le contour sombre. Le SVG et les statistiques JSON restent disponibles.

Comparer ce rendu au PCB : nombres de flashes et de trous, découpes, gouttes, orientation, repères et absence des annotations. Un flash n'est pas toujours une pastille : ne pas supposer l'égalité sans regarder le contenu. Les chiffres ne prouvent pas la topologie électrique ; regarder aussi les espaces et les liaisons.

Ouvrir les Gerbers dans GerbView si accessible. Sinon annoncer précisément le lecteur utilisé, sans prétendre avoir ouvert l'application.

Rendre le PDF en images puis inspecter toutes les pages : titres, taille de la carte, bornes, BOM sans texte coupé, schéma lisible. Ne pas imprimer le PDF assemblé comme typon : la mise en page redimensionne les vues. Un typon nécessite un export séparé à l'échelle 1:1, avec orientation vérifiée sur une empreinte connue et contrôle d'une dimension imprimée.
