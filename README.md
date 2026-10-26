# Skill `c-pic-iut-geii` — le C pour PIC comme en cours de GEII

Une **skill** pour agent IA (Claude, Codex…) : écrire, corriger ou expliquer du code
C pour microcontrôleur PIC (MPLAB X / XC8) **comme le demandent les enseignants du
département GEII de l'IUT Lyon 1**, dans les modules INFO2, INFO3 et les SAÉ.

Le problème qu'elle règle : une IA laissée seule écrit du C « de forum », avec des
notions jamais vues en cours, qu'un étudiant ne sait pas expliquer ligne par ligne
devant l'enseignant. Avec cette skill, elle reste dans le programme et **guide plutôt
que de donner la solution**.

## Ce que fait la skill

- **Identifie le contexte avant de coder** : quelle carte, quel module, quel PIC.

  | Module | PIC | Style attendu |
  |---|---|---|
  | INFO2 (S2) | PIC16F1789 | Registres écrits directement (`TRISA0`, `PR2`, `T2CON`…) |
  | INFO3 (S3) | PIC16F18875 | Fonctions générées par MCC (`LED_D2_SetHigh()`, `TMR2_SetInterruptHandler()`…) |
  | SAÉ 22 / projets | PIC16F1788 | Squelette du sujet (`libsae22.h`) + registres directs |

- **N'utilise que les notions vues en cours** : E/S, masques, Timer0/Timer2,
  interruptions, EUSART, SPI, PWM, CAN, LCD. Ce qui est hors programme est remplacé
  par son équivalent vu en cours.
- **Reprend les squelettes de programme** des sujets de TP de chaque module.
- **Applique les règles que les enseignants vérifient** : plus petit type possible,
  drapeaux remis à zéro tôt, interruptions courtes, variables partagées `volatile`
  avec section critique, lectures et écritures multi-bits par masques.
- **Mode pédagogique par défaut** : indices, questions, squelettes `// à compléter`.
  La solution complète seulement si on la demande explicitement.
- **Checklist avant de rendre du code**, et renvoi à la datasheet du fabricant en cas de doute.

## Exemples de demandes

- « Fais clignoter la LED D2 toutes les 500 ms avec le Timer2, en INFO3 (MCC). »
- « Mon interruption sur RB0 ne se déclenche pas, voici mon code. »
- « Explique-moi comment lire le potentiomètre avec le CAN sur la carte de la SAÉ. »

## Installer

```bash
git clone https://github.com/glm02/INFO-GEII-SKILL.git

# Claude Code
cp -r INFO-GEII-SKILL/c-pic-iut-geii ~/.claude/skills/

# Codex
cp -r INFO-GEII-SKILL/c-pic-iut-geii ~/.agents/skills/
```

Pour l'application Claude (claude.ai) : compresser le dossier `c-pic-iut-geii` en zip
et l'importer dans les paramètres, rubrique Skills.
Tuto illustré : [rafaelgmille.site/stack#installer](https://www.rafaelgmille.site/stack#installer).

## Limites

La skill est écrite à partir des cours et des sujets de TP ; elle ne remplace ni la
datasheet du PIC ni l'avis de l'enseignant. Elle sert à apprendre : rendre du code
qu'on ne sait pas expliquer reste une mauvaise idée.

---

Rafael — étudiant en 2e année de BUT GEII · [portfolio](https://www.rafaelgmille.site) ·
mes autres skills : [skills-claude-code](https://github.com/glm02/skills-claude-code)
