# TP CAO (SAE22) : déroulé et vidéos

Carte support : PIC16F1788 (DIP28), 2 boutons, 2 interrupteurs, 4 LED, liaison série, LCD 2x16
(162B), connecteur PICkit/SNAP. Carte 9 x 8 cm, simple face. Schéma : `assets/Carte_PIC_CAO.pdf`.
Placement imposé : `assets/PlacementComposants.png` (origine relative au coin haut droit :
pastille 1 du LCD en (-38 ; 10), pastille 1 de J1 en (-5 ; 25)). Pas de trous de fixation.

Chaque étape renvoie à sa vidéo ; la transcription, quand elle existe, est dans
`transcriptions/<id>.md`. Index des vidéos : [videos.md](videos.md).

## TP1 Introduction

1. Projet `G20x_Nom_TP_CAO` dans `W:\CAO_IUT` — vidéo `Q0n2wbpyJLw`.
2. Décompresser les bibliothèques de l'IUT dans le dossier du projet (`assets/` du skill).
3. Ajouter `IUT_CAO_symboles` à la table des symboles **du projet** — vidéo `AyB4f1mrR5Q`.
   Au premier lancement de KiCad : copier la table globale par défaut (option recommandée).
4. Créer la bibliothèque `G20x_Nom_symboles` — vidéo `p79w6GWcTMo`.

## TP2 Saisie du schéma

1. Cartouche : date du jour, rév. 1.0, titre « SAE22 : Carte commande moteurs robot », société
   « IUT LYON 1 - GEII », commentaire 1 « NOM Prenom », commentaire 2 « G20x » — vidéo `qSjW3b9668Q`.
