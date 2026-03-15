# SnapText ✍️

Tu tapes les mêmes choses 100 fois par jour ? Moi aussi. C'est pour ça que j'ai construit SnapText.
Tu définis un raccourci, genre `/prompt`, et dès que tu le tapes — peu importe où, dans Chrome, Notion, Word, n'importe quoi — SnapText l'efface et colle le texte complet à la place. Automatiquement, en moins d'une seconde.

C'est mon premier projet Python. Je l'ai construit pour apprendre, et parce que j'en avais besoin tous les jours.

---

## Comment ça marche concrètement ?

Tu tapes `/prompt` au clavier → SnapText détecte le raccourci → efface les 7 caractères → colle ton texte via Cmd+V. C'est tout.

Le script tourne en arrière-plan et écoute ton clavier en permanence. Il ne s'active que quand tu tapes quelque chose qui commence par `/`, donc il est discret et ne consomme pas de ressources inutilement.

---

## Ce que SnapText sait faire

- **Remplacer un raccourci par un texte long** — la fonction principale, et elle marche bien
- **Hot-reload** — tu modifies tes snippets, SnapText les recharge tout seul sans que tu aies besoin de redémarrer quoi que ce soit
- **Lancement automatique au démarrage** — une fois configuré, tu n'y penses plus

---

## Installer SnapText

Tu auras besoin de macOS et Python 3.

```bash
# Clone le projet
git clone https://github.com/Ugo-Ferrero/SnapText.git
cd SnapText

# Installe les dépendances
pip install pynput pyperclip pyobjc-framework-Cocoa

# Lance le script
python3 SnapText.py
```

> La première fois, macOS va te demander une autorisation d'accessibilité pour que SnapText puisse lire le clavier. Va dans **Réglages Système → Confidentialité → Accessibilité** et autorise le Terminal. C'est obligatoire pour que ça fonctionne.

---

## Ajouter tes propres snippets

C'est simple. Deux étapes :

**1. Crée un fichier** dans le dossier `snippets/` avec ton texte à l'intérieur.

**2. Ajoute une ligne dans `snippets.json`** :
```json
{
  "/prompt": "prompt.xml",
  "/monraccourci": "mon_fichier.txt"
}
```

Sauvegarde, et c'est immédiatement actif. Pas besoin de redémarrer.

---

## Lancer SnapText automatiquement au démarrage du Mac

```bash
cp com.SnapText.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.SnapText.plist
```

---

## Ce que j'aimerais ajouter un jour

- Une petite interface pour gérer les snippets sans ouvrir le JSON à la main
- Des variables dynamiques comme la date ou l'heure dans les snippets
- Pourquoi pas un support Windows/Linux

---

## Le projet en détail

```
SnapText/
├── SnapText.py          # Le cœur du projet — écoute le clavier, détecte les raccourcis, gère les remplacements
├── snippets.json        # La liste des raccourcis et leurs fichiers associés
├── snippets/            # Les textes longs, un fichier par snippet
├── com.SnapText.plist   # Pour le lancement automatique au démarrage
└── CLAUDE.md            # Mes notes de dev (j'utilise Claude Code pour m'aider à coder)
```

---

Construit par **Ugo Ferrero** — en apprenant, étape par étape.
