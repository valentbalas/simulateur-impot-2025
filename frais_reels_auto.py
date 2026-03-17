"""
Calculateur intelligent de frais professionnels reels.
Compare automatiquement avec le forfait 10 %.
Gere les repas sans justificatifs, les tickets restaurant, et le bareme km.
"""
from calcul_impot import FraisReels, MoteurImpot


REPAS_VALEUR_FOYER = 5.35       # Valeur du repas prepare a la maison (2024)
REPAS_MIN_EXTE     = 10.20      # Seuil minimal d'un repas pris a l'exterieur sans justificatif
REPAS_DEDUCTIBLE_SANS_JUST = REPAS_MIN_EXTE - REPAS_VALEUR_FOYER  # = 4.85 EUR par repas

TICKET_RESTO_LIMITE_PATRONALE = 0.60   # 60 % de la valeur faciale maximum exonere
TICKET_RESTO_PLAFOND_EXONERE  = 7.18   # Part patronale exoneree max en 2024 (7.18 EUR/jour)

TELETRAVAIL_JOUR = 2.70
TELETRAVAIL_MAX_MOIS = 59.40


def calculer_frais_repas(
    nb_repas_pro_an: int,
    repas_avec_justif: float = 0,
    montant_total_avec_justif: float = 0,
    tickets_resto_valeur_faciale: float = 0,
    tickets_resto_part_patronale: float = 0,
) -> dict:
    """
    Calcule les frais de repas deductibles.

    SANS justificatif :
      Deductible forfaitaire = nb_repas * 4.85 EUR
      (prix minimal exterieur 10.20 EUR - valeur foyer 5.35 EUR)

    AVEC justificatif :
      Deductible = montant total - (nb_repas * 5.35 EUR)

    TICKETS RESTAURANT :
      La part patronale exoneree ne genere pas de frais
      L'eventuelle part patronale au-dela du plafond (7.18 EUR/jour)
      doit etre reintegree dans le salaire imposable.
    """
    # Frais sans justificatifs
    deductible_sans_just = nb_repas_pro_an * REPAS_DEDUCTIBLE_SANS_JUST

    # Frais avec justificatifs
    nb_avec_just = min(repas_avec_justif, nb_repas_pro_an)
    nb_sans_just = max(0, nb_repas_pro_an - nb_avec_just)
    deductible_avec_just = max(0.0,
        montant_total_avec_justif - nb_avec_just * REPAS_VALEUR_FOYER)

    # Correction tickets restaurant
    # La part patronale exoneree (dans les limites) n'est pas un frais reel
    exoneree_tickets = min(
        tickets_resto_part_patronale,
        TICKET_RESTO_PLAFOND_EXONERE * (nb_repas_pro_an / 220 * 220)  # approx jours
    )
    # Part patronale exoneree = avantage : elle couvre une partie du repas
    # On doit donc la deduire du deductible (l'employeur paie deja cette part)
    avantage_ticket = min(exoneree_tickets, deductible_avec_just + deductible_sans_just)

    # Total frais repas
    total_repas = deductible_sans_just + deductible_avec_just - avantage_ticket

    return {
        'nb_repas_total':              nb_repas_pro_an,
        'nb_repas_sans_justif':        nb_sans_just,
        'nb_repas_avec_justif':        int(nb_avec_just),
        'deductible_sans_justif':      round(deductible_sans_just, 2),
        'deductible_avec_justif':      round(deductible_avec_just, 2),
        'avantage_ticket_resto':       round(avantage_ticket, 2),
        'total_deductible_repas':      round(max(0, total_repas), 2),
        'note_sans_just':              f"{nb_sans_just} repas x {REPAS_DEDUCTIBLE_SANS_JUST} EUR = {round(nb_sans_just*REPAS_DEDUCTIBLE_SANS_JUST,2)} EUR (sans justif)",
        'note_avec_just':              f"{int(nb_avec_just)} repas justifies : {round(montant_total_avec_justif,2)} EUR - {round(nb_avec_just*REPAS_VALEUR_FOYER,2)} EUR (foyer) = {round(deductible_avec_just,2)} EUR",
        'note_tickets':                f"Tickets resto : part patronale couvre {round(avantage_ticket,2)} EUR" if avantage_ticket > 0 else "",
    }


def calculer_frais_reels_complets(data: dict, salaire: float) -> dict:
    """
    Calcul complet et automatique des frais reels.
    Retourne le total, le detail, et la comparaison avec le forfait.
    """
    m = MoteurImpot()
    forfait = max(m.ABATTEMENT_SALAIRES_MIN, min(salaire * 0.10, m.ABATTEMENT_SALAIRES_MAX))

    # 1. Frais kilomestriques
    km      = data.get('km', 0)
    cv      = data.get('cv', 5)
    tveh    = data.get('type_vehicule', 'thermique')
    fkm     = round(FraisReels.calculer_bareme_km(km, cv, tveh), 2) if km > 0 else 0

    # 2. Frais de repas
    repas_d = calculer_frais_repas(
        nb_repas_pro_an              = data.get('nb_repas', 0),
        repas_avec_justif            = data.get('nb_repas_avec_justif', 0),
        montant_total_avec_justif    = data.get('montant_repas_justif', 0),
        tickets_resto_valeur_faciale = data.get('tickets_valeur_faciale', 0),
        tickets_resto_part_patronale = data.get('tickets_part_patronale', 0),
    )
    f_repas = repas_d['total_deductible_repas']

    # 3. Teletravail
    jours_tt = data.get('jours_teletravail', 0)
    f_tt = min(jours_tt * TELETRAVAIL_JOUR, TELETRAVAIL_MAX_MOIS * 12) if jours_tt > 0 else 0

    # 4. Autres
    double_res = data.get('double_residence', 0)
    formation  = data.get('formation', 0)
    materiel   = data.get('materiel', 0)
    syndicats  = data.get('syndicats_non_deductibles', 0)
    autres     = data.get('autres', 0)

    total_fr = round(fkm + f_repas + f_tt + double_res + formation + materiel + syndicats + autres, 2)

    # Comparaison
    gain = round(total_fr - forfait, 2)
    conseil = (
        "Frais reels plus avantageux" if gain > 0
        else "Forfait 10 % plus avantageux — conserver le forfait"
    )

    return {
        # Sous-totaux
        'frais_km':             fkm,
        'frais_repas':          f_repas,
        'frais_repas_detail':   repas_d,
        'frais_teletravail':    round(f_tt, 2),
        'double_residence':     double_res,
        'formation':            formation,
        'materiel':             materiel,
        'autres':               autres,
        # Total
        'total_frais_reels':    total_fr,
        # Comparaison
        'forfait_10pct':        round(forfait, 2),
        'gain_vs_forfait':      gain,
        'recommandation':       conseil,
        'utiliser_frais_reels': gain > 0,
        # Kilometrique
        'km':                   km,
        'cv':                   cv,
        'type_vehicule':        tveh,
    }