2. Saisie (vidéo d'Éric Peronnin `Aj7RpaX0Y7o`, de 6 min 50 à 28 min, sauter 16 min 18 → 20 min 20) :
   - alimentations et `PWR_FLAG` (outil Power), labels globaux (forme et point de connexion dans les propriétés) ;
   - croix « non connecté » sur les pattes libres ; lignes bleues = polylignes graphiques (pas des fils ni des bus).
3. Symboles :

| Repères | Bibliothèque | Symbole |
|---|---|---|
| C1 | Device | C_Polarized_Small |
| C2–C5 | Device | C |
| D1–D4 | Device | LED |
| DS1 | G20x_Nom_symboles | 162B-CC-BC-3LP (à créer) |
| J1 | Connector | Screw_Terminal_01x02 |
| J2, J3 | Connector_Generic | Conn_01x06 |
| J4 | Connector | Conn_PIC_ICSP_ICD |
| R1–R14 | Device | R |
| RV1 | Device | R_Potentiometer |
| SW1, SW2, SW4 | Switch | SW_Push |
| SW3 | Switch | SW_DIP_x02 |
| U1 | IUT_CAO_symboles | PIC16F1788-xSP |
| TP1–TP6 | Connector | TestPoint |

4. Créer un symbole : exemple du PIC16F1788 — vidéo `41ZLt-VEniQ` (recherche 0:34, filtre 1:00,
   alias 2:59, copie en bibliothèque perso 3:30, propriétés 4:03, suppression des alias 5:10,
   types de pattes 6:00, édition des pattes 7:01, rectangle 8:42, vérification 10:06).
5. Symbole du LCD 162B à partir du HY1602E — vidéo `63cvwbsB4Cc`. Différence : rétroéclairage sur
   les pattes 1 et 2. Filtre d'empreinte `*162B*`, référence DS, valeur et nom `162B-CC-BC-3LP`,
   empreinte `IUT_CAO_empreintes:162B`.
6. Annotation : à la main (touche e) pour garder les repères du schéma de référence.
7. Vérifier : pattes 1-2 du LCD, LCD_D7 → RA6 et LCD_D6 → RA7, numéros du bornier, sens des
   labels (entrée, sortie, bidirectionnel). Puis ERC sans erreur.

## TP3 Empreintes

1. Bibliothèque `G20x_Nom_empreintes.pretty` — vidéo `0lUDxkM02b8`.
2. Modifier une empreinte existante : exemple de la LED — vidéo `7t7NjbGzVW4`.
3. Résistance 1/4 W carbone (corps 6,8 mm) : partir de
   `R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal`, pastilles **2 mm**, perçage 0,8 mm,
   raccourcir la sérigraphie des pattes (grille fine). Le pas entre pastilles est le critère clé.
4. Créer une empreinte de zéro : bornier 3 points — vidéo `ne_GFI0vpOk` (nommage 1:41, pastilles
   5:06, édition des pastilles 6:43, sérigraphie F.SilkS 10:44, sauvegarde 14:00, courtyard F.CrtYd
   14:36, couche F.Fab 16:38, couches 17:49, propriétés 18:58). Sur F.Fab, la référence s'écrit
   `${REFERENCE}` : ne pas la modifier.
5. Bornier 2 points `Bornier_1x02_L10mm_W7.5mm_P5mm` (doc KRM02).

## TP4 Association des empreintes

- Éditeur de champs des symboles (une empreinte pour plusieurs composants) — vidéo `WbTXC78V_tc`.
- Outil « Assigner les empreintes » (filtres des symboles) — vidéo `ffEXPfvdr5o`.
- Empreintes de la carte PIC : C1 `CP_Radial_D6.3mm_P2.50mm`, C2–C5 `C_Disc_D4.7mm_W2.5mm_P5.00mm`,
  LED `LED_D5.0mm`, DS1 `162B`, J1 bornier perso, J2 `PinHeader_1x06_P2.54mm_Vertical`,
  J3 `Molex_KK-254_AE-6410-06A_1x06_P2.54mm_Vertical`, J4 `PicKit_4_Snap_1x08_P2.54mm_Vertical`,
  résistances DIN0207 perso, RV1 `Potentiometer_Bourns_3306F_Vertical`,
  SW `SW_TH_Tactile_Omron_B3F-10xx`, SW3 `SW_DIP_SPSTx02_Slide_7.5x7.01mm_W7.62mm_P2.54mm_LowProfile`,
  TP `TestPoint_Loop_D2.50mm_Drill1.0mm` (tout dans `IUT_CAO_empreintes`), U1
  `Package_DIP:DIP-28_W7.62mm_Socket_LongPads`.
- Valeurs : C1 47u, C2–C5 100n, D1-D2 « LED R », D3-D4 « LED V », R1-R4/R12 10k, R5/R6/R11 56k,
  R7-R10/R14 270, R13 1.5k, RV1 10k, SW B3F-1000.

## TP5 Placement et routage

1. Importer le schéma dans le PCB (icône « mettre à jour le PCB depuis le schéma ») — vidéo
   `b9YZTuc07bk`. 8 avertissements attendus (pastilles sans patte de symbole) : normal.
2. Contour sur Edge.Cuts, dans le cartouche, rectangle 9 x 8 cm — vidéo `tNCylnmHwfo`.
3. Règles de conception ([regles-iut.md](regles-iut.md)) — vidéo `16VS6WO6exY` (couches 0:00,
   règles 3:50).
4. Placement — vidéo `0uf_CUoXeUo` (recherche et rotation 0:00, sélection et alignement 3:22,
   coordonnées 5:52, courtyard du PICkit 8:02). Astuce : sélectionner un groupe dans le schéma,
   passer au PCB, touche P.
5. Routage — vidéo `pybFDs3VGEo` (piste 0:00, routeur interactif 1:47, sélection 2:51, tout effacer
   3:41, strap à 2 vias 4:35, affichage 5:34, surbrillance d'un nœud 7:14, déplacer une piste 7:58,
   déplacer un composant 8:22, pistes non routées 8:36).
6. DRC sans erreur, sérigraphie comprise.

## TP6 Finalisation

1. Textes NOM - G20x, +5V et GND (B.Cu en miroir + F.SilkS) — vidéo `7IovMUk7RWo`.
2. Plan de masse — vidéo `PlhdJviFyr0`.
3. Teardrops — vidéo `9KMaULURQUY`.
4. DRC sans erreur, aucune connexion non routée.
5. Gerber et perçage — vidéo `3R4WV4Kqol4`. Dossier de fabrication : `scripts/dossier_iut.py`.
6. Archiver le projet et le remettre à l'enseignant.

## Dossier de fabrication (format du prof)

Exemple : `assets/DOSSIER DE FABRICATION.pdf`. Page de garde (SAE22 - CAO, GROUPE NOM), sommaire,
puis 1. Schéma (PDF), 2. Couche de fabrication F.Fab + Edge.Cuts et vue 3D (rendu lancer de rayons),
3. Straps (F.Cu + Edge.Cuts), 4. BOM (Reference, Value ; CSV importé dans Excel).
