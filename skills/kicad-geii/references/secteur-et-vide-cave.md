# Secteur, optocoupleurs et retour d'expérience vide-cave

Cette référence contient des points de revue et un exemple de projet, pas une certification ni un schéma universel. Les valeurs du vide-cave ne sont pas des consignes générales du cours.

## Déterminer les domaines électriques

Suivre tous les chemins conducteurs, y compris les résistances, diodes, condensateurs, blindages, interfaces de programmation et alimentations. Le nom GND n'indique pas à lui seul une masse isolée. Un neutre secteur n'est pas une masse 5 V accessible.

Classer aussi les réseaux intermédiaires : LED d'optocoupleur côté entrée secteur, gâchette triac, résistances de commande, conducteurs du capteur de courant. Une détection fondée uniquement sur les noms AC_L et AC_N les manquerait.

Les distances dépendent notamment de la norme applicable, du type d'isolation, de la tension de travail et des surtensions, de l'altitude, de la pollution et du matériau. Vérifier distances dans l'air et lignes de fuite séparément. Ni 3 mm ni un DRC à zéro ne suffisent à déclarer une isolation de sécurité conforme. Le vernis épargne standard n'est pas à considérer comme une isolation de sécurité ; l'IUT n'en dépose pas.

Le fichier `assets/regles_secteur.kicad_dru` est un exemple de séparation de 3 mm pour une classe Secteur. L'adapter aux exigences établies, l'intégrer au fichier de règles existant sans l'écraser, vérifier tous les membres de classe et les priorités des autres règles. Il ne remplace ni le calcul des distances ni l'examen du boîtier et du montage.

## Erreur rencontrée sur le 6N136

Sur le vide-cave, l'entrée LED de U1 recevait le secteur à travers les résistances, mais sa cathode retournait vers GND basse tension. Cela créait un chemin conducteur entre les deux domaines et supprimait l'isolement prévu. Le retour devait appartenir au même domaine secteur que l'entrée, avec une protection de la LED contre la tension inverse adaptée à ce montage.

Vérifier le brochage du modèle exact dans la fiche fabricant avant de câbler : anode, cathode, alimentation de sortie, sortie, broche de base éventuelle et broches non utilisées. Une diode antiparallèle protège la LED en inverse dans un montage d'entrée alternatif approprié ; elle ne résout pas le dimensionnement des résistances ni les autres protections secteur.

La sortie doit rejoindre le PIC par un connecteur physique et un retour compatible. Pour le vide-cave corrigé dans la session historique : signal RB4 sur J6.1, retour GND sur J6.2. Recontrôler les fichiers actuels avant d'utiliser ces repères.

## Vérifier les calculs plutôt que recopier les valeurs

Pour une chaîne de deux résistances égales sur 230 V efficaces :

```
R_total = R1 + R2
I_crête ≈ (sqrt(2) × U_eff - V_LED) / R_total
P_R ≈ U_eff² × R / R_total²
```

L'estimation de puissance suppose une conduction comparable sur les deux alternances, par LED puis diode de protection. Vérifier la tension secteur maximale, les tolérances et le courant réellement requis par le détecteur.

Deux résistances de 47 kΩ donnent environ 0,28 W chacune à 230 V et environ 3,4 mA crête avec une LED autour de 1,5 V. Ces chiffres ne valident pas le transfert optique : confronter le courant au CTR minimal garanti, à sa plage de caractérisation, à la température, à la résistance de rappel et aux seuils d'entrée du PIC. Vérifier également puissance déclassée, tenue en tension et dimensions de chaque résistance. « DIN0207 » ne garantit aucune puissance de 1 W.

Une sortie avec 22 kΩ et 1 nF donne une constante RC nominale de 22 µs. Vérifier alimentation, seuils, temps de propagation, largeur des impulsions et méthode logicielle de détection du zéro. Une détection par LED simple peut distinguer les alternances ; ne pas supposer deux impulsions identiques par période.

## Objectifs de routage du vide-cave

- Demande du projet : pistes basse tension ≥ 1 mm, pistes secteur visées à 2 mm, davantage si le courant l'impose.
- Les branches de détection transportant quelques mA ne se dimensionnent pas comme l'alimentation du moteur, même si elles sont au potentiel secteur.
- Le pas des broches du triac peut empêcher une largeur uniforme de 2 mm. Déplacer, réorienter ou changer de boîtier si nécessaire ; sinon documenter longueur, largeur et raison du rétrécissement.
- Ne pas réduire une séparation secteur/basse tension pour satisfaire une préférence de largeur.
- Le courant de démarrage de la pompe, le triac exact, son refroidissement, les protections et le câblage extérieur demandent leurs propres vérifications.

Les connexions modifiées aux borniers doivent être annoncées clairement, sur le schéma et sur la carte. Ne pas prétendre que les Gerbers sont prêts à alimenter sans avoir validé l'ensemble des points de sécurité applicables.
