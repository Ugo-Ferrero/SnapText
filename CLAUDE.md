# CLAUDE.md

Ce fichier sert à briefer Claude (Cowork ou Claude Code) sur le projet SnapText.

## C'est quoi SnapText ?

SnapText est un outil macOS qui tourne en arrière-plan et remplace automatiquement des raccourcis clavier par des textes longs. Tu tapes `/prompt` n'importe où sur le Mac → SnapText efface le raccourci et colle le texte complet via Cmd+V.

Inspiré de Text Blaze, construit en Python. C'est mon premier projet, je ne suis pas développeur — je construis des outils pour aller plus vite dans mon travail avec l'aide de l'IA.

## Fichiers du projet

- `SnapText.py` — le script principal. Écoute le clavier avec pynput, détecte les raccourcis qui commencent par `/`, efface les caractères avec Backspace, copie le texte via pbcopy et colle avec Cmd+V
- `snippets.json` — mapping `{"/raccourci": "nom_du_fichier.xml"}`
- `snippets/` — dossier contenant les fichiers texte/XML de chaque snippet
- `com.SnapText.plist` — pour lancer SnapText automatiquement au démarrage du Mac
- `requirements.txt` — dépendances Python

## Comment ça marche techniquement

- `pynput.keyboard.Listener` écoute tous les keystrokes globalement
- Un buffer (max 50 chars) accumule les touches tapées
- Le buffer se réinitialise quand on tape `/` (nouveau raccourci potentiel)
- À chaque touche, `verifier_buffer()` compare le buffer aux raccourcis connus
- Sur match : `effacer_et_coller()` envoie Backspace × len(raccourci), copie via `pbcopy` (subprocess), colle via Cmd+V
- Hot-reload : `verifier_maj_snippets()` surveille le mtime de snippets.json et recharge si modifié
- Le remplacement tourne dans un thread séparé (pynput interdit de simuler des touches depuis son propre thread)

## Lancer le projet

```bash
python3 SnapText.py
```

macOS requiert la permission Accessibilité pour le Terminal (Réglages Système → Confidentialité → Accessibilité).

## Dépendances

```bash
pip install -r requirements.txt
# pynput, pyperclip, pyobjc-framework-Cocoa
```

## Ce qu'on veut construire en V2

### Fonctionnalité : autocomplétion avec popup discrète

**Comportement attendu :**
- Quand l'utilisateur tape `/`, une petite popup discrète apparaît avec la liste de tous les snippets disponibles (affichage : juste le raccourci, ex: `/prompt`)
- Plus l'utilisateur tape de lettres après le `/`, plus la liste se filtre (ex: `/pro` → ne montre que `/prompt`)
- Si l'utilisateur appuie sur **Échap** ou tape autre chose → la popup disparaît silencieusement, sans déclencher de remplacement
- Si l'utilisateur appuie sur **Entrée** ou **clique** sur un snippet → le remplacement se déclenche
- La popup doit être **non-intrusive** : si quelqu'un tape juste `/` sans vouloir un snippet, ça ne doit pas le gêner

**Contraintes techniques :**
- On est sur macOS uniquement
- Le script tourne en arrière-plan sans interface graphique
- La popup doit s'afficher par-dessus toutes les autres fenêtres, au bon endroit
- Penser à utiliser `tkinter` ou `AppKit` (pyobjc) pour la fenêtre flottante

**Ce qu'il ne faut pas casser :**
- Le hot-reload des snippets
- Le système de remplacement existant (Backspace + pbcopy + Cmd+V)
- La détection du buffer clavier
