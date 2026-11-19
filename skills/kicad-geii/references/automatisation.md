# Automatisation KiCad

## Deux Python différents

- Python livré avec KiCad : `pcbnew` disponible ; utiliser pour géométrie et édition du PCB.
- Python usuel : PyMuPDF, Gerbonara et resvg-py ; utiliser pour le dossier et les aperçus. Ne pas supposer que les dépendances installées dans l'un existent dans l'autre.
- Détection CLI : PATH ou installations locales KiCad 10 puis 9 ; surcharge par `KICAD_CLI`. Vérifier `kicad-cli version` et `--help` pour l'installation réelle. Les fonctions du dossier ciblent KiCad 10.

## Modifier sans corrompre

Charger une copie et collecter les objets à modifier dans une liste Python avant tout ajout ou suppression. Ne pas muter les collections SWIG pendant leur parcours : des plantages ont été observés.

Garder références aux empreintes et à la carte pendant l'accès aux pastilles. Respecter les unités internes et utiliser `pcbnew.FromMM` / `ToMM` ; les angles et rotations ont leurs types dédiés suivant la version.

Le parseur S-expression de `kicad_common.py` sert à lire des champs, pas à réécrire arbitrairement un schéma. Une substitution globale peut casser les symboles embarqués, descriptions échappées, UUID ou instances. Préférer l'interface KiCad et ses opérations natives ; si une édition de texte est nécessaire, viser un nœud précis, contrôler les UUID et réexporter schéma, netlist et ERC.

Mettre à jour les valeurs dans le schéma et la carte. Une modification d'empreinte exige de vérifier les tables de bibliothèques et la parité ; ne pas ignorer `lib_footprint_mismatch` pour faire disparaître le symptôme.

## Limites des contrôles livrés

`controle_iut.py` ne modifie pas les sources. Il recharge les zones pour le DRC en mémoire, sans `--save-board`.

- Les objectifs de largeur viennent des classes du `.kicad_pro`, ou du profil JSON explicite. Les motifs usuels sont interprétés avec les jokers de fichiers ; des affectations KiCad plus complexes demandent confirmation dans l'interface.
- Le contrôle des angles porte sur les extrémités communes de segments droits hors pastilles et vias. Il n'inspecte pas exhaustivement les jonctions en milieu de segment, les zones ni les jonctions avec arcs.
- Les anneaux sont estimés par les dimensions X/Y ; le DRC reste nécessaire pour les formes personnalisées.
- Les straps sont contrôlés par segments F.Cu, vias du même réseau et courtyards disponibles. Vérifier visuellement les cartes sans courtyard ou avec une géométrie inhabituelle.
- Le DRC traite la fermeture du contour ; sa boîte englobante n'est pas une preuve indépendante de fermeture.
- Aucune mesure exhaustive de ligne de fuite, aucun calcul de courant admissible ni audit des composants n'est réalisé.
- Les exclusions restent visibles dans les rapports. Un échec de commande ou un rapport absent interrompt le traitement.

Pour tester une règle, créer un défaut contrôlé sur une copie isolée et exiger la violation attendue dans le rapport. Les scripts ne doivent pas modifier la carte d'origine pour leur propre validation.
