import re


def est_lettres_seulement(valeur):
    return all(c.isalpha() or c.isspace() or c in "-'éèêëàâäùûüôöîïçÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ" for c in valeur)


def est_chiffres_seulement(valeur):
    if not valeur:
        return True
    return valeur.isdigit()


def est_nombre(valeur):
    if not valeur:
        return False
    try:
        float(valeur)
        return True
    except ValueError:
        return False


def est_float_possible(valeur):
    if valeur == "" or valeur == "-" or valeur == ".":
        return True
    if valeur.startswith("-") and valeur.count("-") == 1:
        valeur = valeur[1:]
    if valeur.count(".") > 1:
        return False
    return all(c.isdigit() or c == "." for c in valeur)


def est_email_valide(email):
    if not email:
        return True
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def valider_champ_texte(valeur, nom_champ, obligatoire=True):
    if obligatoire and not valeur.strip():
        return f"Le champ '{nom_champ}' est obligatoire"
    if valeur.strip() and not est_lettres_seulement(valeur.strip()):
        return f"Le champ '{nom_champ}' ne doit contenir que des lettres"
    return None


def valider_champ_telephone(valeur, nom_champ="Téléphone", obligatoire=False):
    if not valeur.strip() and obligatoire:
        return f"Le champ '{nom_champ}' est obligatoire"
    if valeur.strip() and not est_chiffres_seulement(valeur.strip()):
        return f"Le champ '{nom_champ}' ne doit contenir que des chiffres"
    return None


def valider_champ_montant(valeur, nom_champ="Montant"):
    if not valeur.strip():
        return f"Le champ '{nom_champ}' est obligatoire"
    if not est_nombre(valeur.strip()):
        return f"Le champ '{nom_champ}' doit être un nombre valide"
    if float(valeur) < 0:
        return f"Le champ '{nom_champ}' ne peut pas être négatif"
    return None


def valider_champ_coordonnee(valeur, nom_champ):
    if not valeur.strip():
        return f"Le champ '{nom_champ}' est obligatoire"
    if not est_nombre(valeur.strip()):
        return f"Le champ '{nom_champ}' doit être un nombre valide"
    return None


def valider_champ_heure(valeur):
    if not valeur.strip():
        return "L'heure prévue est obligatoire"
    for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]:
        try:
            from datetime import datetime
            datetime.strptime(valeur.strip(), fmt)
            return None
        except ValueError:
            continue
    return "Format d'heure invalide (attendu : AAAA-MM-JJ HH:MM)"
