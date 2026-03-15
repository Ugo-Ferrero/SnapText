import os
import json
import time
import threading
import subprocess
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller

try:
    from AppKit import NSPasteboard, NSPasteboardTypeString
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False

# ──────────────────────────────────────────────
# Chemins absolus
# ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────
# Chargement des snippets depuis snippets.json
# ──────────────────────────────────────────────
def charger_snippets(chemin_json=os.path.join(SCRIPT_DIR, "snippets.json"), dossier_snippets=os.path.join(SCRIPT_DIR, "snippets")):
    """
    Lit le fichier JSON contenant le mapping {raccourci: nom_fichier},
    puis charge le contenu de chaque fichier depuis le dossier spécifié.
    Retourne un dictionnaire {raccourci: texte_complet}.
    """
    try:
        with open(chemin_json, "r", encoding="utf-8") as f:
            mapping = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {chemin_json} : {e}")
        return {}

    snippets_charges = {}
    
    # Pour chaque raccourci, on lit le fichier correspondant dans le dossier "snippets"
    for raccourci, nom_fichier in mapping.items():
        chemin_fichier = os.path.join(dossier_snippets, nom_fichier)
        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                # Le contenu du fichier devient le texte à coller
                snippets_charges[raccourci] = f.read()
        except Exception as e:
            print(f"⚠️ Impossible de charger le fichier '{nom_fichier}' pour le raccourci '{raccourci}' : {e}")

    return snippets_charges

snippets = charger_snippets()
chemin_json_global = os.path.join(SCRIPT_DIR, "snippets.json")
derniere_maj_json = os.path.getmtime(chemin_json_global) if os.path.exists(chemin_json_global) else 0
print(f"✅ Snippets chargés ({len(snippets)} trouvés) :", list(snippets.keys()))

def verifier_maj_snippets():
    """Vérifie si le fichier snippets.json a été modifié et le recharge si nécessaire."""
    global snippets, derniere_maj_json
    try:
        if os.path.exists(chemin_json_global):
            mtime = os.path.getmtime(chemin_json_global)
            if mtime > derniere_maj_json:
                print("\n🔄 Modification détectée dans snippets.json. Rechargement...")
                nouveaux_snippets = charger_snippets()
                snippets = nouveaux_snippets
                derniere_maj_json = mtime
                print(f"✅ Snippets rechargés :", list(snippets.keys()))
                
                # Réafficher le prompt vu qu'on a écrit au milieu du terminal
                print("\n🚀 Mon Text Blaze est actif. Tapez un raccourci pour le remplacer.")
                print("   (Ctrl+C dans ce terminal pour arrêter)\n")
    except Exception as e:
        pass  # Eviter de planter le script si le fichier est en cours de sauvegarde

# ──────────────────────────────────────────────
# Contrôleur clavier (pour simuler des frappes)
# ──────────────────────────────────────────────
controleur = Controller()

# Buffer qui garde en mémoire les dernières touches tapées
buffer = []

# Longueur maximale du buffer
LONGUEUR_MAX_BUFFER = 50

# Flag pour ignorer les événements clavier pendant qu'on simule des touches
en_cours_de_remplacement = False


def effacer_et_coller(raccourci, texte):
    """
    Exécuté dans un thread séparé pour éviter le conflit avec pynput.
    Efface le raccourci avec des Backspace, puis colle le texte via le presse-papier.
    """
    global en_cours_de_remplacement
    try:
        en_cours_de_remplacement = True

        # Petite pause réduite à 0.02s pour laisser l'écouteur relâcher la touche en cours
        time.sleep(0.02)

        print(f"  ↩️  Effacement de '{raccourci}' ({len(raccourci)} caractères)...")

        # Sur Mac, Shift+Home ne sélectionne pas le texte vers la gauche.
        # Le plus sûr et universel est d'appuyer sur Backspace autant de fois qu'il y a de caractères.
        for _ in range(len(raccourci)):
            controleur.press(Key.backspace)
            controleur.release(Key.backspace)
            # Un micro délai pour ne pas saturer le système
            time.sleep(0.01)

        # Copier le texte dans le presse-papier
        print(f"  📋 Copie dans le presse-papier ({len(texte)} caractères)...")
        
        # "Utilise subprocess avec pbcopy directement au lieu de pyperclip" (très rapide sur Mac)
        try:
            subprocess.run(['pbcopy'], input=texte.encode('utf-8'), check=True)
            print("  ✅ pbcopy (subprocess) OK")
        except Exception as e:
            print(f"  ❌ Erreur pbcopy : {e}")

        # Délai post-copie augmenté pour laisser à macOS le temps de synchroniser le presse-papier
        time.sleep(0.05)

        # Coller avec Cmd+V ("Réduis tous les délais (time.sleep) au minimum viable — teste avec 0.02 secondes")
        print("  ⌨️  Envoi Cmd+V...")
        controleur.press(Key.cmd)
        time.sleep(0.02)
        controleur.press('v')
        time.sleep(0.02)
        controleur.release('v')
        time.sleep(0.02)
        controleur.release(Key.cmd)
        print("  ✅ Remplacement terminé !")

    except Exception as e:
        print(f"  ❌ ERREUR dans effacer_et_coller : {e}")
    finally:
        # "Réduis tous les délais" - réactivation rapide du listener
        time.sleep(0.02)
        en_cours_de_remplacement = False


