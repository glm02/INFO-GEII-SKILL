# Règles de fabrication de l'IUT GEII Lyon 1

Source : cours « Conception de circuits imprimés » et TP du module CAO / SAE22
(http://geii.pages.univ-lyon1.fr/cao/), KiCad 10.0.3 annoncé dans le TP1 archivé.
Ces règles concernent le procédé et le TP décrits ; elles ne certifient pas une carte secteur.

## Comment l'IUT fabrique

- Gravure **laser** de plaques cuivrées : le laser brûle le cuivre à enlever. Plus il reste de
  cuivre, plus c'est rapide → **plan de masse** demandé.
- Simple ou double face, **sans trous métallisés**, **sans vernis épargne**, **sans sérigraphie**.
- Un via se fait à la main avec du fil rigide dénudé, soudé des deux côtés.
- La sérigraphie n'est pas imprimée, mais le DRC doit être propre : pas de sérigraphie sur les pastilles.

## Dimensions

| Élément | Minimum | À viser |
|---|---|---|
| Largeur de piste | 0,25 mm (10 th) | 0,5 mm ; puissance selon le courant (10 °C d'échauffement) |
| Isolement entre conducteurs | 0,25 mm | 0,5 à 1 mm |
| Perçage | **0,8 mm** (forets plus fins trop fragiles) | 0,8 mm pour les pattes fines |
| Pastille | Anneau demandé : 0,4 mm | **2 mm** de diamètre pour 0,8 mm de trou (anneau résultant : 0,6 mm) |
| Texte cuivre | 0,8 mm de haut, trait 0,08 mm (règle KiCad) | 1,5 mm, trait 0,3 mm, gras |

### Règles de conception du TP (Configuration du CI)

Contraintes : isolement 0,5 · piste 0,6 · connexion 0,6 · anneau 0,4 · via 2 · trou/cuivre 0,4 ·
cuivre/contour 1 · trou traversant 0,7 · trou à trou 1 · texte 0,8 / 0,08 (mm).

Classes d'équipotentielles :

| Classe | Isolement | Piste | Via / trou |
|---|---|---|---|
| Default | 0,5 | 0,6 | 2 / 0,8 |
| Power | 0,5 | 0,7 | 2 / 0,8 |

Affectation : `+5V` et `GND` → Power. Images : `assets/regles_conception.png`, `assets/classes_equipots.png`.

## Simple face et straps

- Pistes sur **B.Cu** (bleu), vues par transparence depuis le dessus.
- Un **strap** est un fil sur le dessus de la carte : dans KiCad, une piste **F.Cu** (rouge) **entre
  deux vias**, jamais depuis une patte de composant (même trou).
- Strap **droit** (horizontal ou vertical), sans virage ni diagonale.
- Un via ne sert qu'à **un** strap.
- Pas de strap sous un composant ni à travers un composant. Les pistes B.Cu peuvent passer sous les composants.
- Pas de via sous un composant (la soudure dessus gêne le composant).
- Une piste peut passer **entre les deux pattes** d'une résistance axiale (pont naturel, pas de strap).
- Double face sans trous métallisés : seul un composant soudable des deux côtés (résistance) peut
  servir de via. Un condensateur ou un connecteur ne le peut pas.

## Placement et routage

- Regrouper les composants reliés entre eux, connecteurs en bord de carte, composants alignés.
- Découplage (100 nF) au plus près du circuit à découpler.
- Points de test accessibles à la sonde d'oscilloscope.
- Le cours demande d'éviter les virages à 90° et de préférer **45°**. Éviter aussi les angles aigus ; la gravure laser locale ne justifie pas de parler systématiquement de pièges à acide.
- CEM : séparer signaux sensibles et bruyants, pas de grandes boucles, chemin le plus court.
- Le connecteur PICkit / SNAP (J4) a une grande zone d'occupation qui peut déborder de la carte.

## Finition (TP6)

- Texte **NOM - G20x** sur **B.Cu et F.Silkscreen**. Sur B.Cu, le texte est **en miroir** pour se lire côté cuivre.
- Texte **+5V** et **GND** à côté des pattes du bornier d'alimentation, sur B.Cu et F.SilkS.
- **Plan de masse** (zone GND sur B.Cu), puis **teardrops** (gouttes), puis DRC sans erreur et
  aucune connexion non routée.

Sur une carte comportant le secteur, un plan GND ne doit jamais franchir la barrière d'isolement.

## Schéma (cours)

- Cartouche complet : titre, auteur (NOM Prénom), groupe, date, révision, numéro de page.
- Blocs fonctionnels séparés et titrés. Renvois (labels globaux) plutôt que de longs fils.
- Toujours un connecteur d'arrivée d'alimentation. `PWR_FLAG` sur les alimentations venant d'un connecteur.
- Préfixes : U/IC circuit intégré, R, C, L, D (diode), LED, Z (Zener), Q (transistor), J (connecteur),
  SW (interrupteur), K (relais), X/XTAL (quartz).
- Barre au-dessus d'un nom de signal : `~{MCLR}`.
- Bornier : vérifier que le numéro des pattes suit le schéma (miroir vertical si besoin).
- ERC sans erreur avant de passer au PCB.

## Nommage du projet

`G20x_Nom_TP_CAO` (numéro de groupe, nom de famille sans espace, accent ni tiret), dans `W:\CAO_IUT`.
Bibliothèques personnelles : `G20x_Nom_symboles` (symboles), `G20x_Nom_empreintes.pretty` (empreintes).
Bibliothèques de l'IUT : `IUT_CAO_symboles.kicad_sym` et `IUT_CAO_empreintes.pretty`, fournies dans `assets/`.

Le nom personnel demandé pour la remise scolaire reste local ; ne pas le publier automatiquement dans un dépôt ou un livrable public.
