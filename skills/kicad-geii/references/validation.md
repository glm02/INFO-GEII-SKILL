# Validation locale des outils

Vérification du 16 novembre 2026, sous Windows : KiCad 10.0.6 et son Python 3.11 pour `pcbnew` ; Python usuel 3.13, PyMuPDF 1.28.2, Gerbonara 1.6.3 et resvg-py 0.5.0 pour les exports.

Les essais utilisent une copie temporaire du projet vide-cave. Les sources du projet courant sont comparées octet par octet à la copie initiale après les essais ; elles restent identiques.

| Essai | Résultat |
|---|---|
| Contrôle de la copie initiale | ERC et DRC : 0 erreur, 0 avertissement, 0 exclusion |
| Rapport pédagogique | Signale notamment les angles à examiner, l'absence de plan GND et la limite de l'anneau U3 ; ne les présente pas comme validés par le DRC |
| Génération complète | Schéma, BOM, couches, rendu 3D, Gerbers, perçages, ZIP et PDF de 7 pages produits |
| Lecture Gerber indépendante | 50 flashes cuivre, 50 perçages, 4 segments de contour ; macros de pastilles arrondies interprétées |
| Inspection visuelle | Toutes les pages du PDF rendues ; aperçu Gerber inspecté |
| Copie avec piste de 0,2 mm et vias percés à 0,6 mm | DRC en défaut ; largeur et perçages signalés ; retour du contrôle : 1 |
| Strap volontairement diagonal | Détecté par le contrôle pédagogique |
| Profil explicite 1 mm / 2 mm | Les trois départs de triac à 1 mm sont signalés ; aucune exception silencieuse |
| Export de la copie en défaut | Interrompu avant création des Gerbers et du dossier PDF ; retour : 2 |
| Export vers une sortie déjà remplie | Refusé, archive ZIP précédente inchangée |
| Règle secteur d'exemple sur une copie avec défaut imposé | Syntaxe acceptée ; violations attribuées explicitement à cette règle |
| Structure du skill | Validateur `quick_validate.py` et liens locaux vérifiés |
| Archive des sources | Empreintes SHA-256 vérifiées |

Gerbonara émet un avertissement de syntaxe sur la position de `G90` dans l'Excellon généré par cette version de KiCad. Les coordonnées et les 50 perçages sont bien lus. Cet essai ne valide pas tous les dialectes Gerber possibles : l'outil cible les fichiers de cuivre, contour et perçage du profil IUT et refuse les couches non reconnues.

Cette validation concerne les outils et les fichiers d'essai. Elle ne constitue pas une qualification électrique ou réglementaire de la carte vide-cave et ne remplace pas une vérification du courant moteur, des composants et de l'isolation applicable.