def declencher_remplacement(raccourci, texte):
    """
    Lance l'effacement et la saisie dans un thread séparé.
    IMPORTANT : pynput interdit de simuler des touches depuis son propre thread,
    donc on délègue à un thread indépendant.
    """
    t = threading.Thread(target=effacer_et_coller, args=(raccourci, texte), daemon=True)
    t.start()


def verifier_buffer():
    """
    Vérifie si le buffer correspond exactement à un raccourci connu.
    Si oui, vide le buffer et déclenche le remplacement.
    """
    texte_buffer = "".join(buffer)

    for raccourci, texte_remplacement in snippets.items():
        if texte_buffer == raccourci:
            print(f"\n🔥 Raccourci détecté : '{raccourci}'")
            buffer.clear()
            declencher_remplacement(raccourci, texte_remplacement)
            return


# ──────────────────────────────────────────────
# Gestionnaire d'événements clavier
# ──────────────────────────────────────────────
def on_press(key):
    """Appelé à chaque fois qu'une touche est pressée."""
    # Ignorer toutes les touches pendant qu'on simule le remplacement
    if en_cours_de_remplacement:
        return

    # Vérifier si on a ajouté/modifié des snippets (hot-reload transparent)
    verifier_maj_snippets()

    try:
        # Touche normale : lettre, chiffre, symbole (y compris '/')
        caractere = key.char
        if caractere is not None:
            if caractere == '/':
                # Nouveau démarrage de raccourci, on réinitialise le buffer
                buffer.clear()
                buffer.append('/')
            elif buffer and buffer[0] == '/':
                # On est déjà en train de taper un raccourci
                buffer.append(caractere)
            else:
                # Si on ne commence pas un raccourci, on ignore la touche (ne trace rien)
                return

            print(f"  Touche : '{caractere}' | Buffer : {''.join(buffer)}")
            # Limiter la taille du buffer par sécurité
            if len(buffer) > LONGUEUR_MAX_BUFFER:
                buffer.pop(0)
            verifier_buffer()

    except AttributeError:
        # Touche spéciale
        if not buffer:
            return  # Inutile de traiter si on ne tape pas un raccourci

        if key == Key.space:
            # L'espace interrompt le raccourci (pas d'espace dans les commandes)
            verifier_buffer()
            buffer.clear()
            print("  [ESPACE] | Buffer réinitialisé")
        elif key == Key.backspace:
            if buffer:
                buffer.pop()
            print(f"  [BACKSPACE] | Buffer : {''.join(buffer)}")
        elif key == Key.enter:
            # L'entrée valide ou annule
            verifier_buffer()
            buffer.clear()
            print("  [ENTRÉE] | Buffer réinitialisé")
        else:
            # Cmd, Ctrl, Option, Fn, flèches... → on vide le buffer pour arrêter l'écoute
            buffer.clear()
            print(f"  [TOUCHE SPÉCIALE: {key}] | Buffer réinitialisé")


# ──────────────────────────────────────────────
# Lancement de l'écoute clavier
# ──────────────────────────────────────────────
print("\n🚀 Mon Text Blaze est actif. Tapez un raccourci pour le remplacer.")
print("   Raccourcis disponibles :", list(snippets.keys()))
print("   (Ctrl+C dans ce terminal pour arrêter)\n")

with keyboard.Listener(on_press=on_press) as ecouteur:
    ecouteur.join()
